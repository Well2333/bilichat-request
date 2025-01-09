import asyncio
import re

from loguru import logger
from playwright.async_api import Page, Response, TimeoutError  # noqa: A004
from sentry_sdk import capture_exception

from bilichat_request.adapters.browser import get_new_page, network_requestfailed, pw_font_injecter
from bilichat_request.config import config, static_dir
from bilichat_request.exceptions import AbortError, CaptchaAbortError, NotFindAbortError

mobile_style_js = static_dir.joinpath("browser", "mobile_style.js")


async def get_mobile_screenshot(page: Page, dynid: str):
    captcha = False

    async def detect_captcha(response: Response) -> None:
        nonlocal captcha
        logger.debug(f"[Captcha] Get captcha image url: {response.url}")
        if await response.body():
            captcha = True

    page.on(
        "response",
        lambda response: (
            detect_captcha(response) if response.url.startswith("https://static.geetest.com/captcha_v3/") else None
        ),
    )

    url = f"https://m.bilibili.com/dynamic/{dynid}"
    await page.set_viewport_size({"width": 460, "height": 780})
    await page.goto(url, wait_until="networkidle")

    if captcha:
        raise CaptchaAbortError("[Captcha] 需要人机验证, 配置 bilichat_bilibili_cookie 可以缓解此问题")

    if "https://m.bilibili.com/404" in page.url:
        raise NotFindAbortError(f"动态 {dynid} 不存在")

    await page.wait_for_load_state(state="domcontentloaded")
    await page.wait_for_selector(".b-img__inner, .dyn-header__author__face", state="visible")

    await page.add_script_tag(path=mobile_style_js)

    await page.wait_for_function("getMobileStyle()")

    await page.wait_for_load_state("networkidle")
    await page.wait_for_load_state("domcontentloaded")

    await page.wait_for_timeout(200)

    # 判断字体是否加载完成
    need_wait = ["imageComplete", "fontsLoaded"]
    await asyncio.gather(*[page.wait_for_function(f"{i}()") for i in need_wait])

    card = await page.query_selector(".opus-modules" if "opus" in page.url else ".dyn-card")
    assert card
    clip = await card.bounding_box()
    assert clip
    return page, clip


async def get_pc_screenshot(page: Page, dynid: str):
    """电脑端动态截图"""
    url = f"https://t.bilibili.com/{dynid}"
    await page.set_viewport_size({"width": 2560, "height": 1080})
    await page.goto(url, wait_until="networkidle")
    # 动态被删除或者进审核了
    if page.url == "https://www.bilibili.com/404":
        raise NotFindAbortError(f"动态 {dynid} 不存在")
    card = await page.query_selector(".card")
    assert card
    clip = await card.bounding_box()
    assert clip
    bar = await page.query_selector(".bili-dyn-action__icon")
    assert bar
    bar_bound = await bar.bounding_box()
    assert bar_bound
    clip["height"] = bar_bound["y"] - clip["y"]
    return page, clip


async def screenshot(
    dynid: str,
    retry: int = config.retry,
    quality: int = 75,
    *,
    mobile_style: bool = True,
) -> bytes:
    logger.info(f"正在截图动态: {dynid}")
    try:
        async with get_new_page(mobile_style=(mobile_style)) as page:
            await page.route(re.compile("^https://fonts.bbot/(.+)$"), pw_font_injecter)

            # page.on("requestfinished", network_request)
            page.on("requestfailed", network_requestfailed)
            if mobile_style:
                page, clip = await get_mobile_screenshot(page, dynid)  # noqa: PLW2901
            else:
                page, clip = await get_pc_screenshot(page, dynid)  # noqa: PLW2901
            clip["height"] = min(clip["height"], 32766)  # 限制高度
            if picture := await page.screenshot(
                clip=clip,
                full_page=True,
                type="jpeg",
                quality=quality,
            ):
                return picture
            else:
                raise AbortError(f"{dynid} 动态截图失败")
    except CaptchaAbortError:
        if retry:
            logger.error(f"动态 {dynid} 截图出现验证码, 重试...")
            return await screenshot(dynid, retry=retry - 1)
        raise
    except TimeoutError as e:
        if retry:
            logger.error(f"动态 {dynid} 截图超时, 重试...")
            return await screenshot(dynid, mobile_style=mobile_style, quality=quality, retry=retry - 1)
        raise AbortError(f"{dynid} 动态截图超时") from e
    except NotFindAbortError as e:
        raise NotFindAbortError(f"动态 {dynid} 不存在") from e
    except Exception as e:
        if "waiting until" in str(e):
            raise NotFindAbortError(f"动态 {dynid} 不存在") from e
        else:
            capture_exception()
            if retry:
                logger.error(f"动态 {dynid} 截图失败, 重试...")
                return await screenshot(dynid, mobile_style=mobile_style, quality=quality, retry=retry - 1)
            raise AbortError(f"{dynid} 动态截图失败") from e
