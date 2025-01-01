from fastapi import APIRouter, HTTPException, Request

from bilichat_request.config import config
from bilichat_request.functions.subs.dynamic import get_dynamic_by_uid
from bilichat_request.functions.subs.dynamic.model import Dynamic
from bilichat_request.functions.subs.live import get_live_by_uids
from bilichat_request.functions.subs.live.model import LiveRoom

from .base import error_handler, limiter

router = APIRouter()


@router.get("/live")
@limiter.limit(config.api_sub_live_limit)
@error_handler
async def get_live(request: Request, uid: int) -> list[LiveRoom]:  # noqa: ARG001
    if not uid:
        raise HTTPException(status_code=400, detail="uid 参数不能为空")
    return await get_live_by_uids([uid])


@router.post("/lives")
@limiter.limit(config.api_sub_live_limit)
@error_handler
async def get_lives(request: Request, uids: list[int]) -> list[LiveRoom]:  # noqa: ARG001
    if not uids:
        raise HTTPException(status_code=400, detail="uids 参数不能为空")
    return await get_live_by_uids(uids)


@router.get("/dynamic")
@limiter.limit(config.api_sub_dynamic_limit)
@error_handler
async def get_dynamic(request: Request, uid: int, offset: int = 0) -> list[Dynamic]:  # noqa: ARG001
    return await get_dynamic_by_uid(uid, offset=offset)
