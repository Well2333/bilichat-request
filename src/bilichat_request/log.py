import logging
import sys
from pathlib import Path

from loguru import logger

from .config import config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "class": "bilichat_request.log.LoguruHandler",
        },
    },
    "loggers": {
        "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
        },
    },
}


class LoguruHandler(logging.Handler):  # pragma: no cover
    """logging 与 loguru 之间的桥梁, 将 logging 的日志转发到 loguru。"""

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logger.remove()

# ensure logs dir exist
LOGPATH = Path("logs")
LOGPATH.mkdir(exist_ok=True)
LOGURU_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green>|<level>{level: <8}</level>|\
<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


# add file logger
logger.add(
    LOGPATH.joinpath("trace/{time:YYYY-MM-DD}.log"),
    format=LOGURU_FORMAT,
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
    rotation="00:00",
    colorize=False,
    level="TRACE",
)

logger.add(
    LOGPATH.joinpath("{time:YYYY-MM-DD}.log"),
    format=LOGURU_FORMAT,
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
    rotation="00:00",
    colorize=False,
    level="INFO",
)

# add stdout logger
logger.add(
    sys.stdout,
    format=LOGURU_FORMAT,
    backtrace=True,
    diagnose=True,
    colorize=True,
    level=config.log_level,
)

# request logger
logger.add(
    LOGPATH.joinpath("req/{time:YYYY-MM-DD}.log"),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green>|<level>{level: <8}</level>|<level>{message}</level>",
    filter=lambda record: record["extra"].get("handler") == "request",
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
    rotation="00:00",
    colorize=False,
    level="TRACE",
)