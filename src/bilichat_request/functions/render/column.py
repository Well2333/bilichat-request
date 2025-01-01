import asyncio
import re

from loguru import logger
from playwright.async_api import TimeoutError  # noqa: A004
from sentry_sdk import capture_exception

from bilichat_request.adapters.browser import get_new_page, network_requestfailed, pw_font_injecter
from bilichat_request.config import config
from bilichat_request.exceptions import AbortError, CaptchaAbortError, NotFindAbortError


async def screenshot(cvid: str, retry: int = config.retry, quality: int = 75) -> bytes:
    logger.info(f"正在截图专栏: cv{cvid}")
    try:
        async with get_new_page() as page:
            await page.route(re.compile("^https://fonts.bbot/(.+)$"), pw_font_injecter)
            page.on("requestfailed", network_requestfailed)
            url = f"https://www.bilibili.com/read/cv{cvid}"
            await page.set_viewport_size({"width": 1080, "height": 1080})
            await page.goto(url, wait_until="networkidle")
            # 专栏被删除或者进审核了
            if page.url == "https://www.bilibili.com/404":
                raise NotFindAbortError(f"cv{cvid} 专栏不存在")
            content = await page.query_selector(".bili-opus-view")
            assert content
            clip = await content.bounding_box()
            assert clip
            clip["y"] = clip["y"] - 30  # 增加顶部白边
            clip["height"] = min(clip["height"] + 30, 32766)  # 增加顶部白边, 限制高度
            clip["x"] = clip["x"] + 40  # 移除左右一半的白边
            clip["width"] = clip["width"] - 80  # 移除左右一半的白边
            await page.set_viewport_size({"width": 1080, "height": int(clip["height"] + 720)})
            await asyncio.sleep(1)
            await page.wait_for_load_state(state="networkidle")
            if picture := await page.screenshot(
                clip=clip,
                full_page=True,
                type="jpeg",
                quality=quality,
            ):
                return picture
            else:
                logger.warning(f"专栏 cv{cvid} 截图失败, 可能是专栏过长无法截图")
                raise AbortError(f"cv{cvid} 专栏截图失败")
    except CaptchaAbortError as e:
        if retry:
            logger.error(f"专栏 cv{cvid} 截图出现验证码, 重试...")
            return await screenshot(cvid, retry=retry - 1)
        raise
    except TimeoutError as e:
        if retry:
            logger.error(f"专栏 cv{cvid} 截图超时, 重试...")
            return await screenshot(cvid, retry=retry - 1)
        raise AbortError(f"cv{cvid} 专栏截图超时") from e
    except NotFindAbortError:
        if retry:
            logger.error(f"专栏 cv{cvid} 不存在, 3秒后重试...")
            await asyncio.sleep(3)
            return await screenshot(cvid, retry=retry - 1)
        raise
    except Exception as e:
        if "waiting until" in str(e):
            if retry:
                logger.error(f"专栏 cv{cvid} 截图超时, 3秒后重试...")
                await asyncio.sleep(3)
                return await screenshot(cvid, retry=retry - 1)
            raise AbortError(f"cv{cvid} 专栏截图超时") from e
        else:
            capture_exception(e) if config.sentry_dsn else None
            if retry:
                logger.error(f"专栏 cv{cvid} 截图失败, 重试...")
                return await screenshot(cvid, retry=retry - 1)
            raise AbortError(f"cv{cvid} 专栏截图失败") from e
