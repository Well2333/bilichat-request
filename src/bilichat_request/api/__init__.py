import os
from datetime import datetime
from importlib.metadata import version

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bilichat_request.config import BILICHAT_MIN_VERSION, config, tz

from .account import router as account_router
from .base import app
from .content import router as content_router
from .subs import router as subs_router
from .tools import router as tools_router

security = HTTPBearer()
router = APIRouter()
router.include_router(content_router, prefix="/content")
router.include_router(account_router, prefix="/account")
router.include_router(subs_router, prefix="/subs")
router.include_router(tools_router, prefix="/tools")


async def verify_token(cred: HTTPAuthorizationCredentials = Depends(security)):
    if cred.credentials != config.api_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )


@router.get("/version")
async def pkg_version():
    return {
        "version": version("bilichat-request"),
        "bilichat_min_version": BILICHAT_MIN_VERSION,
        "package": "bilichat-request",
        "datetime": datetime.now(tz).isoformat(),
    }


# 仅在Docker环境下启用健康检查接口
if os.getenv("DOCKER", "").lower() in ("true", "1", "yes"):
    @app.get("/health")
    async def health_check():
        """健康检查接口，仅在Docker环境下启用"""
        return {"status": "ok"}


app.include_router(
    router, prefix=f"/{config.api_path}", dependencies=[Depends(verify_token)] if config.api_access_token else []
)
