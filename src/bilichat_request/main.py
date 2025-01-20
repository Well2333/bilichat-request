import contextlib

from uvicorn import Config, Server

from bilichat_request.api.base import app
from bilichat_request.config import config
from bilichat_request.log import LOGGING_CONFIG


def main():
    with contextlib.suppress(KeyboardInterrupt):
        Server(
            Config(
                app,
                host=config.api_host,
                port=config.api_port,
                log_config=LOGGING_CONFIG,
            )
        ).run()
