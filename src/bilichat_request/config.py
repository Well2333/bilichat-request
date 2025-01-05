import sys
from pathlib import Path
from typing import Literal

import yaml
from loguru import logger
from pydantic import BaseModel
from pytz import timezone

nonebot_env = "nonebot2" in sys.modules

if nonebot_env:
    logger.info("检测到 nonebot2 运行, 启用兼容运行模型")
else:
    logger.info("未检测到 nonebot2 运行, 启用独立模式")


class Config(BaseModel):
    log_level: Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    retry: int = 3
    data_path: str = "data"
    sentry_dsn: str = ""
    playwright_download_host: str = ""
    bilichat_min_version: str = "6.0.2"

    # FastAPI config
    api_host: str = "127.0.0.1"
    api_port: int = 40432
    api_path: str = "bilichatapi"
    api_access_token: str = ""
    api_sub_dynamic_limit: str = "12/minute"
    api_sub_live_limit: str = "30/minute"


def set_config(config_: Config):
    global config  # noqa: PLW0603
    config = config_


config = Config()
if not nonebot_env:
    cfg_path = Path("config.yaml")
    if cfg_path.exists():
        config = Config.model_validate(yaml.safe_load(cfg_path.read_bytes()))
    

static_dir = Path(__file__).parent / "static"
tz = timezone("Asia/Shanghai")
