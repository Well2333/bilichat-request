import asyncio
import contextlib
import itertools
import json
import random
from asyncio import Lock
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger
from typing_extensions import TypedDict

from .adapters.web import WebRequester
from .config import config, tz
from .const import data_path
from .exceptions import ResponseCodeError
from .functions.cookie_cloud import PyCookieCloud


class Note(TypedDict):
    create_time: str
    source: str


class WebAccount:
    lock: Lock
    uid: int
    cookies: dict[str, Any]
    web_requester: WebRequester
    file_path: Path
    note: Note
    cookie_cloud: PyCookieCloud | None

    def __init__(
        self,
        uid: str | int,
        cookies: dict[str, Any],
        note: Note | None = None,
        cookies_cloud: PyCookieCloud | None = None,
    ) -> None:
        self.lock = Lock()
        self.uid = int(uid)
        self.note = note or {
            "create_time": datetime.now(tz=tz).isoformat(timespec="seconds"),
            "source": "",
        }
        self.cookies = cookies
        self.cookie_cloud = cookies_cloud

        self.web_requester = WebRequester(cookies=self.cookies, update_callback=self.update)
        self.file_path = data_path / "auth" / f"web_{self.uid}.json"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.save()
        cc_str = f"(CookieCloud: {self.cookie_cloud.uuid})" if self.cookie_cloud else ""
        logger.success(f"Web 账号 {self.uid}{cc_str} 已加载, 来源: {self.note.get('source', '')}")

    def dump(self, *, exclude_cookies: bool = False) -> dict[str, Any]:
        cookies = {}
        if not exclude_cookies:
            if self.cookie_cloud:
                cookies = {
                    "url": self.cookie_cloud.url,
                    "uuid": self.cookie_cloud.uuid,
                    "password": self.cookie_cloud.password,
                }
            else:
                cookies = self.cookies
        return {
            "uid": self.uid,
            "note": self.note,
            "cookies": cookies,
        }

    def save(self) -> None:
        if self.uid <= 100:
            return
        self.file_path.write_text(
            json.dumps(
                self.dump(),
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def update(self, cookies: dict[str, Any]) -> bool:
        old_cookies = self.cookies
        self.cookies.update(cookies)
        if old_cookies == self.cookies:
            return False
        self.save()
        return True

    def remove(self) -> None:
        if self.uid <= 100:
            return
        self.file_path.unlink()
        _web_accounts.pop(self.uid, None)

    @classmethod
    def load_from_cookiecloud(cls, cloud: PyCookieCloud) -> "WebAccount":
        cookies = cloud.get_cookie_sync()
        return cls(
            uid=str(cookies["DedeUserID"]),
            cookies=cookies,
            cookies_cloud=cloud,
            note={"create_time": datetime.now(tz=tz).isoformat(timespec="seconds"), "source": cloud.url},
        )

    @classmethod
    def load_from_json(cls, auth_json: str | bytes | dict | list) -> "WebAccount":
        if isinstance(auth_json, (str, bytes)):
            auth_json = json.loads(auth_json)
        if isinstance(auth_json, list):
            # 浏览器原始格式的 cookies
            cookies = {auth_["name"]: auth_["value"] for auth_ in auth_json}
            return cls(
                uid=cookies["DedeUserID"],
                cookies=cookies,
            )
        elif isinstance(auth_json, dict):
            if uid := auth_json.get("DedeUserID"):
                # 直接传入的 kv 格式 cookies, 常见于 API 直接传入
                return cls(
                    uid=uid,
                    cookies=auth_json,
                )
            elif auth_json.get("url"):
                # 直接传入的 Cookie Cloud 的 cookies, 常见于 API 直接传入
                cloud = PyCookieCloud(auth_json["url"], auth_json["uuid"], auth_json["password"])
                return cls.load_from_cookiecloud(cloud)
            elif cookies := auth_json.get("cookies"):
                # 本地文件的 cookies
                if isinstance(cookies, dict) and cookies.get("url"):
                    # Cookie Cloud 的 cookies
                    cloud = PyCookieCloud(cookies["url"], cookies["uuid"], cookies["password"])
                    wacc = cls.load_from_cookiecloud(cloud)
                    wacc.note = auth_json.get("note") or wacc.note
                    return wacc
                else:
                    # 本地保存的 cookies
                    return cls(**auth_json)
        raise ValueError(f"无法解析的 cookies 数据: {auth_json}")

    async def check_alive(self, retry: int = config.retry) -> bool:
        try:
            logger.debug(f"查询 Web 账号 <{self.uid}> 存活状态")
            await self.web_requester.check_new_dynamics(0)
            logger.debug(f"Web 账号 <{self.uid}> 确认存活")
        except ResponseCodeError as e:
            if e.code == -101:
                logger.error(f"Web 账号 <{self.uid}> 已失效: {e}")
                return False
            if retry:
                logger.warning(f"Web 账号 <{self.uid}> 查询存活失败: {e}, 重试...")
                await asyncio.sleep(1)
                await self.check_alive(retry=retry - 1)
            return False
        return True


_seqid_generator = itertools.count(0)


@contextlib.asynccontextmanager
async def get_web_account(account_uid: int | None = None):
    seqid = f"{next(_seqid_generator) % 1000:03}"
    logger.debug(f"{seqid}-开始获取 Web 账号。传入的 account_uid={account_uid}")

    timeout = 10  # 超时时间为10秒
    loop = asyncio.get_running_loop()
    start_time = loop.time()

    try:
        if account_uid is not None:
            web_account = await _acquire_specific_account(seqid, account_uid, timeout)
        else:
            web_account = await _acquire_any_account(seqid, timeout, start_time, loop)

        # 检查账户状态并处理失效情况
        web_account = await _validate_and_update_account(seqid, web_account)
        if web_account is None:
            # 重新获取账号
            async with get_web_account() as new_web_account:
                yield new_web_account
                return

        yield web_account

    finally:
        if "web_account" in locals() and web_account:
            if web_account.lock.locked():
                web_account.lock.release()
                logger.debug(f"{seqid}-🔓🟢 <{web_account.uid}>")
            if web_account.uid <= 100:
                del _web_accounts[web_account.uid]
                logger.debug(f"{seqid}-Web 账号 <{web_account.uid}> 已删除")


async def _acquire_specific_account(seqid: str, account_uid: int, timeout: int) -> WebAccount:
    logger.debug(f"{seqid}-尝试获取指定 UID 的 Web 账号: {account_uid}")
    web_account = _web_accounts.get(account_uid)
    if not web_account:
        logger.error(f"{seqid}-Web 账号 <{account_uid}> 不存在")
        raise ValueError(f"Web 账号 <{account_uid}> 不存在")

    try:
        await asyncio.wait_for(web_account.lock.acquire(), timeout=timeout)
        logger.debug(f"{seqid}-🔒🔴 <{web_account.uid}>")
    except asyncio.TimeoutError:
        logger.error(f"{seqid}-🔒⌛️ <{web_account.uid}>")
        raise asyncio.TimeoutError(f"{seqid}-获取 Web 账号 <{web_account.uid}> 超时")  # noqa: B904
    return web_account


async def _acquire_any_account(
    seqid: str, timeout: int, start_time: float, loop: asyncio.AbstractEventLoop
) -> WebAccount:
    if not _web_accounts:
        logger.debug(f"{seqid}-没有可用的 Web 账号, 正在创建临时 Web 账号, 可能会受到风控限制")
        new_uid = random.randint(1, 100)  # 根据实际需求调整UID范围
        web_account = WebAccount(new_uid, {})
        _web_accounts[new_uid] = web_account
        logger.debug(f"{seqid}-🔒🔴 <{web_account.uid}>")
        await web_account.lock.acquire()
        return web_account

    logger.debug(f"{seqid}-尝试获取任意可用的 Web 账号")
    remaining_timeout = timeout

    while remaining_timeout > 0:
        for account in _web_accounts.values():
            if not account.lock.locked():
                try:
                    acquire_timeout = remaining_timeout
                    await asyncio.wait_for(account.lock.acquire(), timeout=acquire_timeout)
                    logger.debug(f"{seqid}-🔒🔴 <{account.uid}>")
                except asyncio.TimeoutError:
                    logger.debug(f"{seqid}-🔒⌛️ <{account.uid}>")
                    continue
                return account

        await asyncio.sleep(0.2)
        elapsed = loop.time() - start_time
        remaining_timeout = timeout - elapsed

    logger.error(f"{seqid}-🔒⌛️ 没有可用的 Web 账号")
    raise asyncio.TimeoutError(f"{seqid}-获取 Web 账号超时")


async def _validate_and_update_account(seqid: str, web_account: WebAccount) -> WebAccount | None:
    if web_account.uid > 100 and not await web_account.check_alive():
        if web_account.cookie_cloud:
            logger.error(f"{seqid}-Web 账号 <{web_account.uid}> 已失效, 尝试从 Cookie Cloud 更新")
            cookies = await web_account.cookie_cloud.get_cookie()
            web_account.update(cookies)
            if not await web_account.check_alive():
                logger.error(f"{seqid}-Web 账号 <{web_account.uid}> 更新后仍然失效, 释放锁并删除")
                await _remove_account(seqid, web_account)
                return None
        else:
            logger.error(f"{seqid}-Web 账号 <{web_account.uid}> 已失效, 释放锁并删除")
            await _remove_account(seqid, web_account)
            return None
    return web_account


async def _remove_account(seqid: str, web_account: WebAccount) -> None:
    web_account.lock.release()
    web_account.remove()
    logger.debug(f"{seqid}-Web 账号 <{web_account.uid}> 已删除")


_web_accounts: dict[int, WebAccount] = {}


def load_all_web_accounts():
    for file_path in data_path.joinpath("auth").glob("web_*.json"):
        logger.info(f"正在从 {file_path} 加载 Web 账号")
        auth_json: list[dict[str, Any]] | dict[str, Any] = json.loads(Path(file_path).read_text(encoding="utf-8"))
        account = WebAccount.load_from_json(auth_json)
        _web_accounts[account.uid] = account
    for cloud_config in config.cookie_clouds:
        logger.info(f"正在从 Cookie Cloud {cloud_config.uuid} 加载 Web 账号")
        cloud = PyCookieCloud(cloud_config.url, cloud_config.uuid, cloud_config.password)
        cookies = cloud.get_cookie_sync()
        account = WebAccount(
            uid=cookies["DedeUserID"],  # type: ignore
            cookies=cookies,
            cookies_cloud=cloud,
            note={"create_time": datetime.now(tz=tz).isoformat(timespec="seconds"), "source": cloud_config.url},
        )
        _web_accounts[account.uid] = account
    logger.info(f"已加载 {len(_web_accounts)} 个 Web 账号")


load_all_web_accounts()
