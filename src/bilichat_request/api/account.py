import json
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from loguru import logger

from bilichat_request.account import Note, PyCookieCloud, WebAccount, _web_accounts
from bilichat_request.model.config import CookieCloud

from .base import error_handler

router = APIRouter()


@router.get("/web_account")
@error_handler
async def get_web_account():
    return [{"uid": str(v.uid), "note": v.note} for v in _web_accounts.values()]


@router.post("/web_account/create")
@error_handler
async def add_web_account(cookies: list[dict[str, Any]] | dict[str, Any] | CookieCloud, note: Note | None = None):
    try:
        cookie_cloud = None
        if isinstance(cookies, CookieCloud):
            cookie_cloud = PyCookieCloud(cookies.url, cookies.uuid, cookies.password)
            cookies = await cookie_cloud.get_cookie()

        acc = WebAccount.load_from_json(cookies)
        if note:
            acc.note = note
        if cookie_cloud:
            acc.cookie_cloud = cookie_cloud
        acc.save()
        _web_accounts[acc.uid] = acc
        return Response(status_code=201, content=json.dumps(acc.dump(exclude_cookies=True), ensure_ascii=False))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/web_account/delete")
@error_handler
async def delete_web_account(uid: int | str):
    for acc in _web_accounts.values():
        if str(acc.uid) == str(uid) or (acc.cookie_cloud and acc.cookie_cloud.uuid == str(uid)):
            acc.remove()
            return Response(status_code=200, content=json.dumps(acc.dump(exclude_cookies=True), ensure_ascii=False))
    raise HTTPException(status_code=404, detail=f"Web 账号 <{uid}> 不存在")
