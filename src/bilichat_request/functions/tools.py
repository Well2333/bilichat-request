import contextlib
import re

from httpx import AsyncClient

from bilichat_request.config import config


async def b23_extract(raw_b23: str) -> str:
    if "b23" in raw_b23 and (b23_ := re.search(r"b23.(tv|wtf)[\\/]+(\w+)", raw_b23)):
        b23 = list(b23_.groups())[1]
    else:
        b23 = raw_b23

    url = f"https://b23.tv/{b23}"
    async with AsyncClient(
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39"
            )
        },
        follow_redirects=True,
    ) as client:
        for _ in range(config.retry):
            with contextlib.suppress(Exception):
                resp = await client.get(url, follow_redirects=True)
                return str(resp.url).split("?")[0]
        raise ValueError(f"无法解析 {raw_b23}")
