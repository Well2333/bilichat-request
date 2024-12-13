from fastapi import APIRouter, Response

from bilichat_request.functions.subs.live import get_live_by_uids

from .base import error_handler

router = APIRouter()


@router.get("/live")
@error_handler
async def get_live(uids: list[int]):
    return Response(await get_live_by_uids(uids))
