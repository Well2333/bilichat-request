import urllib.parse
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from loguru import logger
from playwright.async_api import Page, Request, Route

from bilichat_request.account import get_web_account
from bilichat_request.config import config
from bilichat_request.exceptions import CaptchaAbortError

from .browser_ctx import get_browser
from .font import get_font_async

font_mime_map = {
    "collection": "font/collection",
    "otf": "font/otf",
    "sfnt": "font/sfnt",
    "ttf": "font/ttf",
    "woff": "font/woff",
    "woff2": "font/woff2",
}


async def pw_font_injecter(route: Route, request: Request):
    parsed = urllib.parse.urlparse(request.url)
    if not parsed.scheme:
        raise ValueError("字体地址不合法")
    query = urllib.parse.parse_qs(parsed.query)
    name = query.get("name", [None])[0]
    if not name:
        raise ValueError("缺少字体名称")
    try:
        logger.debug(f"请求字体文件 {name}")
        suffix = Path(parsed.path).suffix.lstrip(".")
        await route.fulfill(
            path=await get_font_async(name),
            content_type=font_mime_map.get(suffix),
        )
    except Exception:
        logger.error(f"找不到字体 {name}")
        await route.fallback()


@asynccontextmanager
async def get_new_page(device_scale_factor: float = 2, *, mobile_style: bool = False, **kwargs) -> AsyncIterator[Page]:
    browser = await get_browser()
    if mobile_style:
        kwargs["user_agent"] = config.mobile_user_agent
    logger.trace("创建新页面")
    page = await browser.new_page(device_scale_factor=device_scale_factor, **kwargs)
    async with get_web_account() as account:
        cookies = account.cookies
        await page.context.add_cookies(
            [
                {
                    "domain": ".bilibili.com",
                    "name": name,
                    "path": "/",
                    "value": value,
                }
                for name, value in cookies.items()
            ]
        )
        try:
            yield page
        finally:
            logger.trace("关闭页面")
            cookies = await page.context.cookies()
            account.update(
                {
                    cookie["name"]: cookie["value"]  # type: ignore
                    for cookie in await page.context.cookies("https://bilibili.com")
                }
            )
            await page.close()


async def network_request(request: Request):
    url = request.url
    method = request.method
    response = await request.response()
    if response:
        status = response.status
        timing = "{:.2f}".format(response.request.timing["responseEnd"])
    else:
        status = "/"
        timing = "/"
    logger.debug(f"[Response] [{method} {status}] {timing}ms <<  {url}")
    if "geetest" in url:
        raise CaptchaAbortError("出现验证码, 请求终止")


def network_requestfailed(request: Request):
    url = request.url
    fail = request.failure
    method = request.method
    logger.warning(f"[RequestFailed] [{method} {fail}] << {url}")
    if "geetest" in url:
        raise CaptchaAbortError("出现验证码, 请求终止")


async def check_browser_health():
    try:
        logger.info("检查浏览器是否可以正常运行")
        async with get_new_page() as page:
            await page.goto("https://bilibili.com")
            await page.wait_for_url("https://www.bilibili.com/", timeout=1000)
        logger.success("浏览器运行正常")
    except Exception as e:
        raise RuntimeError("浏览器无法访问bilibili, 请检查安装环境或尝试联系开发者") from e
