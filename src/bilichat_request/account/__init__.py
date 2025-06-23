import asyncio
import contextlib
import itertools
import json
import random
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from loguru import logger

from bilichat_request.compat import scheduler

from ..config import config, tz
from ..const import data_path
from ..functions.cookie_cloud import PyCookieCloud
from .base import BaseWebAccount, RecoverableWebAccount, TemporaryWebAccount
from .cookie_cloud import CCWebAccount
from .normal import NormalWebAccount

_seqid_generator = itertools.count(0)
_background_tasks: set[asyncio.Task[Any]] = set()


class WebAccountManager:
    """Web账号管理器"""

    def __init__(self) -> None:
        self._accounts: dict[int, BaseWebAccount] = {}

    @property
    def accounts(self) -> dict[int, BaseWebAccount]:
        """获取所有账号"""
        return self._accounts

    @property
    def available_accounts(self) -> list[BaseWebAccount]:
        """获取所有可用账号"""
        return [acc for acc in self._accounts.values() if acc.available]

    def load_all_accounts(self) -> None:
        """加载所有Web账号"""
        # 加载本地文件中的普通账号
        auth_dir = data_path.joinpath("auth")
        if auth_dir.exists():
            for file_path in auth_dir.glob("web_*.json"):
                logger.info(f"正在从 {file_path} 加载普通 Web 账号")
                try:
                    auth_json: dict[str, Any] = json.loads(file_path.read_text(encoding="utf-8"))
                    account = NormalWebAccount.load_from_json(auth_json)
                    self.add_account(account)
                except Exception as e:
                    logger.error(f"加载账号文件 {file_path} 失败: {e}")

        # 加载CookieCloud账号
        for cloud_config in config.cookie_clouds:
            logger.info(f"正在从 Cookie Cloud {cloud_config.uuid} 加载 Web 账号")
            try:
                cloud = PyCookieCloud(cloud_config.url, cloud_config.uuid, cloud_config.password)
                account = CCWebAccount.load_from_cookiecloud(cloud)
                self.add_account(account)
            except Exception as e:
                logger.error(f"从 Cookie Cloud {cloud_config.uuid} 加载账号失败: {e}")

        account_info = "\n* ".join(acc.info_str for acc in self._accounts.values())
        logger.info(f"已加载 {len(self._accounts)} 个 Web 账号: \n* {account_info}")

    def add_account(self, account: BaseWebAccount) -> None:
        """添加账号到管理器"""
        self._accounts[account.uid] = account

    def remove_account(self, uid: int) -> bool:
        """从管理器中移除账号"""
        if uid in self._accounts:
            self._accounts[uid].remove()
            if not isinstance(self._accounts[uid], RecoverableWebAccount):
                del self._accounts[uid]
            return True
        return False

    async def acquire_account(self, seqid: str) -> BaseWebAccount:
        logger.debug(f"{seqid}-尝试获取账号")

        while True:
            accounts = self.available_accounts
            random.shuffle(accounts)

            for account in accounts:
                if not account.lock.locked():
                    # 尝试锁定账号
                    try:
                        await asyncio.wait_for(account.lock.acquire(), timeout=0.1)
                        logger.debug(f"{seqid}-🔒账号锁定 <{account.uid}>")
                    except asyncio.TimeoutError:
                        logger.debug(f"{seqid}-🔴获取超时 <{account.uid}>")
                        continue
                    # 检查是否可用
                    if not await account.check_alive():
                        if isinstance(account, RecoverableWebAccount):
                            task = asyncio.create_task(account.recover())
                            _background_tasks.add(task)
                            task.add_done_callback(_background_tasks.discard)
                        continue
                    # 账号可用, 返回
                    return account

            await asyncio.sleep(0.2)


# 创建全局账号管理器实例
account_manager = WebAccountManager()


@contextlib.asynccontextmanager
async def get_web_account() -> AsyncIterator[BaseWebAccount]:
    seqid = f"{next(_seqid_generator) % 1000:03}"
    logger.debug(f"{seqid}-开始获取 Web 账号。")

    web_account: BaseWebAccount | None = None

    try:
        # 获取并锁定账号
        # 如果没有任何可用账号, 创建临时账号
        if not account_manager.available_accounts:
            logger.debug(f"{seqid}-没有任何可用账号, 正在创建临时 Web 账号, 可能会受到风控限制")
            web_account = TemporaryWebAccount()
            await web_account.lock.acquire()
            logger.debug(f"{seqid}-🔒账号锁定 <{web_account.uid}>")
        # 有可用的账号, 获取账号
        else:
            web_account = await account_manager.acquire_account(seqid)
        # 账号出库使用
        st = datetime.now(tz=tz)
        logger.info(f"{seqid}-⬆️ 账号出库 <{web_account.uid}>")
        yield web_account
        logger.info(f"{seqid}-⬇️ 账号回收 <{web_account.uid}> 总耗时: {(datetime.now(tz=tz) - st).total_seconds()}s")

    finally:
        # 解锁并清理账号资源
        if web_account and web_account.lock.locked():
            web_account.lock.release()
            logger.debug(f"{seqid}-🟢账号解锁 <{web_account.uid}>")


@scheduler.scheduled_job("interval", seconds=config.account_recover_interval)
async def recover_accounts() -> None:
    """恢复账号"""
    for account in account_manager.accounts.values():
        if isinstance(account, RecoverableWebAccount) and not account.available:
            await account.recover()


# 初始化时加载所有账号
account_manager.load_all_accounts()

__all__ = [
    "BaseWebAccount",
    "CCWebAccount",
    "NormalWebAccount",
    "account_manager",
    "get_web_account",
]
