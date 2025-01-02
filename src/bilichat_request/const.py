from pathlib import Path

from .config import config

data_path = Path(config.data_path)
data_path.mkdir(parents=True, exist_ok=True)
