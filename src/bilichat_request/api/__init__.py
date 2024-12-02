from importlib.metadata import version

from fastapi import APIRouter

from ..config import config
from .account import router as account_router
from .base import app
from .render import router as render_router

router = APIRouter()

router.include_router(render_router, prefix="/render")
router.include_router(account_router, prefix="/account")


@router.get("/version")
async def pkg_version():
    return version("bilichat-request")


app.include_router(router, prefix=f"/{config.api_path}")
