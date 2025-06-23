from os import getenv
from typing import Literal

from pydantic import BaseModel


class CookieCloud(BaseModel):
    url: str
    """CookieCloud URL"""
    uuid: str
    """CookieCloud UUID"""
    password: str
    """CookieCloud 密码"""


class Config(BaseModel):
    # 基础配置
    log_level: Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    """日志等级, nonebot2 运行时此设置无效"""
    data_path: str = "data"
    """数据存储路径, nonebot2 运行时此设置无效"""
    sentry_dsn: str = ""
    """Sentry DSN"""
    playwright_download_host: str = ""
    """playwright 下载地址"""
    playwright_headless: bool = True
    """playwright 是否启用无头模式, 生产环境请勿关闭, 使用 nonebot_plugin_htmlrender 运行时此设置无效"""

    # 爬虫相关配置
    retry: int = 3
    """请求重试次数"""
    timeout: int = 20
    """请求超时时间"""
    dynamic_cache_ttl: int = 120
    """动态获取(高风控接口)缓存时间, 0 为禁用缓存"""
    pc_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
    """PC 端 User-Agent"""
    mobile_user_agent: str = "Mozilla/5.0 (Android 15; Mobile; rv:135.0) Gecko/135.0 Firefox/135.0"
    """移动端 User-Agent"""

    # FastAPI 相关配置
    api_host: str = getenv("API_HOST", "127.0.0.1")
    """API 监听地址, nonebot2 运行时此设置无效"""
    api_port: int = 40432
    """API 监听端口, nonebot2 运行时此设置无效"""
    api_path: str = "bilichatapi"
    """API 路由前缀"""
    api_access_token: str = ""
    """API 访问令牌"""
    api_sub_dynamic_limit: str = "720/hour"
    """API 订阅动态限制, 参数可参考 https://limits.readthedocs.io/en/stable/quickstart.html#rate-limit-string-notation"""
    api_sub_live_limit: str = "1800/hour"
    """API 订阅直播限制, 参数可参考 https://limits.readthedocs.io/en/stable/quickstart.html#rate-limit-string-notation"""
    api_enable_health_check: bool = getenv("DOCKER", "").lower() in ("true", "1", "yes")
    """是否启用健康检查接口, 主要用于Docker环境"""

    # 账号相关配置
    account_recover_interval: int = 120
    """可恢复的账号失效后重试获取的间隔时间(秒)"""
    ## cookie cloud 相关配置
    cookie_clouds: list[CookieCloud] = []
    """CookieCloud 配置, 用于自动获取 cookie"""
