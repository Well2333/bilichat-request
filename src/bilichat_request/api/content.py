import re
from base64 import b64encode
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from bilichat_request.account import get_web_account
from bilichat_request.functions.render import column, dynamic
from bilichat_request.functions.render.video import style_blue

from .base import error_handler

router = APIRouter()


class Content(BaseModel):
    type: Literal["video", "column", "dynamic"]
    id: str
    b23: str
    img: str

    @classmethod
    async def video(cls, video_id: int | str, quality: int = 75) -> "Content":
        img, info = await style_blue.screenshot(video_id, quality=quality)
        return cls(type="video", id=info.aid, b23=info.b23_url, img=b64encode(img).decode())

    @classmethod
    async def column(cls, cvid: int | str, quality: int = 75) -> "Content":
        cvid = str(cvid)
        if cvid.startswith("cv"):
            cvid = cvid[2:]
        async with get_web_account() as account:
            b23 = await account.web_requester.get_b23_url(f"cv{cvid}")
        img = await column.screenshot(cvid=str(cvid), quality=quality)
        return cls(type="column", id=f"cv{cvid}", b23=b23, img=b64encode(img).decode())

    @classmethod
    async def dynamic(cls, dynamic_id: str, quality: int = 75, *, mobile_style: bool = True) -> "Content":
        async with get_web_account() as account:
            b23 = await account.web_requester.get_b23_url(f"https://t.bilibili.com/{dynamic_id}")
        img = await dynamic.screenshot(dynamic_id, mobile_style=mobile_style, quality=quality)
        return cls(type="dynamic", id=dynamic_id, b23=b23, img=b64encode(img).decode())


@router.get("/video")
@error_handler
async def get_video(video_id: int | str, quality: int = 75) -> Content:
    return await Content.video(video_id, quality=quality)


@router.get("/column")
@error_handler
async def get_column(cvid: int | str, quality: int = 75) -> Content:
    return await Content.column(cvid, quality=quality)


@router.get("/dynamic")
@error_handler
async def get_dynamic(dynamic_id: str, quality: int = 75, *, mobile_style: bool = True) -> Content:
    return await Content.dynamic(dynamic_id, quality=quality, mobile_style=mobile_style)


@router.get("/")
@error_handler
async def get_content(bililink: str, quality: int = 75) -> Content:
    if matched := re.search(r"(?i)av(\d{1,15})|bv(1[0-9a-z]{9})", bililink):
        _id = matched.group()
        content = await Content.video(_id, quality=quality)

    elif matched := re.search(r"cv(\d{1,16})", bililink):
        _id = matched.group()
        content = await Content.column(_id, quality=quality)

    elif matched := re.search(r"(dynamic|opus|t.bilibili.com)/(\d{1,128})", bililink):
        _id = matched.group()
        content = await Content.dynamic(_id, quality=quality)

    else:
        raise ValueError("无法识别的链接")

    return content
