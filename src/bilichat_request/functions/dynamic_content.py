import re
from typing import NamedTuple

from loguru import logger

from bilichat_request.adapters.browser import get_new_page, pw_font_injecter
from bilichat_request.exceptions import NotFindAbortError


class DynamicContent(NamedTuple):
    """动态内容结构"""

    text: str  # 文字内容，无内容时为 ""
    images: list[str]  # 图片链接列表，无内容时为 []


async def extract_dynamic_content(dynamic_id: str) -> DynamicContent:
    """
    通过浏览器访问动态页面并提取其中的文字内容和图片链接

    Args:
        dynamic_id: 动态ID

    Returns:
        DynamicContent: 包含文字内容和图片链接的结构

    Raises:
        NotFindAbortError: 动态不存在
    """
    logger.info(f"正在提取动态内容: {dynamic_id}")

    async with get_new_page() as page:
        try:
            await page.route(re.compile("^https://fonts.bbot/(.+)$"), pw_font_injecter)

            # 访问动态页面
            url = f"https://t.bilibili.com/{dynamic_id}"
            await page.goto(url, wait_until="networkidle")

            # 检查页面是否正常加载
            if page.url == "https://www.bilibili.com/404":
                raise NotFindAbortError(f"动态 {dynamic_id} 不存在")

            # 等待页面完全加载
            await page.wait_for_load_state("domcontentloaded")

            # 等待内容加载完成，直到动态内容区域出现
            await page.wait_for_selector(".dyn-card-opus")

            # 查找动态内容区域
            dynamic_cards = await page.query_selector_all(".dyn-card-opus")

            text_content = ""
            image_urls = []

            if dynamic_cards:
                # 使用第一个找到的动态卡片
                card = dynamic_cards[0]

                # 提取文字内容
                text_element = await card.query_selector(".dyn-card-opus__summary .bili-rich-text__content")
                if text_element:
                    text_content = await text_element.inner_text()
                    text_content = text_content.strip()
                    logger.debug(f"找到文字内容: {text_content}")

                # 提取图片链接
                img_elements = await card.query_selector_all(".dyn-card-opus__pics img")
                for img_element in img_elements:
                    try:
                        # 获取图片的src属性
                        src = await img_element.get_attribute("src")
                        if src and (src.startswith(("http", "//"))):
                            # 确保URL格式正确
                            if src.startswith("//"):
                                src = "https:" + src

                            # 清理图片参数
                            if "@" in src:
                                src = src.split("@")[0]

                            # 避免重复
                            if src not in image_urls:
                                logger.debug(f"找到图片链接: {src}")
                                image_urls.append(src)
                    except Exception:
                        logger.exception("获取图片链接时发生错误")
                        continue

            logger.info(f"找到文字内容: {'是' if text_content else '否'}, 找到 {len(image_urls)} 张图片")

            result = DynamicContent(text=text_content, images=image_urls)
            logger.info("成功提取动态内容")

        except NotFindAbortError:
            raise
        except Exception as e:
            logger.error(f"获取动态 {dynamic_id} 的内容时发生错误: {e!s}")
            raise NotFindAbortError(f"获取动态 {dynamic_id} 的内容时发生错误: {e!s}") from e
        return result
