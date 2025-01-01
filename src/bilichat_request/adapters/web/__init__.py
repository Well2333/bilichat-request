import json
import re
import time
from collections.abc import Callable
from hashlib import md5
from typing import Any
from urllib.parse import urlencode

from httpx import AsyncClient
from httpx._types import URLTypes
from loguru import logger

from bilichat_request.config import config
from bilichat_request.exceptions import ResponseCodeError

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
        "Safari/537.36 Edg/114.0.1823.67"
    ),
    "Referer": "https://www.bilibili.com/",
}
APPKEY = "4409e2ce8ffd12b8"
APPSEC = "59b43e04ad6965f34319062b478f83dd"


class WebRequester:
    _salt = None

    def __init__(
        self,
        cookies: dict[str, Any],
        update_callback: Callable[[dict[str, Any]], bool],
        headers: dict[str, str] | None = None,
        **kwargs,
    ) -> None:
        self.client: AsyncClient = AsyncClient(follow_redirects=True, headers=DEFAULT_HEADERS, **kwargs)
        self.cookies = cookies
        self.update_callback = update_callback

        if headers:
            self.client.headers = headers

        # 需要初始化请求
        self._inited = False

    async def request(
        self,
        method: str,
        url: URLTypes,
        params: dict[str, Any] | None = None,
        retry: int = config.retry,
        *args,
        raw: bool = False,
        wbi: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        if params is None:
            params = {}
        if not self._inited:
            await self._init()
        if wbi:
            await self._sign_params(params)

        try:
            logger.trace(f"请求: {method} {url} {params}")
            resp = await self.client.request(method, url, params=params, cookies=self.cookies, *args, **kwargs)  # noqa: B026
            self.update_callback(dict(resp.cookies))
            resp.encoding = "utf-8"
            if resp.status_code == 200:
                raw_json: dict[str, Any] = resp.json()
            else:
                raise ResponseCodeError(
                    code=resp.status_code,
                    msg="请求失败",
                    data={"url": url, "params": params, "response": resp.text},
                )
            logger.trace(f"响应: {raw_json}")
            if raw:
                return raw_json
            if raw_json["code"] == -403:
                retry = retry - 1
                if retry < 0:
                    raise ResponseCodeError(
                        code=raw_json["code"],
                        msg=raw_json["message"],
                        data=raw_json.get("data", {}),
                    )
                self._salt = await self._get_salt()
                return await self.request(method, url, retry=retry, **kwargs)
            if raw_json["code"] != 0:
                raise ResponseCodeError(
                    code=raw_json["code"],
                    msg=raw_json["message"],
                    data=raw_json.get("data", {}),
                )
            return raw_json["data"]
        except Exception as e:
            logger.error(f"请求失败: {e}")
            raise

    async def get(
        self,
        url: URLTypes,
        params: dict[str, Any] | None = None,
        retry: int = config.retry,
        *args,
        raw: bool = False,
        wbi: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        if params is None:
            params = {}
        return await self.request("GET", url, params, retry, *args, raw=raw, wbi=wbi, **kwargs)

    async def post(
        self,
        url: URLTypes,
        params: dict[str, Any] | None = None,
        retry: int = config.retry,
        *args,
        raw: bool = False,
        wbi: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        if params is None:
            params = {}
        return await self.request("POST", url, params, retry, *args, raw=raw, wbi=wbi, **kwargs)

    async def _init(self) -> None:
        resp = await self.client.request(
            "GET",
            "https://data.bilibili.com/v/",
            follow_redirects=True,
        )
        self.update_callback(dict(resp.cookies))
        self._inited = True

    @staticmethod
    def _encrypt_params(params: dict[str, Any], local_id: int = 0) -> dict[str, Any]:
        params["local_id"] = local_id
        params["appkey"] = APPKEY
        params["ts"] = int(time.time())
        params["sign"] = md5(f"{urlencode(sorted(params.items()))}{APPSEC}".encode()).hexdigest()
        return params

    async def _get_salt(self) -> str:
        resp = await self.client.request(
            "GET",
            "https://api.bilibili.com/x/web-interface/nav",
            headers=DEFAULT_HEADERS,
        )
        self.update_callback(dict(resp.cookies))
        con = resp.json()
        img_url = con["data"]["wbi_img"]["img_url"]
        sub_url = con["data"]["wbi_img"]["sub_url"]
        re_rule = r"wbi/(.*?).png"
        img_key = "".join(re.findall(re_rule, img_url))
        sub_key = "".join(re.findall(re_rule, sub_url))
        n = img_key + sub_key
        array = list(n)
        # 注释fmt是为了阻止Black把下面的order格式化为更多行
        # fmt:off
        order = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39,
                12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63,
                57, 62, 11, 36, 20, 34, 44, 52]
        # fmt:on
        salt = "".join([array[i] for i in order])[:32]
        return salt

    async def _encrypt_w_rid(self, params: str | dict) -> tuple[str, str]:
        """传入参数字符串返回签名和时间tuple[w_rid,wts]
        -----------
        params:str格式: qn=32&fnver=0&fnval=4048&fourk=1&voice_balance=1&gaia_source=pre-load&avid=593238479&bvid=BV16q4y1k7mq&cid=486645610\n
        params:dict格式: {'qn': '32', 'fnver': '0', 'fnval': '4048', 'fourk': '1', 'voice_balance': '1', 'gaia_source': 'pre-load', 'avid': '593238479', 'bvid': 'BV16q4y1k7mq', 'cid': '486645610'}:
        """
        wts = str(int(time.time()))
        if isinstance(params, str):
            params_list = (params + "&wts=" + wts).split("&")
        elif isinstance(params, dict):
            params["wts"] = wts
            params_list = [f"{key}={value}" for key, value in params.items()]
        else:
            raise TypeError(f"invalid type of e:{type(params)}")
        params_list.sort()
        if self._salt is None:
            _salt = await self._get_salt()
        w_rid = md5(("&".join(params_list) + _salt).encode(encoding="utf-8")).hexdigest()
        return w_rid, wts

    async def _sign_params(self, params: dict[str, Any]) -> None:
        params.pop("w_rid", "")
        params.pop("wts", "")
        params["token"] = params.get("token", "")
        params["platform"] = params.get("platform", "web")
        params["web_location"] = params.get("web_location", 1550101)
        w_rid, wts = await self._encrypt_w_rid(params)
        params["w_rid"] = w_rid
        params["wts"] = wts

    # ================== 以下为API ==================

    async def get_b23_url(self, burl: str) -> str:
        """
        b23 链接转换

        Args:
            burl: 需要转换的 BiliBili 链接
        """
        if "/" not in burl:
            burl = "https://www.bilibili.com/" + burl
        url = "https://api.bilibili.com/x/share/click"
        data = {
            "build": 6700300,
            "buvid": 0,
            "oid": burl,
            "platform": "android",
            "share_channel": "COPY",
            "share_id": "public.webview.0.0.pv",
            "share_mode": 3,
        }
        resp = await self.post(url, data=data)
        return resp["content"]

    async def get_player(self, aid: int, cid: int):
        """
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/player.md#web-播放器信息
        """
        url = "https://api.bilibili.com/x/player/v2"
        params = {
            "aid": aid,
            "cid": cid,
        }
        return await self.get(url, params=params)

    async def get_dynamic(self, dyn_id: str):
        """
        获取动态信息
        """
        url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?timezone_offset=-480&id={dyn_id}"
        headers = {
            "Referer": f"https://t.bilibili.com/{dyn_id}",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 uacq"
            ),
        }
        return await self.get(url=url, headers=headers)

    async def search_user(self, keyword: str, ps: int = 5):
        """
        搜索用户
        """
        url = "https://app.bilibili.com/x/v2/search/type"
        data = {"build": "6840300", "keyword": keyword, "type": "2", "ps": ps}

        return await self.get(url, params=data)

    async def get_user_dynamics(self, uid: int, offset: int = 0):
        """从 UP 主页获取动态信息
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/dynamic/space.md#获取用户空间动态"""
        url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space"
        data = {"host_mid": uid}
        if offset:
            data["offset"] = offset
        headers = {
            **DEFAULT_HEADERS,
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 uacq"
            ),
            "Origin": "https://space.bilibili.com",
            "Referer": f"https://space.bilibili.com/{uid}/dynamic",
        }
        return await self.get(url, params=data, headers=headers)

    async def get_all_dynamics_list(self, offset: int = 0):
        """获取该账号订阅的全部动态
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/dynamic/all.md#获取全部动态列表"""
        url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all"
        params = {
            "offset_dynamic_id": offset,
        }
        return await self.get(url, params=params)

    async def check_new_dynamics(self, update_baseline: int = 0):
        """https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/dynamic/all.md#检测是否有新动态"""
        url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all/update"
        params = {
            "update_baseline": update_baseline,
        }
        return await self.get(url, params=params)

    async def relation_modify(self, uid: int, act: int):
        """
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/user/relation.md#操作用户关系

        Act:
            1:	 关注
            2:	 取关
        """
        url = "https://api.bilibili.com/x/relation/modify"
        params = {
            "act": act,
            "fid": int(uid),
        }
        return await self.post(url, params=params, raw=True)

    async def check_user_subs(self, uid: int, ps: int = 50, pn: int = 1):
        """
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/user/relation.md#查询用户关注明细
        ps: 每页数量, 默认(最大值) 50
        pn: 页码
        """
        url = "https://api.bilibili.com/x/relation/followings"
        params = {
            "vmid": uid,
            "ps": ps,
            "pn": pn,
        }
        return await self.get(url, params=params)

    async def get_video_info(self, video_id: int | str):
        """https://github.com/SocialSisterYi/bilibili-API-collect/blob/e5fbfed42807605115c6a9b96447f6328ca263c5/docs/video/info.md#获取视频详细信息(web端)"""
        url = "https://api.bilibili.com/x/web-interface/view"
        params = {}
        video_id = str(video_id).removeprefix("av").removeprefix("AV")
        if video_id.isdigit():
            params["aid"] = int(video_id)
        else:
            params["bvid"] = video_id
        return await self.get(url, params=params)

    async def get_video_info_detail(self, video_id: int | str):
        """https://github.com/SocialSisterYi/bilibili-API-collect/blob/e5fbfed42807605115c6a9b96447f6328ca263c5/docs/video/info.md#获取视频超详细信息(web端)"""
        url = "https://api.bilibili.com/x/web-interface/view/wbi/detail"
        params = {}
        if str(video_id).isdigit():
            params["aid"] = int(video_id)
        else:
            params["bvid"] = video_id
        return await self.get(url, params=params, wbi=True)

    async def get_user_card(self, uid: int):
        """https://github.com/SocialSisterYi/bilibili-API-collect/blob/e5fbfed42807605115c6a9b96447f6328ca263c5/docs/user/info.md#用户名片信息"""
        url = "https://api.bilibili.com/x/web-interface/card"
        params = {
            "mid": uid,
        }
        return await self.get(url, params=params)

    async def get_rooms_info_by_uids(
        self,
        uids: list[int | str],
    ):
        """根据 UID 批量获取直播间信息"""
        url = "https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids"
        data = json.dumps({"uids": uids})
        return await self.post(url, data=data)

    # 以下为旧接口

    async def get_user_dynamics_old(
        self,
        uid: int,
        offset: int = 0,
        *,
        need_top: bool = False,
        **kwargs,
    ):
        """获取指定用户历史动态"""
        url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history"
        params = {
            "host_uid": uid,
            "offset_dynamic_id": offset,
            "need_top": int(bool(need_top)),
        }
        return await self.get(url, params=params, **kwargs)

    async def get_followed_new_dynamics_old(self, **kwargs):
        """获取最新关注动态"""
        url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new"
        params = {
            "type_list": 268435455,
        }
        return await self.get(url, params=params, **kwargs)

    async def get_followed_history_dynamics_old(self, offset: int, **kwargs):
        """获取历史关注动态"""
        url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_history"
        params = {
            "type_list": 268435455,
            "offset_dynamic_id": offset,
        }
        return await self.get(url, params=params, **kwargs)

    async def get_followed_dynamics_update_info_old(self, offset: int = 0, **kwargs):
        """获取关注动态更新信息"""
        url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/web_cyclic_num"
        params = {
            "type_list": 268435455,
            "offset": offset,
        }
        return await self.get(url, params=params, **kwargs)
