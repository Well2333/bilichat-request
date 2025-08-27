import contextlib
import itertools
import json
import random
from collections.abc import AsyncIterator
from typing import Any

from loguru import logger

from bilichat_request.compat import scheduler

from ..config import config
from ..const import data_path
from ..exceptions import ResponseCodeError
from ..functions.cookie_cloud import PyCookieCloud
from .base import BaseWebAccount, RecoverableWebAccount, TemporaryWebAccount
from .cookie_cloud import CCWebAccount
from .normal import NormalWebAccount

_seqid_generator = itertools.count(0)

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
            account = self._accounts[uid]
            if isinstance(account, RecoverableWebAccount):
                account.available = False
            elif isinstance(account, NormalWebAccount):
                account.remove()
                del self._accounts[uid]
            elif isinstance(account, TemporaryWebAccount):
                del self._accounts[uid]
            return True
        return False


account_manager = WebAccountManager()


@contextlib.asynccontextmanager
async def get_web_account() -> AsyncIterator[BaseWebAccount]:
    seqid = f"{next(_seqid_generator) % 1000:03}"
    if not account_manager.available_accounts:
        logger.debug(f"{seqid}-没有任何可用账号, 正在创建临时 Web 账号, 可能会受到风控限制")
        account = TemporaryWebAccount()
    else:
        account = random.choice(account_manager.available_accounts)
    logger.info(f"{seqid}-获取账号 <{account.uid}>")

    try:
        yield account
    except ResponseCodeError as e:
        if e.code == -101 and not await account.check_alive():
            account_manager.remove_account(account.uid)
        raise
    finally:
        if isinstance(account, TemporaryWebAccount):
            account_manager.remove_account(account.uid)


@scheduler.scheduled_job("interval", seconds=config.account_recover_interval)
async def handle_unavailable_accounts() -> None:
    """处理不可用账号"""
    for account in account_manager.accounts.values():
        if not account.available:
            if isinstance(account, RecoverableWebAccount):
                await account.recover()
            else:
                account_manager.remove_account(account.uid)


account_manager.load_all_accounts()

__all__ = [
    "BaseWebAccount",
    "CCWebAccount",
    "NormalWebAccount",
    "account_manager",
    "get_web_account",
]
