# BiliChat Request

一个用于获取哔哩哔哩内容的 API 服务，支持视频、动态、专栏等内容的截图渲染，以及账户管理、订阅监控等功能。


[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://hub.docker.com/r/well404/bilichat-request)

## ✨ 主要功能

- 🖼️ **内容截图**: 视频、动态、专栏内容的自动截图生成
- 👤 **账户管理**: 支持多账户管理，自动cookie同步
- 📡 **订阅监控**: 直播状态监控、用户动态获取
- 🔗 **链接处理**: B23短链接生成和解析
- 🛠️ **RESTful API**: 完整的API接口，易于集成
- 🐳 **Docker支持**: 一键部署，开箱即用

## 🚀 快速开始

### 使用 Docker 运行（推荐）

```bash
# 使用 Docker Compose
docker-compose up -d

# 或使用 Docker 命令
docker run -d \
  --name bilichat-request \
  -p 40432:40432 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/data:/app/data \
  well404/bilichat-request:latest
```

### 使用 pip 安装

```bash
# 安装 pipx（推荐）
pip install pipx
pipx install bilichat-request

# 或直接使用 pip
pip install bilichat-request

# 启动服务
bilirq
```

服务启动后，访问 `http://localhost:40432` 即可使用API。

## 📚 API 文档

| 模块 | 描述 | 链接 |
|------|------|------|
| 📋 **API 概述** | API 基础信息和认证说明 | [docs/api-overview.md](docs/api-overview.md) |
| 👤 **账户管理** | Web账户的增删查管理 | [docs/account.md](docs/account.md) |
| 🖼️ **内容服务** | 视频、动态、专栏截图服务 | [docs/content.md](docs/content.md) |
| 📡 **订阅服务** | 直播监控和动态获取 | [docs/subs.md](docs/subs.md) |
| 🔧 **工具服务** | B23链接处理和UP主搜索 | [docs/tools.md](docs/tools.md) |
| 💻 **系统接口** | 版本信息和健康检查 | [docs/system.md](docs/system.md) |

## 🔧 快速配置

创建 `config.yaml` 文件进行基本配置：

```yaml
# API 访问控制
api_access_token: "your_secure_token"

# CookieCloud 同步（可选）
cookie_clouds:
  - url: "https://your-cookiecloud.com"
    uuid: "your-uuid"
    password: "your-password"

# 日志等级
log_level: "INFO"
```

更多配置选项请参考 [配置文档](src/bilichat_request/model/config.py)。

## 📖 API 使用示例

```bash
# 获取视频截图
curl -X GET "http://localhost:40432/bilichatapi/content/video?video_id=BV1xx411c7mu" \
  -H "Authorization: Bearer your_token"

# 获取用户动态
curl -X GET "http://localhost:40432/bilichatapi/subs/dynamic?uid=123456" \
  -H "Authorization: Bearer your_token"

# 搜索UP主
curl -X GET "http://localhost:40432/bilichatapi/tools/search_up?keyword=测试" \
  -H "Authorization: Bearer your_token"
```

完整API文档请查看 [API文档](docs/api-overview.md)。

## ⚠️ 重要提示

- 长时间运行可能遇到浏览器崩溃、网络故障等问题，建议定时重启服务
- 生产环境请务必配置访问令牌（`api_access_token`）
- 确保有足够的系统资源用于浏览器渲染

## 🔗 相关链接

- [API 在线文档](https://apifox.com/apidoc/shared-4c1ba1cb-aa98-4a24-9986-193ab8f1519e/246937366e0)
- [CookieCloud 项目](https://github.com/easychen/CookieCloud)
- [Docker Hub](https://hub.docker.com/r/well404/bilichat-request)
