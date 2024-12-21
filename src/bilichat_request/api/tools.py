from fastapi import APIRouter, HTTPException

from bilichat_request.account import get_web_account
from bilichat_request.functions.tools import b23_extract as b23_ext

from .base import error_handler

router = APIRouter()


@router.get("/b23_extract")
@error_handler
async def b23_extract(url: str) -> str:
    try:
        return await b23_ext(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/b23_generate")
@error_handler
async def b23_generate(url: str) -> str:
    async with get_web_account() as account:
        b23 = await account.web_requester.get_b23_url(url)
    return b23
