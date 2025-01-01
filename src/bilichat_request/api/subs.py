from fastapi import APIRouter, Request

from bilichat_request.functions.subs.dynamic import get_dynamic_by_uid
from bilichat_request.functions.subs.dynamic.model import Dynamic
from bilichat_request.functions.subs.live import get_live_by_uids
from bilichat_request.functions.subs.live.model import LiveRoom

from .base import error_handler, limiter

router = APIRouter()


@router.get("/live")
@limiter.limit("3/minute")
@error_handler
async def get_live(request: Request, uid: int) -> list[LiveRoom]:
    return await get_live_by_uids([uid])


@router.post("/lives")
@limiter.limit("3/minute")
@error_handler
async def get_lives(request: Request, uids: list[int]) -> list[LiveRoom]:
    return await get_live_by_uids(uids)


@router.get("/dynamic")
@limiter.limit("12/minute")
@error_handler
async def get_dynamic(request: Request, uid: int, offset: int = 0) -> list[Dynamic]:
    return await get_dynamic_by_uid(uid, offset=offset)
