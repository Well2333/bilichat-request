import json
import sys
from pathlib import Path

import yaml
from loguru import logger
from pytz import timezone

from .model.config import Config

nonebot_env = bool({x for x in sys.modules if "nonebot" in x})

BILICHAT_MIN_VERSION = "6.0.7"

if nonebot_env:
    logger.info("检测到 nonebot2 运行, 启用兼容运行模型")
else:
    logger.info("未检测到 nonebot2 运行, 启用独立模式")


def set_config(config_: Config):
    global config  # noqa: PLW0603
    config = config_


config = Config()
cfg_path = Path("config.yaml")


def save_config():
    if not nonebot_env:
        cfg_path.write_bytes(yaml.safe_dump(json.loads(config.model_dump_json()), allow_unicode=True).encode("utf-8"))


def load_config():
    if not nonebot_env and cfg_path.exists():
        config = Config.model_validate(yaml.safe_load(cfg_path.read_bytes()))
        set_config(config)


load_config()


static_dir = Path(__file__).parent / "static"
tz = timezone("Asia/Shanghai")
