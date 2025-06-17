# bilichat-request

> api docs: https://apifox.com/apidoc/shared-4c1ba1cb-aa98-4a24-9986-193ab8f1519e/246937366e0

> cookiecloud: https://github.com/easychen/CookieCloud/blob/master/README_cn.md

⚠️ 由于未知原因，长时间运行可能导致浏览器崩溃、网络故障及未知错误，建议项目定时重启以避免未知错误 ⚠️

## 安装与运行

### 使用 Docker 运行(推荐)

使用 Docker Compose 运行

```shell
docker-compose up -d
```

或使用 Docker 命令运行

```shell
docker run -d \
--name bilichat-request \
-p 40432:40432 \
-v /your/path/to/project/config.yaml:/app/config.yaml \
-v /your/path/to/project/data:/app/data \
-v /your/path/to/project/logs:/app/logs \
well404/bilichat-request:latest
```

### 直接安装并运行

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

具体的配置项及默认值可以参考 [config.py](https://github.com/Well2333/bilichat-request/blob/main/src/bilichat_request/model/config.py)。
