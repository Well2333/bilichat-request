from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from loguru import logger
from playwright.async_api import Page, Request, Route
from yarl import URL

from bilichat_request.account import get_web_account
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
    url = URL(request.url)
    if not url.is_absolute():
        raise ValueError("字体地址不合法")
    try:
        logger.debug(f"请求字体文件 {url.query['name']}")
        await route.fulfill(
            path=await get_font_async(url.query["name"]),
            content_type=font_mime_map.get(url.suffix),
        )
    except Exception:
        logger.error(f"找不到字体 {url.query['name']}")
        await route.fallback()


@asynccontextmanager
async def get_new_page(device_scale_factor: float = 2, *, mobile_style: bool = False, **kwargs) -> AsyncIterator[Page]:
    browser = await get_browser()
    if mobile_style:
        kwargs["user_agent"] = (
            "5.0 (Linux; Android 13; SM-A037U) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36  uacq"
        )
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
