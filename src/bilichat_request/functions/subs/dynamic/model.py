from enum import Enum

from pydantic import BaseModel


class DynamicType(str, Enum):
    NONE = "DYNAMIC_TYPE_NONE"
    """无效动态"""

    FORWARD = "DYNAMIC_TYPE_FORWARD"
    """动态转发, 通常关联原始动态的ID"""

    AV = "DYNAMIC_TYPE_AV"
    """投稿视频, 包含视频的AV号"""

    PGC = "DYNAMIC_TYPE_PGC"
    """剧集 (番剧、电影、纪录片) , 通常关联某一剧集的分集AV号"""

    COURSES = "DYNAMIC_TYPE_COURSES"
    """课程, 通常用于与学习平台相关的内容"""

    WORD = "DYNAMIC_TYPE_WORD"
    """纯文字动态, 通常包含动态ID"""

    DRAW = "DYNAMIC_TYPE_DRAW"
    """带图动态, 通常包含相册ID"""

    ARTICLE = "DYNAMIC_TYPE_ARTICLE"
    """投稿专栏, 通常包含专栏的CV号"""

    MUSIC = "DYNAMIC_TYPE_MUSIC"
    """音乐, 具体内容未明确"""

    COMMON_SQUARE = "DYNAMIC_TYPE_COMMON_SQUARE"
    """装扮、剧集点评、普通分享, 涉及个人装扮、剧集点评或其他普通分享"""

    COMMON_VERTICAL = "DYNAMIC_TYPE_COMMON_VERTICAL"
    """未指定类型, 可能是系统内其他类型的占位符"""

    LIVE = "DYNAMIC_TYPE_LIVE"
    """直播间分享, 通常包含直播间ID"""

    MEDIALIST = "DYNAMIC_TYPE_MEDIALIST"
    """收藏夹, 通常包含收藏夹的ML号"""

    COURSES_SEASON = "DYNAMIC_TYPE_COURSES_SEASON"
    """课程季节, 通常包含课程的ID"""

    COURSES_BATCH = "DYNAMIC_TYPE_COURSES_BATCH"
    """未指定类型, 可能是系统内其他类型的占位符"""

    AD = "DYNAMIC_TYPE_AD"
    """广告, 具体内容未明确"""

    APPLET = "DYNAMIC_TYPE_APPLET"
    """小程序, 具体内容未明确"""

    SUBSCRIPTION = "DYNAMIC_TYPE_SUBSCRIPTION"
    """订阅类型的动态, 通常与用户的订阅行为有关"""

    LIVE_RCMD = "DYNAMIC_TYPE_LIVE_RCMD"
    """直播开播, 通常包含直播的ID"""

    BANNER = "DYNAMIC_TYPE_BANNER"
    """横幅类型的动态, 通常用于宣传或展示"""

    UGC_SEASON = "DYNAMIC_TYPE_UGC_SEASON"
    """合集更新, 通常与视频内容的AV号相关"""

    SUBSCRIPTION_NEW = "DYNAMIC_TYPE_SUBSCRIPTION_NEW"
    """新的订阅动态, 具体内容未明确"""


class Dynamic(BaseModel):
    dyn_id: int
    """动态id"""
    dyn_type: DynamicType
    """动态类型"""
    dyn_timestamp: int
    """动态发布时间"""


CARD_TYPE_MAP: dict[int, DynamicType] = {
    1: DynamicType.FORWARD,
    2: DynamicType.DRAW,
    4: DynamicType.WORD,
    8: DynamicType.AV,
    64: DynamicType.ARTICLE,
    256: DynamicType.MUSIC,
    512: DynamicType.PGC,
    2048: DynamicType.COMMON_SQUARE,
}  # https://github.com/SocialSisterYi/bilibili-API-collect/issues/143
