import asyncio
import os
import re
import sys
from pathlib import Path

from loguru import logger
from playwright._impl._driver import compute_driver_executable, get_driver_env


def log(level: str, rich_text: str) -> None:
    getattr(logger.opt(colors=True), level)(
        rich_text.replace("[", "<").replace("]", ">"),
        alt=rich_text,
    )


class Progress:
    def __init__(self, name: str) -> None:
        self.last_updated: float = 0
        self.progress: float = 0.0
        self.name = name

    def update(self, *, target: float):
        import time

        if self.progress >= 100:
            return
        if (
            time.time() - self.last_updated >= 1
            or (target - self.progress >= 10 and time.time() - self.last_updated >= 0.1)
            or target == 100
        ):
            self.progress = target
            log(
                "info",
                f"[cyan]{self.name}[/] [green]{'-' * int(self.progress / 5):<20}[/] [magenta]{int(self.progress)}%[/]",
            )
            self.last_updated = time.time()


async def install_browser(
    download_host: str | None = None,
    browser_type: str = "firefox",
):
    env = get_driver_env()
    if download_host:
        env["PLAYWRIGHT_DOWNLOAD_HOST"] = download_host

    cde_raw = compute_driver_executable()
    cde = [cde_raw.as_posix()] if isinstance(cde_raw, Path) else list(cde_raw)

    command = [
        *cde,
        "install",
        "--with-deps",
        browser_type,
    ]

    if sys.platform.startswith("win") or os.name == "nt":
        log(
            "info",
            f"Start download Playwright for {browser_type} with dependencies, "
            "may require administrator privileges from you."
            f"command: [cyan]{' '.join(command)}[/]",
        )
    else:
        log(
            "info",
            f"Start download Playwright for {browser_type} with dependencies, may require you to access sudo.",
        )

    shell = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, env=env)
    returncode = None

    assert shell.stdout

    progress: Progress | None = None

    while line := re.sub("\x1b.*?m", "", (await shell.stdout.readline()).decode("UTF-8")):
        if "Downloading" in line:
            progress = Progress(line[12:-1])
        if percent := re.findall("(\\d+)%", line):
            progress_target = float(percent[0])
            if progress:
                progress.update(target=progress_target)
        elif p := re.match("(?P<file>.*) downloaded to (?P<path>.*)", line):
            p = p.groupdict()
            log(
                "success",
                "Downloaded [cyan]{file}[/] to [magenta]{path}[/]".format(file=p["file"], path=p["path"]),
            )
        elif line == "Failed to install browsers\n":
            message = await shell.stdout.read()
            log("error", "Download Failed:\n" + message.decode("UTF-8"))
            returncode = 1

    if returncode or shell.returncode:
        log("error", f"Failed to download Playwright for {browser_type}.")
        log("error", "Please see: [magenta]https://playwright.dev/python/docs/intro[/]")
        log(
            "error",
            "Run [magenta]poetry run playwright install[/] or "
            "[magenta]pdm run playwright install[/] to install Playwright manually.",
        )
    else:
        log("success", f"Playwright for {browser_type} is installed.")
