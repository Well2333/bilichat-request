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
    log_level: Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    """日志等级, nonebot2 运行时此设置无效"""
    retry: int = 3
    """请求重试次数"""
    data_path: str = "data"
    """数据存储路径, nonebot2 运行时此设置无效"""
    sentry_dsn: str = ""
    """Sentry DSN"""
    playwright_download_host: str = ""
    """playwright 下载地址"""

    # FastAPI config
    api_host: str = "127.0.0.1"
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

    # cookie cloud config
    cookie_clouds: list[CookieCloud] = []
    """CookieCloud 配置, 用于自动获取 cookie"""