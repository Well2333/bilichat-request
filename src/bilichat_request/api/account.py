import json
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from loguru import logger

from bilichat_request.account import Note, WebAccount, _web_accounts

from .base import error_handler

router = APIRouter()


@router.get("/web_account")
@error_handler
async def get_web_account():
    return [{"uid": str(v.uid), "note": v.note} for v in _web_accounts.values()]


@router.post("/web_account/create")
@error_handler
async def add_web_account(uid: int, cookies: list[dict[str, Any]] | dict[str, Any], note: Note | None = None):
    try:
        if isinstance(cookies, list):
            cookies_ = {}
            for auth_ in cookies:
                cookies_[auth_["name"]] = auth_["value"]
            acc = WebAccount(
                uid=cookies_["DedeUserID"],
                cookies=cookies_,
            )
            acc.save()
            _web_accounts[uid] = acc
            return Response(status_code=201, content=json.dumps(acc.dump(), ensure_ascii=False))
        elif isinstance(cookies, dict):
            acc = WebAccount(uid=uid, cookies=cookies, note=note)
            acc.save()
            _web_accounts[uid] = acc
            return Response(status_code=201, content=json.dumps(acc.dump(), ensure_ascii=False))
        raise ValueError(f"无法解析的 cookies 数据: {cookies}")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/web_account/delete")
@error_handler
async def delete_web_account(uid: int):
    if uid not in _web_accounts:
        raise HTTPException(status_code=404, detail=f"Web 账号 <{uid}> 不存在")
    acc = _web_accounts.pop(uid)
    return Response(status_code=200, content=json.dumps(acc.dump(exclude_cookies=True), ensure_ascii=False))
