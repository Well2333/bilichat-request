from collections.abc import Sequence
from json import JSONDecodeError

from httpx import ConnectError, TransportError
from loguru import logger
from sentry_sdk import capture_exception

from bilichat_request.account import get_web_account
from bilichat_request.exceptions import AbortError, ResponseCodeError

from .model import LiveRoom


async def get_live_by_uids(ups: Sequence[int]) -> list[LiveRoom]:
    async with get_web_account() as account:
        try:
            status_infos = await account.web_requester.get_rooms_info_by_uids(list(ups))
        except (TransportError, ConnectError, JSONDecodeError, ResponseCodeError) as e:
            logger.error(f"获取直播状态失败: {type(e)} {e}")
            raise AbortError(f"获取直播状态失败: {type(e)} {e}") from e
        except RuntimeError as e:
            logger.error(f"[Live] 获取直播状态失败: {type(e)} {e}")
            if "The connection pool was closed while" not in str(e):
                capture_exception(e)
            raise AbortError(f"获取直播状态失败: {type(e)} {e}") from e
        except Exception as e:
            logger.error(e)
            capture_exception(e)
            raise

    rooms = [LiveRoom(**room) for _, room in status_infos.items()]  # type: ignore
    return rooms
