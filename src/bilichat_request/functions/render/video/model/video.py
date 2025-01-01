from typing_extensions import TypedDict


class Vip(TypedDict):
    """
    成员的大会员状态。
    """

    type: int  # 成员会员类型, 0: 无, 1: 月会员, 2: 年会员
    status: int  # 会员状态, 0: 无, 1: 有
    due_date: int  # 到期时间, UNIX 毫秒时间戳
    vip_pay_type: int  # 会员支付类型, 作用尚不明确
    theme_type: int  # 会员主题类型, 通常为0
    label: dict[str, str] | None  # 会员标签信息, 作用尚不明确


class Official(TypedDict):
    """
    成员的官方认证信息。
    """

    role: int  # 成员认证级别, 参考[用户认证类型一览](../user/official_role.md)
    title: str  # 成员认证名, 若没有则为空
    desc: str  # 成员认证备注, 若没有则为空
    type: int  # 成员认证类型, -1: 无, 0: 有认证


class StaffMember(TypedDict):
    """
    合作成员的信息。
    """

    mid: int  # 成员mid
    title: str  # 成员名称
    name: str  # 成员昵称
    face: str  # 成员头像url
    vip: Vip  # 成员大会员状态
    official: Official  # 成员认证信息
    follower: int  # 成员粉丝数
    label_style: int | None  # 作用尚不明确, 具体含义不清楚


class HonorReply(TypedDict):
    """
    包含当前稿件的荣誉回馈信息。
    """

    honor: list[dict[str, str | None]]


class SubtitleAuthor(TypedDict):
    """
    字幕上传者信息。
    """

    mid: int  # 字幕上传者mid
    name: str  # 字幕上传者昵称
    sex: str  # 字幕上传者性别, 值为'男', '女', '保密'
    face: str  # 字幕上传者头像url
    sign: str  # 字幕上传者签名
    rank: int  # 会员等级, 作用尚不明确
    birthday: int  # 生日, 作用尚不明确
    is_fake_account: int  # 是否为假账号, 作用尚不明确
    is_deleted: int  # 是否已删除, 作用尚不明确


class SubtitlelistItem(TypedDict):
    """
    字幕列表中的单个字幕项。
    """

    id: int  # 字幕id
    lan: str  # 字幕语言
    lan_doc: str  # 字幕语言名称
    is_lock: bool  # 是否锁定
    author_mid: int  # 字幕上传者mid
    subtitle_url: str  # json格式字幕文件url
    author: SubtitleAuthor  # 字幕上传者信息


class Subtitle(TypedDict):
    """
    字幕信息对象, 包括是否允许提交字幕及字幕列表。
    """

    allow_submit: bool  # 是否允许提交字幕
    list: list[SubtitlelistItem]  # 字幕列表


class Dimension(TypedDict):
    """
    视频分辨率信息, 包括宽度、高度和旋转信息。
    """

    width: int  # 分辨率宽度
    height: int  # 分辨率高度
    rotate: int  # 旋转标志, 0表示正常, 1表示对换宽高


class Page(TypedDict):
    """
    视频的分P信息。
    """

    cid: int  # 分P cid
    page: int  # 分P序号, 从1开始
    from_: str  # 视频来源, vupload: 普通上传, hunan: 芒果TV, qq: 腾讯
    part: str  # 分P标题
    duration: int  # 分P持续时间, 单位为秒
    vid: str | None  # 站外视频vid, 只有站外视频有效
    weblink: str | None  # 站外视频跳转url, 只有站外视频有效
    dimension: Dimension | None  # 当前分P分辨率, 部分较老视频无分辨率值


class Rights(TypedDict):
    """
    视频的属性标志。
    """

    bp: int  # 是否允许承包
    elec: int  # 是否支持充电
    download: int  # 是否允许下载
    movie: int  # 是否电影
    pay: int  # 是否PGC付费
    hd5: int  # 是否有高码率
    no_reprint: int  # 是否显示“禁止转载”标志
    autoplay: int  # 是否自动播放
    ugc_pay: int  # 是否UGC付费
    is_cooperation: int  # 是否为联合投稿
    ugc_pay_preview: int  # 作用尚不明确
    no_background: int  # 作用尚不明确
    clean_mode: int  # 作用尚不明确
    is_stein_gate: int  # 是否为互动视频
    is_360: int  # 是否为全景视频
    no_share: int  # 作用尚不明确
    arc_pay: int  # 作用尚不明确
    free_watch: int  # 作用尚不明确


class Owner(TypedDict):
    """
    视频UP主信息。
    """

    mid: int  # UP主mid
    name: str  # UP主昵称
    face: str  # UP主头像url


class Stat(TypedDict):
    """
    视频的统计信息。
    """

    aid: int  # 稿件avid
    view: int  # 播放数
    danmaku: int  # 弹幕数
    reply: int  # 评论数
    favorite: int  # 收藏数
    coin: int  # 投币数
    share: int  # 分享数
    now_rank: int  # 当前排名
    his_rank: int  # 历史最高排名
    like: int  # 获赞数
    dislike: int  # 点踩数, 恒为0
    evaluation: str  # 视频评分
    vt: int  # 作用尚不明确, 恒为0


class Data(TypedDict):
    """
    视频信息本体。
    """

    bvid: str  # 稿件bvid
    aid: int  # 稿件avid
    videos: int  # 稿件分P总数
    tid: int  # 分区tid
    tname: str  # 子分区名称
    copyright: int  # 视频类型
    pic: str  # 稿件封面图片url
    title: str  # 稿件标题
    pubdate: int  # 稿件发布时间, 秒级时间戳
    ctime: int  # 用户投稿时间, 秒级时间戳
    desc: str  # 视频简介
    desc_v2: list[dict[str, int]]  # 新版视频简介
    state: int  # 视频状态
    duration: int  # 稿件总时长, 单位为秒
    forward: int | None  # 撞车视频跳转avid, 仅撞车视频存在此字段
    mission_id: int | None  # 稿件参与的活动id
    redirect_url: str | None  # 重定向url, 仅番剧或影视视频存在此字段
    rights: Rights  # 视频属性标志
    owner: Owner  # 视频UP主信息
    stat: Stat  # 视频状态数
    dynamic: str  # 视频同步发布的动态文字内容
    cid: int  # 视频1P cid
    dimension: Dimension  # 视频1P分辨率
    premiere: None  # 为空
    teenage_mode: int | None  # 用于青少年模式
    is_chargeable_season: bool | None  # 是否可收费季节
    is_story: bool | None  # 是否在Story Mode展示
    is_upower_exclusive: bool | None  # 是否为充电专属
    is_upower_pay: bool | None  # 作用尚不明确
    is_upower_show: bool | None  # 作用尚不明确
    no_cache: bool | None  # 是否不允许缓存
    pages: list[Page]  # 视频分P列表
    subtitle: Subtitle  # 视频CC字幕信息
    staff: list[StaffMember] | None  # 合作成员列表
    is_season_display: bool | None  # 作用尚不明确
    user_garb: dict[str, str] | None  # 用户装扮信息
    honor_reply: HonorReply | None  # 荣誉回馈信息
    like_icon: str | None  # 空串
    need_jump_bv: bool | None  # 需要跳转到BV号?
    disable_show_up_info: bool | None  # 禁止展示UP主信息?
    is_story_play: bool | None  # 是否为Story Mode视频
    is_view_self: bool | None  # 是否为自己投稿的视频
    argue_info: dict[str, str] | None  # 争议/警告信息
