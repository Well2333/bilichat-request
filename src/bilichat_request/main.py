from uvicorn import Config, Server

from bilichat_request.api.base import app
from bilichat_request.config import config, nonebot_env

if not nonebot_env:
    from bilichat_request.log import LOGGING_CONFIG

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

    if __name__ == "__main__":
        main()
