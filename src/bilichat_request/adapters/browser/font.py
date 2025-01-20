from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZipFile

import httpx
from loguru import logger

from bilichat_request.const import data_path

DEFAULT_DYNAMIC_FONT = "HarmonyOS_Sans_SC_Medium.ttf"
font_path = data_path.joinpath("font")
font_path.mkdir(parents=True, exist_ok=True)


def is_absolute(url: str) -> bool:
    p = urlparse(url)
    return bool(p.scheme and p.netloc)


def get_filename(url: str) -> str:
    return Path(urlparse(url).path).name


def check_font_path(font: str) -> Path | None:
    if is_absolute(font):
        name = get_filename(font)
        if font_path.joinpath(name).exists():
            logger.debug(f"Font {name} found in local")
            return font_path.joinpath(name)
    elif font_path.joinpath(font).exists():
        logger.debug(f"Font {font} found in local")
        return font_path.joinpath(font)
    return None


async def get_font_async(font: str = DEFAULT_DYNAMIC_FONT):
    logger.debug(f"Loading font: {font}")
    font_file_path = check_font_path(font)
    if font_file_path:
        return font_file_path
    elif is_absolute(font):
        logger.warning(f"Font {font} does not exist, downloading...")
        async with httpx.AsyncClient() as client:
            resp = await client.get(font)
            if resp.status_code != 200:
                raise ConnectionError(f"Font {font} failed to download")
            name = get_filename(font)
            font_path.joinpath(name).write_bytes(resp.content)
            return font_path.joinpath(name)
    else:
        raise FileNotFoundError(f"Font {font} does not exist")


def get_font_sync(font: str = DEFAULT_DYNAMIC_FONT):
    logger.debug(f"Loading font: {font}")
    font_file_path = check_font_path(font)
    if font_file_path:
        return font_file_path
    elif is_absolute(font):
        logger.warning(f"Font {font} does not exist, downloading...")
        with httpx.Client() as client:
            resp = client.get(font)
            if resp.status_code != 200:
                raise ConnectionError(f"Font {font} failed to download")
            name = get_filename(font)
            font_path.joinpath(name).write_bytes(resp.content)
            return font_path.joinpath(name)
    else:
        raise FileNotFoundError(f"Font {font} does not exist")


def font_init():
    font_url = (
        "https://mirrors.bfsu.edu.cn/pypi/web/packages/ad/97/"
        "03cd0a15291c6c193260d97586c4adf37a7277d8ae4507d68566c5757a6a/"
        "bbot_fonts-0.1.1-py3-none-any.whl"
    )
    lock_file = font_path.joinpath(".lock")
    lock_file.touch(exist_ok=True)
    if lock_file.read_text() != font_url:
        logger.warning("font file does not exist. Trying to download")
        font_file = BytesIO()
        with httpx.Client() as client:
            client.follow_redirects = True
            with client.stream("GET", font_url) as r:
                for chunk in r.iter_bytes():
                    font_file.write(chunk)
        with ZipFile(font_file) as z:
            fonts = [i for i in z.filelist if str(i.filename).startswith("bbot_fonts/font/")]
            for f in fonts:
                file_name = Path(f.filename).name
                local_file = font_path.joinpath(file_name)
                if not local_file.exists():
                    logger.debug(local_file)
                    local_file.write_bytes(z.read(f))

        lock_file.write_text(font_url)


font_init()
