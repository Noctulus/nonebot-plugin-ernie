"""可选的 Markdown 转图片支持。

``nonebot-plugin-htmlrender`` 0.8 起把 ``md_to_pic`` 换成了
``render_markdown``，并返回 ``RenderedImage``；这里同时兼容新旧两套 API。
未安装或渲染失败时返回 ``None``，由调用方回退为文本发送。
"""

from __future__ import annotations

from nonebot.log import logger

__all__ = ["markdown_to_image"]

_warned = False


async def markdown_to_image(markdown: str, *, width: int = 800) -> bytes | None:
    """把 Markdown 文本渲染为 PNG 字节；失败时返回 ``None``。"""
    global _warned

    try:
        import nonebot_plugin_htmlrender as htmlrender
    except Exception as exc:  # 未安装、依赖缺失或 NoneBot 尚未初始化
        if not _warned:
            _warned = True
            logger.warning(
                "无法加载 nonebot-plugin-htmlrender，图片输出已回退为文本：{}", exc
            )
        return None

    try:
        render_markdown = getattr(htmlrender, "render_markdown", None)
        if callable(render_markdown):
            rendered = await render_markdown(
                markdown,
                width=width,
                timeout_seconds=60.0,
            )
            data = getattr(rendered, "data", None)
            if isinstance(data, bytes):
                return data
            if isinstance(rendered, bytes):
                return rendered
            logger.warning("htmlrender 返回了无法识别的渲染结果，已回退为文本")
            return None

        # 兼容 nonebot-plugin-htmlrender < 0.8 的旧接口
        md_to_pic = getattr(htmlrender, "md_to_pic", None)
        if callable(md_to_pic):
            result = await md_to_pic(md=markdown, width=width)
            if isinstance(result, bytes):
                return result
            logger.warning("htmlrender 返回了无法识别的渲染结果，已回退为文本")
            return None
    except Exception as exc:
        if not _warned:
            _warned = True
            logger.opt(exception=exc).warning(
                "Markdown 渲染失败，已回退为文本发送。"
                "请确认已安装 htmlrender 的渲染后端并配置 render.provider"
            )
        return None

    if not _warned:
        _warned = True
        logger.warning(
            "nonebot-plugin-htmlrender 版本过低或缺少渲染接口，图片输出已回退为文本"
        )
    return None
