{
  description = "A basic flake using pyproject.toml project metadata";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    { nixpkgs, pyproject-nix, ... }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs nixpkgs.lib.systems.flakeExposed;
      pkgsBySystem = forAllSystems (
        system:
        import nixpkgs {
          inherit system;
        }
      );

      project = pyproject-nix.lib.project.loadPyproject {
        projectRoot = ./.;
      };
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = pkgsBySystem.${system};

          python = pkgs.python3;
          attrs = project.renderers.buildPythonPackage { inherit python; };
          scriptName = "bilirq";
          package = python.pkgs.buildPythonPackage (attrs // { meta.mainProgram = scriptName; });
        in
        {
          default = package;
          docker-image =
            let
              browsers = pkgs.playwright-driver.browsers.override {
                withChromium = false;
                withFirefox = true;
                withWebkit = false; # may require `export PLAYWRIGHT_HOST_PLATFORM_OVERRIDE="ubuntu-24.04"`
                withFfmpeg = false;
                withChromiumHeadlessShell = false;
              };
              packageWrapper =
                pkgs.runCommand "${attrs.pname}-wrapper"
                  {
                    nativeBuildInputs = [ pkgs.makeWrapper ];
                    meta.mainProgram = scriptName;
                  }
                  ''
                    mkdir -p $out/tmp
                    makeWrapper "${lib.getExe package}" "$out/bin/${scriptName}" \
                        --set-default PLAYWRIGHT_BROWSERS_PATH "${browsers}" \
                        --set-default DOCKER "true" \
                        --set-default API_HOST "0.0.0.0"
                  '';
            in
            pkgs.dockerTools.buildLayeredImage {
              name = attrs.pname;
              tag = "latest";
              layeringPipeline = [
                [
                  "subcomponent_out"
                  [
                    browsers
                    python
                  ]
                ]
                [
                  "over"
                  "rest"
                  [
                    "pipe"
                    [
                      [ "popularity_contest" ]
                      [
                        "limit_layers"
                        72
                      ]
                    ]
                  ]
                ]
              ];
              contents = (
                [ packageWrapper ]
                ++ (with pkgs; [
                  bashInteractive
                  coreutils
                  curl
                  tini
                ])
              );
              config = {
                Entrypoint = [
                  "/bin/tini"
                  "--"
                ];
                Cmd = [ "/bin/${scriptName}" ];
                ExposedPorts = {
                  "40432" = { };
                };
                Env = [
                  "TZ=Asia/Shanghai"
                ];
              };
            };
        }
      );
    };
}
