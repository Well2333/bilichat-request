import sys
from pathlib import Path
from secrets import token_urlsafe
from typing import Literal

from loguru import logger
from pydantic import BaseModel
from pytz import timezone

nonebot_env = "nonebot2" in sys.modules

if nonebot_env:
    logger.info("检测到 nonebot2 运行, 启用兼容运行模型")
else:
    logger.info("未检测到 nonebot2 运行, 启用独立模式")


class Config(BaseModel):
    log_level: Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "TRACE"
    retry: int = 3
    data_path: str = "data"
    sentry_dsn: str = ""
    proxy: str = ""
    playwright_download_host: str = ""

    # FastAPI config
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_path: str = "bilichatapi"
    api_access_token: str = "123"


token = token_urlsafe(16)
logger.info(f"API 鉴权 Token: {token}")

config = Config()
data_path = Path(config.data_path)
data_path.mkdir(parents=True, exist_ok=True)

static_dir = Path(__file__).parent / "static"
tz = timezone("Asia/Shanghai")
