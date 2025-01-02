import sys

from loguru import logger
from playwright.async_api import Browser, Error, Playwright, async_playwright

from bilichat_request.config import nonebot_env

from .install_browser import install_browser

_browser: Browser | None = None
_playwright: Playwright | None = None


async def init(**kwargs) -> Browser:
    global _browser  # noqa: PLW0603
    global _playwright  # noqa: PLW0603
    _playwright = await async_playwright().start()
    try:
        _browser = await launch_browser(**kwargs)
    except Error:
        await install_browser()
        _browser = await launch_browser(**kwargs)
    return _browser


async def launch_browser(**kwargs) -> Browser:
    assert _playwright is not None, "Playwright 没有安装"
    logger.info("使用 firefox 启动")
    return await _playwright.firefox.launch(headless=True, **kwargs)


if nonebot_env and "nonebot_plugin_htmlrender" in sys.modules:
    from nonebot_plugin_htmlrender import get_browser

else:

    async def get_browser(**kwargs) -> Browser:
        return _browser if _browser and _browser.is_connected() else await init(**kwargs)


# async def shutdown_browser():
#    global _browser
#    global _playwright
#    if _browser:
#        if _browser.is_connected():
#            await _browser.close()
#        _browser = None
#    if _playwright:
#        # await _playwright.stop()
#        _playwright = None
