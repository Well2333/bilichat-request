from collections.abc import Callable
from functools import wraps
from json import JSONDecodeError

from cachetools import TTLCache
from httpx import ConnectError, TransportError
from loguru import logger
from sentry_sdk import capture_exception

from bilichat_request.account import get_web_account
from bilichat_request.config import config
from bilichat_request.exceptions import AbortError, ResponseCodeError

from .model import CARD_TYPE_MAP, Dynamic, DynamicType

dyn_cache = TTLCache(maxsize=99999, ttl=config.dynamic_cache_ttl or 1)  # type: ignore


def cache_dynamics(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(up_uid: int, *args, **kwargs) -> list[Dynamic]:
        if not kwargs.get("offset", 0) and config.dynamic_cache_ttl and (cached := dyn_cache.get(up_uid)):
            logger.debug(f"使用缓存: {up_uid}")
            return cached

        result = await func(up_uid, *args, **kwargs)
        if config.dynamic_cache_ttl:
            dyn_cache[up_uid] = result
        return result

    return wrapper


def dyn_error_handler(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):  # noqa: ANN202
        try:
            logger.trace(f"执行请求: {func.__name__} {args} {kwargs}")
            return await func(*args, **kwargs)
        except (TransportError, ConnectError, JSONDecodeError, ResponseCodeError) as e:
            logger.error(f"获取动态状态失败: {type(e)} {e}")
            raise AbortError(f"获取动态状态失败: {type(e)} {e}") from e
        except RuntimeError as e:
            logger.error(f"获取动态状态失败: {type(e)} {e}")
            if "The connection pool was closed while" not in str(e):
                capture_exception(e)
            raise AbortError(f"获取动态状态失败: {type(e)} {e}") from e
        except Exception as e:
            logger.error(e)
            capture_exception(e)
            raise

    return wrapper


@dyn_error_handler
@cache_dynamics
async def get_dynamic_by_uid(up_uid: int, offset: int = 0) -> list[Dynamic]:
    dyns: list[Dynamic] = []
    async with get_web_account() as account:
        resp = await account.web_requester.get_user_dynamics(up_uid, offset=offset)
        items = resp.get("items", [])
        if items:
            dyns.extend(
                [
                    Dynamic(
                        dyn_id=int(item["id_str"]),
                        dyn_type=item["type"],
                        dyn_timestamp=item["modules"]["module_author"]["pub_ts"],
                    )
                    for item in items
                ]
            )
    return dyns


@dyn_error_handler
@cache_dynamics
async def get_dynamic_by_uid_old(up_uid: int) -> list[Dynamic]:
    dyns: list[Dynamic] = []
    async with get_web_account() as account:
        resp = await account.web_requester.get_user_dynamics_old(up_uid)
        cards = resp.get("cards", [])
        if cards:
            dyns.extend(
                [
                    Dynamic(
                        dyn_id=int(card["desc"]["dynamic_id_str"]),
                        dyn_type=CARD_TYPE_MAP.get(card["desc"]["type"], DynamicType.NONE),
                        dyn_timestamp=card["desc"]["timestamp"],
                    )
                    for card in cards
                ]
            )
    return dyns
