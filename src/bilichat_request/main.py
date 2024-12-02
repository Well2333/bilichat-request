from uvicorn import Config, Server

from .api.base import app
from .config import config, nonebot_env

if not nonebot_env:
    from .log import LOGGING_CONFIG

    if config.sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(
            dsn=config.sentry_dsn,
            traces_sample_rate=1.0,
        )

    def main():
        Server(
            Config(
                app,
                host=config.api_host,
                port=config.api_port,
                log_config=LOGGING_CONFIG,
            )
        ).run()
