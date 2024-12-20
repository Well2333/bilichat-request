from fastapi import APIRouter, Response

from bilichat_request.functions.render import column, dynamic
from bilichat_request.functions.render.video import style_blue

from .base import error_handler

router = APIRouter()


@router.get("/video")
@error_handler
async def render_video(video_id: int | str, quality: int = 75):
    img = await style_blue.screenshot(video_id, quality=quality)
    return Response(img)


@router.get("/column")
@error_handler
async def render_column(cvid: int | str, quality: int = 75) -> Response:
    cvid = str(cvid)
    if cvid.startswith("cv"):
        cvid = cvid[2:]
    return Response(await column.screenshot(cvid=str(cvid), quality=quality))


@router.get("/dynamic")
@error_handler
async def render_dynamic(dynamic_id: str, quality: int = 75, *, mobile_style: bool = True):
    return Response(await dynamic.screenshot(dynamic_id, mobile_style=mobile_style, quality=quality))
