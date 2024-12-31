from fastapi import APIRouter

from bilichat_request.functions.subs.dynamic import get_dynamic_by_uid
from bilichat_request.functions.subs.dynamic.model import Dynamic
from bilichat_request.functions.subs.live import get_live_by_uids
from bilichat_request.functions.subs.live.model import LiveRoom

from .base import error_handler

router = APIRouter()


@router.get("/live")
@error_handler
async def get_live(uid: int) -> list[LiveRoom]:
    return await get_live_by_uids([uid])


@router.post("/lives")
@error_handler
async def get_lives(uids: list[int]) -> list[LiveRoom]:
    return await get_live_by_uids(uids)


@router.get("/dynamic")
@error_handler
async def get_dynamic(uid: int, offset: int = 0) -> list[Dynamic]:
    return await get_dynamic_by_uid(uid, offset=offset)
