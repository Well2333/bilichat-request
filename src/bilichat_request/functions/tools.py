import contextlib
import re

from httpx import AsyncClient
from nonebot.log import logger
from pydantic import BaseModel, Field

from bilichat_request.account import get_web_account
from bilichat_request.config import config


class SearchUp(BaseModel):
    nickname: str = Field(validation_alias="title")
    uid: int = Field(validation_alias="mid")

    def __str__(self) -> str:
        return f"{self.nickname}({self.uid})"


class SearchResult(BaseModel):
    items: list[SearchUp] = []


async def search_up(text_u: str, ps: int = 5) -> SearchUp | list[SearchUp]:
    text_u = text_u.strip(""""'“”‘’""").strip().replace("：", ":")  # noqa: RUF001
    async with get_web_account() as account:
        resp = await account.web_requester.search_user(text_u, ps)
        result = SearchResult(**resp)
    if result.items:
        for up in result.items:
            if up.nickname == text_u or str(up.uid) in text_u:
                logger.debug(up)
                return up
    # 没有找到对应的 up 但是输入的是 uid
    if text_u.isdigit():
        return await search_up("UID: " + text_u, ps)
    # 没有找到对应的 up
    return result.items


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


XOR_CODE = 23442827791579
MASK_CODE = 2251799813685247
MAX_AID = 1 << 51
ALPHABET = "FcwAPNKTMug3GV5Lj7EJnHpWsx4tb8haYeviqBz6rkCy12mUSDQX9RdoZf"
ENCODE_MAP = 8, 7, 0, 5, 1, 3, 2, 4, 6
DECODE_MAP = tuple(reversed(ENCODE_MAP))

BASE = len(ALPHABET)
PREFIX = "BV1"
PREFIX_LEN = len(PREFIX)
CODE_LEN = len(ENCODE_MAP)


def av2bv(aid: int) -> str:
    bvid = [""] * 9
    tmp = (MAX_AID | aid) ^ XOR_CODE
    for i in range(CODE_LEN):
        bvid[ENCODE_MAP[i]] = ALPHABET[tmp % BASE]
        tmp //= BASE
    return PREFIX + "".join(bvid)


def bv2av(bvid: str) -> int:
    assert bvid[:3].upper() == PREFIX

    bvid = bvid[3:]
    tmp = 0
    for i in range(CODE_LEN):
        idx = ALPHABET.index(bvid[DECODE_MAP[i]])
        tmp = tmp * BASE + idx
    return (tmp & MASK_CODE) ^ XOR_CODE
