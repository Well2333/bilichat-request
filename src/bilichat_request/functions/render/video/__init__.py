from datetime import datetime
from io import BytesIO
from typing import TYPE_CHECKING, ClassVar

from httpx import AsyncClient

from bilichat_request.account import get_web_account
from bilichat_request.config import config, tz
from bilichat_request.exceptions import NotFindAbortError, ResponseCodeError

if TYPE_CHECKING:
    from .model.card import Data as CardData
    from .model.video import Data as VideoData


def num_fmt(num: int):
    if num < 10000:
        return str(num)
    elif num < 100000000:
        return ("%.2f" % (num / 10000)) + "万"
    else:
        return ("%.2f" % (num / 100000000)) + "亿"


class UP:
    def __init__(
        self,
        name: str,
        face: bytes | BytesIO,
        level: int,
        fans: str,
        video_counts: int,
        title: str = "UP主",
        name_color: str = "black",
        official_verify: int = -1,
    ) -> None:
        self.name: str = name
        """UP名"""
        self.face: BytesIO = face if isinstance(face, BytesIO) else BytesIO(face)
        """UP头像"""
        self.level: int = level
        """UP等级"""
        self.name_color: str = name_color or "black"
        """UP名字颜色"""
        self.fans: str = fans
        """粉丝数"""
        self.video_counts: int = video_counts
        """视频投稿数量"""
        self.title: str = title
        """合作视频中的角色"""
        self.official_verify: int = official_verify
        """小闪电认证: -1 为无, 0 为个人, 1 为企业"""

    @classmethod
    async def from_card(cls, card: dict, title: str = "UP主") -> "UP":  # type: ignore
        card: CardData
        name = card["card"]["name"]
        bg_color = card["card"]["vip"]["nickname_color"] or "black"
        level = card["card"]["level_info"]["current_level"]
        video_counts = card["archive_count"]
        official_verify = card["card"]["official_verify"]["type"]
        face_req = await AsyncClient(follow_redirects=True).get(card["card"]["face"])
        if face_req.status_code == 404:
            face_req = await AsyncClient(follow_redirects=True).get("https://i0.hdslb.com/bfs/face/member/noface.jpg")
        face = face_req.content
        return cls(
            name=name,
            name_color=bg_color,
            level=level,
            face=face,
            fans=num_fmt(card["follower"]),
            video_counts=video_counts,
            title=title,
            official_verify=official_verify,
        )


class VideoImage:
    _render_methods: ClassVar[dict] = {}

    def __init__(
        self,
        cover: bytes | BytesIO,
        duration: int,
        type_name: str,
        title: str,
        view: str,
        danmaku: str,
        favorite: str,
        coin: str,
        like: str,
        reply: str,
        share: str,
        pubdate: datetime,
        uploaders: list[UP],
        b23_url: str,
        aid: str,
        desc: str | None = None,
    ) -> None:
        self.cover: BytesIO = cover if isinstance(cover, BytesIO) else BytesIO(cover)
        """视频封面"""
        minutes, self.seconds = divmod(duration, 60)
        self.hours, self.minutes = divmod(minutes, 60)
        self.type_name: str = type_name
        """视频分区"""
        self.title: str = title
        """视频标题"""
        self.desc: str = desc or "该视频没有简介"
        """视频简介"""
        self.view: str = view
        """播放量"""
        self.danmaku: str = danmaku
        """弹幕数"""
        self.favorite: str = favorite
        """收藏"""
        self.coin: str = coin
        """投币"""
        self.like: str = like
        """点赞"""
        self.reply: str = reply
        """评论"""
        self.share: str = share
        """分享"""
        self.pubdate: datetime = pubdate
        """发布时间"""
        self.uploaders: list[UP] = uploaders
        """up主列表"""
        self.b23_url: str = b23_url
        """b23短链"""
        self.aid: str = aid
        """av号"""

    @classmethod
    async def get(
        cls,
        video_id: str | int,
        b23_url: str | None = None,
        retry: int = config.retry,
    ) -> "VideoImage":
        try:
            async with get_web_account() as account:
                data: VideoData = await account.web_requester.get_video_info(video_id)  # type: ignore
        except ResponseCodeError as e:
            if e.code == -404:
                raise NotFindAbortError(f"找不到视频 {video_id}") from e
            if retry:
                return await cls.get(video_id, b23_url, retry - 1)
            raise
        b23_url = b23_url or await account.web_requester.get_b23_url(data["bvid"])
        # 获取封面
        async with AsyncClient() as client:
            client.headers.update(
                {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
                    ),
                    "origin": "https://www.bilibili.com",
                    "referer": f"https://www.bilibili.com/video/{data['bvid']}",
                }
            )
            # 封面
            cover_bytes = (await client.get(data["pic"])).content
            # up列表
            ups = []
            # 合作视频(UP在第一个)
            if staffs := data.get("staff"):
                ups.extend(
                    [
                        await UP.from_card(await account.web_requester.get_user_card(staff["mid"]), staff["title"])
                        for staff in staffs
                    ]
                )

            # 单人视频
            else:
                ups.append(
                    await UP.from_card(
                        await account.web_requester.get_user_card(data["owner"]["mid"]),
                    )
                )

        return cls(
            cover=cover_bytes,
            duration=data["duration"],
            type_name=data["tname"],
            title=data["title"],
            desc=data["desc"],
            view=num_fmt(data["stat"]["view"]),
            danmaku=num_fmt(data["stat"]["danmaku"]),
            favorite=num_fmt(data["stat"]["favorite"]),
            coin=num_fmt(data["stat"]["coin"]),
            like=num_fmt(data["stat"]["like"]),
            reply=num_fmt(data["stat"]["reply"]),
            share=num_fmt(data["stat"]["share"]),
            pubdate=datetime.fromtimestamp(data["pubdate"], tz=tz),
            uploaders=ups,
            b23_url=b23_url,
            aid=f"av{data['aid']}",
        )

    @staticmethod
    def get_up_level_code(level: int) -> tuple[str, tuple[int, int, int]]:
        if level == 0:
            up_level = "\ue6cb"
            level_color = (191, 191, 191)
        elif level == 1:
            up_level = "\ue6cc"
            level_color = (191, 191, 191)
        elif level == 2:
            up_level = "\ue6cd"
            level_color = (149, 221, 178)
        elif level == 3:
            up_level = "\ue6ce"
            level_color = (146, 209, 229)
        elif level == 4:
            up_level = "\ue6cf"
            level_color = (255, 179, 124)
        elif level == 5:
            up_level = "\ue6d0"
            level_color = (255, 108, 0)
        else:
            up_level = "\ue6d1"
            level_color = (255, 0, 0)
        return up_level, level_color
