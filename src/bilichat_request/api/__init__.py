from datetime import datetime
from importlib.metadata import version

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bilichat_request.config import config, tz

from .account import router as account_router
from .base import app
from .render import router as render_router
from .subs import router as subs_router

security = HTTPBearer()
router = APIRouter()
router.include_router(render_router, prefix="/render")
router.include_router(account_router, prefix="/account")
router.include_router(subs_router, prefix="/subs")


async def verify_token(cred: HTTPAuthorizationCredentials = Depends(security)):  # noqa: B008
    if cred.credentials != config.api_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )


@router.get("/version")
async def pkg_version():
    return {
        "version": version("bilichat-request"),
        "package": "bilichat-request",
        "datetime": datetime.now(tz).isoformat(),
    }


app.include_router(
    router, prefix=f"/{config.api_path}", dependencies=[Depends(verify_token)] if config.api_access_token else []
)
