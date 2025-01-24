# bilichat-request

> api docs: https://apifox.com/apidoc/shared-4c1ba1cb-aa98-4a24-9986-193ab8f1519e/246937366e0

> cookiecloud: https://github.com/easychen/CookieCloud/blob/master/README_cn.md

## 安装并运行

直接使用 pip 或 pipx 安装即可，推荐使用 pipx 或类似的工具，以避免污染系统环境。

```shell
pip install pipx
pipx install bilichat-request
```

安装完成后，可以直接使用 `bilirq` 命令启动。

```shell
bilirq
```

## 调整配置

在工作路径下创建 `config.yaml` 文件，并向其中添加所需要调整的内容即可，例如：

```yaml
cookie_clouds:
  - url: https://example.com
    uuid: ********
    password: ********
```

具体的配置项及默认值可以参考 [config.py](https://github.com/Well2333/bilichat-request/blob/main/src/bilichat_request/config.py)。