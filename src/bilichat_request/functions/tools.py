import contextlib
import re
from typing import Any

from httpx import AsyncClient
from loguru import logger
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


def shorten_long_items(
    obj: Any,  # noqa:
    max_length: int = 100,
    prefix_length: int = 10,
    suffix_length: int = 10,
    max_list_length: int = 50,
    list_prefix: int = 3,
    list_suffix: int = 1,
) -> Any:
    """
    递归遍历 JSON 对象, 缩短超过指定长度的字符串和列表。

    :param obj: 要处理的 JSON 对象(可以是 dict, list, str, etc.)
    :param max_length: 定义何时需要缩短的最大长度阈值
    :param prefix_length: 缩短后保留的前缀长度
    :param suffix_length: 缩短后保留的后缀长度
    :param max_list_length: 定义何时需要缩短的最大列表长度阈值
    :param list_prefix: 缩短后保留的列表前缀长度
    :param list_suffix: 缩短后保留的列表后缀长度
    :return: 处理后的 JSON 对象
    """
    if not obj:
        return obj
    if isinstance(obj, BaseModel):
        obj = obj.model_dump()

    if isinstance(obj, dict):
        return {k: shorten_long_items(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        if len(obj) > max_list_length:
            placeholder = f"...[total:{len(obj)}]..."
            shortened = obj[:list_prefix] + [placeholder] + obj[-list_suffix:]
            return [shorten_long_items(item) if item != placeholder else item for item in shortened]
        else:
            return [shorten_long_items(item) for item in obj]
    elif isinstance(obj, str):
        return f"{obj[:prefix_length]}...[total:{len(obj)}]...{obj[-suffix_length:]}" if len(obj) > max_length else obj
    elif isinstance(obj, tuple | set):
        processed = shorten_long_items(list(obj))
        return type(obj)(processed)
    else:
        return obj
