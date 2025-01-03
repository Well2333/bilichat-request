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

    def __init__(self, uid: str | int, cookies: dict[str, Any], note: Note | None = None) -> None:
        self.lock = Lock()
        self.uid = int(uid)
        self.cookies = cookies
        self.note = note or {
            "create_time": datetime.now(tz=tz).isoformat(timespec="seconds"),
            "source": "",
        }
        self.web_requester = WebRequester(cookies=self.cookies, update_callback=self.update)
        self.file_path = data_path / "auth" / f"web_{self.uid}.json"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.save()

    def dump(self, *, exclude_cookies: bool = False) -> dict[str, Any]:
        return {
            "uid": self.uid,
            "note": self.note,
            "cookies": self.cookies if not exclude_cookies else {},
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

    @classmethod
    def load_from_json(cls, json_path: str | Path) -> "WebAccount":
        auth_json: list[dict[str, Any]] | dict[str, Any] = json.loads(Path(json_path).read_text(encoding="utf-8"))
        if isinstance(auth_json, list):
            cookies = {}
            for auth_ in auth_json:
                cookies[auth_["name"]] = auth_["value"]
            return cls(
                uid=cookies["DedeUserID"],
                cookies=cookies,
            )
        elif isinstance(auth_json, dict):
            return cls(**auth_json)

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


def load_all_web_accounts():
    for file_path in data_path.joinpath("auth").glob("web_*.json"):
        logger.info(f"正在从 {file_path} 加载 Web 账号")
        account = WebAccount.load_from_json(file_path)
        _web_accounts[account.uid] = account
    logger.info(f"已加载 {len(_web_accounts)} 个 Web 账号")


_seqid_generator = itertools.count(1)


@contextlib.asynccontextmanager
async def get_web_account(account_uid: int | None = None):
    # 获取唯一的 seqid
    seqid = next(_seqid_generator)
    logger.debug(f"[{seqid}] 开始获取 Web 账号。传入的 account_uid={account_uid}")

    timeout = 10  # 超时时间为10秒
    loop = asyncio.get_running_loop()
    start_time = loop.time()

    web_account = None

    try:
        if account_uid is not None:
            logger.debug(f"[{seqid}] 尝试获取指定 UID 的 Web 账号: {account_uid}")
            web_account = _web_accounts.get(account_uid)
            if not web_account:
                logger.error(f"[{seqid}] Web 账号 <{account_uid}> 不存在")
                raise ValueError(f"Web 账号 <{account_uid}> 不存在")
            try:
                await asyncio.wait_for(web_account.lock.acquire(), timeout=timeout)
                logger.debug(f"[{seqid}] 🔒🔴 <{web_account.uid}>")
            except asyncio.TimeoutError:
                logger.error(f"[{seqid}] 🔒⌛️ <{web_account.uid}>")
                raise asyncio.TimeoutError(f"[{seqid}] 获取 Web 账号 <{web_account.uid}> 超时")  # noqa: B904

        elif _web_accounts:
            logger.debug(f"[{seqid}] 尝试获取任意可用的 Web 账号")
            elapsed = 0
            while elapsed < timeout:
                for account in _web_accounts.values():
                    if not account.lock.locked():
                        try:
                            remaining_time = timeout - elapsed
                            await asyncio.wait_for(account.lock.acquire(), timeout=remaining_time)
                            web_account = account
                            logger.debug(f"[{seqid}] 🔒🔴 <{web_account.uid}>")
                            break
                        except asyncio.TimeoutError:
                            logger.debug(f"[{seqid}] 🔒⌛️ <{account.uid}>")
                            continue
                if web_account:
                    break
                await asyncio.sleep(0.2)
                elapsed = loop.time() - start_time
            if not web_account:
                logger.error(f"[{seqid}] 🔒⌛️")
                raise asyncio.TimeoutError(f"[{seqid}] 获取 Web 账号超时")

        else:
            logger.debug(f"[{seqid}] 没有可用的 Web 账号, 正在创建临时 Web 账号, 可能会受到风控限制")
            new_uid = random.randint(1, 100)  # 根据实际需求调整UID范围
            web_account = WebAccount(new_uid, {})
            _web_accounts[new_uid] = web_account
            logger.debug(f"[{seqid}] 🔒🔴 <{web_account.uid}>")
            await web_account.lock.acquire()

        # 获取锁后进行账户状态检查
        if web_account.uid > 100:
            alive = await web_account.check_alive()
            if not alive:
                logger.error(f"[{seqid}] Web 账号 <{web_account.uid}> 已失效, 释放锁并删除")
                web_account.lock.release()
                del _web_accounts[web_account.uid]
                web_account = None
                # 重新获取账号
                async with get_web_account() as new_web_account:
                    yield new_web_account
                    return

        if web_account:
            yield web_account
    finally:
        if web_account:
            if web_account.lock.locked():
                web_account.lock.release()
                logger.debug(f"[{seqid}] 🔓🟢 <{web_account.uid}>")
            if web_account.uid <= 100:
                del _web_accounts[web_account.uid]
                logger.debug(f"[{seqid}] Web 账号 <{web_account.uid}> 已删除")


_web_accounts: dict[int, WebAccount] = {}

load_all_web_accounts()
