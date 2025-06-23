import json
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from loguru import logger

from bilichat_request.account import CCWebAccount, NormalWebAccount, account_manager
from bilichat_request.account.base import Note

from .base import error_handler

router = APIRouter()


@router.get("/web_account")
@error_handler
async def get_web_account():
    return [{"uid": str(v.uid), "note": v.note} for v in account_manager.accounts.values()]


@router.post("/web_account/create")
@error_handler
async def add_web_account(cookies: dict[str, Any], note: Note | None = None):
    """
    添加普通Web账号

    支持的格式:
    - 键值对格式的cookies (dict), 必须包含DedeUserID

    注意: 不再支持通过API添加CookieCloud账号, 请在config.yaml中配置
    """
    try:
        # 只创建普通账号
        acc = NormalWebAccount.load_from_cookies(cookies, note)
        acc.save()

        # 将账号添加到管理器中
        account_manager.add_account(acc)

        return Response(status_code=201, content=json.dumps(acc.info, ensure_ascii=False))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/web_account/delete")
@error_handler
async def delete_web_account(uid: int | str):
    """
    删除普通Web账号

    - 只支持删除普通账号
    - CookieCloud账号不支持通过API删除, 请修改config.yaml
    """
    accounts = account_manager.accounts.copy()

    # 查找并删除普通账号
    for acc in accounts.values():
        if str(acc.uid) == str(uid) and isinstance(acc, NormalWebAccount):
            acc.remove()
            return Response(status_code=200, content=json.dumps(acc.info, ensure_ascii=False))

    # 检查是否为CookieCloud账号

    for acc in accounts.values():
        if str(acc.uid) == str(uid) and isinstance(acc, CCWebAccount):
            raise HTTPException(
                status_code=400, detail=f"CookieCloud 账号 <{uid}> 不支持通过API删除, 请在config.yaml中移除配置"
            )

    raise HTTPException(status_code=404, detail=f"普通 Web 账号 <{uid}> 不存在")
