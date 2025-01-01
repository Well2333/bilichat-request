from typing_extensions import TypedDict


class LevelInfo(TypedDict):
    """Contains user level information."""

    current_level: int  # 当前等级
    current_min: int  # 作用尚不明确
    current_exp: int  # 作用尚不明确
    next_exp: int  # 作用尚不明确


class Pendant(TypedDict):
    """Contains information about the user's pendant."""

    pid: int  # 挂件id
    name: str  # 挂件名称
    image: str  # 挂件图片url
    expire: int  # 作用尚不明确


class Nameplate(TypedDict):
    """Contains information about the user's nameplate."""

    nid: int  # 勋章id
    name: str  # 勋章名称
    image: str  # 勋章图片url (正常)
    image_small: str  # 勋章图片url (小)
    level: str  # 勋章等级
    condition: str  # 勋章条件


class Official(TypedDict):
    """Contains official verification information."""

    role: int  # 认证类型
    title: str  # 认证信息
    desc: str  # 认证备注
    type: int  # 是否认证


class OfficialVerify(TypedDict):
    """Contains official verification status."""

    type: int  # 是否认证
    desc: str  # 认证信息


class VipLabel(TypedDict):
    """Contains the VIP label information."""

    path: str  # 标签路径
    text: str  # 标签文字
    label_theme: str  # 标签主题
    text_color: str  # 文字颜色
    bg_style: int  # 背景样式
    bg_color: str  # 背景颜色
    border_color: str  # 边框颜色


class Vip(TypedDict):
    """Contains VIP information."""

    type: int  # 大会员类型
    status: int  # 大会员状态
    due_date: int  # 会员到期时间
    vip_pay_type: int  # 会员支付类型
    theme_type: int  # 主题类型
    label: VipLabel  # 标签信息
    avatar_subscript: int  # 是否有小图标
    nickname_color: str  # 昵称颜色
    role: int  # 用户角色
    avatar_subscript_url: str  # 小图标URL
    vipType: int  # 大会员类型
    vipStatus: int  # 大会员状态


class Card(TypedDict):
    """Contains the user profile information."""

    mid: str  # 用户mid
    approve: bool  # 作用尚不明确
    name: str  # 用户昵称
    sex: str  # 用户性别
    face: str  # 用户头像链接
    DisplayRank: str  # 作用尚不明确
    regtime: int  # 作用尚不明确
    spacesta: int  # 用户状态
    birthday: str  # 作用尚不明确
    place: str  # 作用尚不明确
    description: str  # 作用尚不明确
    article: int  # 作用尚不明确
    attentions: list[str]  # 作用尚不明确
    fans: int  # 粉丝数
    friend: int  # 关注数
    attention: int  # 关注数
    sign: str  # 用户签名
    level_info: LevelInfo  # 用户等级信息
    pendant: Pendant  # 用户挂件信息
    nameplate: Nameplate  # 用户勋章信息
    Official: Official  # 用户认证信息
    official_verify: OfficialVerify  # 用户认证信息2
    vip: Vip  # 大会员状态
    space: dict  # 主页头图


class Data(TypedDict):
    """Contains the main data of the response."""

    card: Card  # 卡片信息
    following: bool  # 是否关注此用户
    archive_count: int  # 用户稿件数
    article_count: int  # 作用尚不明确
    follower: int  # 粉丝数
    like_num: int  # 点赞数
