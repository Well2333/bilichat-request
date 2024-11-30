from pydantic import BaseModel
from pathlib import Path


class Config(BaseModel):
    retry: int = 3
    data_path: str = "data"
    sentry_dsn: str = ""
    proxy: str = ""
    playwright_download_host: str = ""


config = Config()
data_path = Path(config.data_path)
data_path.mkdir(parents=True, exist_ok=True)

static_dir = Path(__file__).parent / "static"
