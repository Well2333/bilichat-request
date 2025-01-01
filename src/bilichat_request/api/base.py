import asyncio
from collections.abc import Callable
from functools import wraps

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

from bilichat_request.config import config, nonebot_env
from bilichat_request.exceptions import AbortError, CaptchaAbortError, NotFindAbortError, ResponseCodeError

# 初始化 Limiter, 默认使用内存存储
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def error_handler(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):  # noqa: ANN202
        try:
            logger.trace(f"执行请求: {func.__name__} {args} {kwargs}")
            return await func(*args, **kwargs)
        except asyncio.TimeoutError as e:
            logger.info(e)
            raise HTTPException(status_code=429, detail={"type": str(type(e)), "detail": str(e)}) from e
        except NotFindAbortError as e:
            logger.info(e)
            raise HTTPException(status_code=404, detail={"type": str(type(e)), "detail": str(e)}) from e
        except HTTPException as e:
            logger.info(f"{type(e)} {e.status_code} {e.detail}")
            raise
        except (AbortError, ResponseCodeError, CaptchaAbortError) as e:
            logger.error(e)
            raise HTTPException(status_code=511, detail={"type": str(type(e)), "detail": str(e)}) from e
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail={"type": str(type(e)), "detail": str(e)}) from e

    return wrapper


if nonebot_env:
    import nonebot
    from nonebot.drivers import ReverseDriver
    from nonebot.drivers.fastapi import Driver as FastAPIDriver

    driver: FastAPIDriver = nonebot.get_driver()  # type: ignore

    if not isinstance(driver, ReverseDriver) or not isinstance(driver.server_app, FastAPI):
        raise NotImplementedError("Only FastAPI reverse driver is supported.")

    driver.server_app.mount(f"/{config.api_path}", app, name="bilichat_api")
