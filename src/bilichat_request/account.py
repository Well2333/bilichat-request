import asyncio
import contextlib
import json
import random
import time
from asyncio import Lock
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger
from typing_extensions import TypedDict

from .adapters.web import WebRequester
from .config import config, data_path, tz
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
        if self.uid <= 10:
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


@contextlib.asynccontextmanager
async def get_web_account(account_uid: int | None = None):
    st = time.time()
    if account_uid:  # 如果传入 account_uid
        web_account = _web_accounts.get(account_uid)
        if not web_account:
            raise ValueError(f"Web 账号 <{account_uid}> 不存在")
        while web_account.lock.locked():
            if time.time() - st > 10:
                raise asyncio.TimeoutError(f"获取 Web 账号 {web_account} 超时")
            await asyncio.sleep(0.2)
        await web_account.lock.acquire()
    elif _web_accounts:
        while True:
            if time.time() - st > 10:
                raise asyncio.TimeoutError("获取 Web 账号超时")
            try:
                web_account = next(iter(_web_accounts.values()))
                if not web_account.lock.locked():
                    await web_account.lock.acquire()
                    break
            except StopIteration:
                await asyncio.sleep(0.2)
    else:
        web_account = WebAccount(random.randint(1, 10), {})
        await web_account.lock.acquire()

    if web_account.uid > 10:
        await web_account.check_alive()
    else:
        logger.warning(f"Web 账号 <{web_account.uid}> 为未登录账号, 请求可能会风控")
    logger.trace(f"锁定 <{web_account.uid}>")
    try:
        yield web_account
    finally:
        web_account.lock.release()
        logger.trace(f"解锁 <{web_account.uid}>")


_web_accounts: dict[int, WebAccount] = {}

load_all_web_accounts()
