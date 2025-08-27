import json
from pathlib import Path
from typing import Any

from loguru import logger

from ..const import data_path
from .base import BaseWebAccount, Note


class NormalWebAccount(BaseWebAccount):
    """普通Web账号"""

    type: str = "Normal"
    file_path: Path

    def __init__(
        self,
        uid: str | int,
        cookies: dict[str, Any],
        note: Note | None = None,
    ) -> None:
        super().__init__(uid, cookies, note)
        self.file_path = data_path / "auth" / f"web_{self.uid}.json"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.save()
        logger.success(f"普通 Web 账号 {self.uid} 已加载, 来源: {self.note.get('source', '')}")

    def _get_dump_cookies(self) -> dict[str, Any]:
        return self.cookies

    def _on_cookies_updated(self) -> None:
        self.save()

    def save(self) -> None:
        """保存账号到本地文件"""
        self.file_path.write_text(
            json.dumps(
                {
                    "uid": self.uid,
                    "cookies": self._get_dump_cookies(),
                    "note": self.note,
                },
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def remove(self) -> None:
        """删除账号本地文件"""
        if self.file_path.exists():
            self.file_path.unlink()

        logger.info(f"普通 Web 账号 {self.uid} 已删除")

    @classmethod
    def load_from_json(cls, auth_json: dict[str, Any]) -> "NormalWebAccount":
        """从JSON数据加载普通账号"""
        # 直接使用字典数据创建账号
        if "DedeUserID" not in auth_json.get("cookies", {}):
            raise DeprecationWarning("可重置的账号(如CookieCloud账号)已不支持此途径添加, 请在config.yaml中配置")
        return cls(**auth_json)

    @classmethod
    def load_from_cookies(cls, cookies: dict[str, Any], note: Note | None = None) -> "NormalWebAccount":
        """从cookies直接创建账号"""
        if "DedeUserID" not in cookies:
            raise ValueError("cookies中缺少DedeUserID字段")

        return cls(
            uid=cookies["DedeUserID"],
            cookies=cookies,
            note=note,
        )
