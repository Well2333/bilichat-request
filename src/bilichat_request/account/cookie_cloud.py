from typing import Any

from loguru import logger

from ..functions.cookie_cloud import PyCookieCloud
from .base import Note, RecoverableWebAccount


class CCWebAccount(RecoverableWebAccount):
    """Cookie Cloud Web账号"""

    type: str = "CookieCloud"
    cookie_cloud: PyCookieCloud

    def __init__(
        self,
        uid: str | int,
        cookies: dict[str, Any],
        cookie_cloud: PyCookieCloud,
        note: Note | None = None,
    ) -> None:
        super().__init__(uid, cookies, note)
        self.cookie_cloud = cookie_cloud
        logger.success(
            f"CookieCloud Web 账号 {self.uid} (UUID: {self.cookie_cloud.uuid}) 已加载, 来源: {self.note.get('source', '')}"
        )

    def _get_dump_cookies(self) -> dict[str, Any]:
        """获取用于导出的cookies信息"""
        return {
            "url": self.cookie_cloud.url,
            "uuid": self.cookie_cloud.uuid,
            "password": self.cookie_cloud.password,
        }

    def _on_cookies_updated(self) -> None:
        """cookies更新后的处理 - CookieCloud账号不保存到本地文件"""

    async def recover(self) -> bool:
        """尝试恢复账号"""
        try:
            new_cookies = await self.cookie_cloud.get_cookie()
            self.update(new_cookies)

            # 重新验证账号
            if await self.check_alive():
                logger.success(f"CookieCloud 账号 <{self.uid}> 恢复成功")
                self.available = True
                return True
            else:
                logger.error(f"CookieCloud 账号 <{self.uid}> 刷新cookies后仍然失效")
                self.available = False
                return False

        except Exception as e:
            logger.error(f"CookieCloud 账号 <{self.uid}> 恢复失败: {e}")
            self.available = False
            return False

    @classmethod
    def load_from_cookiecloud(cls, cloud: PyCookieCloud) -> "CCWebAccount":
        """从CookieCloud加载账号"""
        cookies = cloud.get_cookie_sync()
        return cls(
            uid=str(cookies["DedeUserID"]),
            cookies=cookies,
            cookie_cloud=cloud,
            note={"create_time": None, "source": cloud.url},
        )
