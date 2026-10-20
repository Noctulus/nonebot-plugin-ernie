"""文心一言（百度千帆）NoneBot2 插件。"""

import time

from nonebot import get_driver, get_plugin_config, require
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from .api import ErnieAPIError, QianfanClient
from .config import PluginConfig
from .render import markdown_to_image

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import (  # noqa: E402
    Alconna,
    Args,
    Image,
    Match,
    MultiVar,
    Text,
    UniMessage,
    on_alconna,
)

__plugin_meta__ = PluginMetadata(
    name="文心一言",
    description="基于百度千帆 API 的文心一言聊天与文生图插件",
    usage=(
        "一言 <内容>：调用文心一言进行对话\n"
        "绘图 <描述>：调用千帆图像生成模型作画"
    ),
    type="application",
    homepage="https://github.com/Noctulus/nonebot-plugin-ernie",
    config=PluginConfig,
)

config = get_plugin_config(PluginConfig)
client = QianfanClient(config)


def _config_hint(*, image: bool = False) -> str | None:
    """返回配置不完整时的提示；配置完整时返回 None。"""
    if not config.wenxin_api_key.strip():
        return (
            "尚未配置 wenxin_api_key，请在 NoneBot 项目的 .env 中填写"
            "百度千帆 API Key（bce-v3/ALTAK-...）"
        )
    if image:
        if not config.wenxin_image_model.strip():
            return "wenxin_image_model 不能为空"
    elif not config.wenxin_model.strip():
        return "wenxin_model 不能为空"
    return None


def _split_text(text: str, limit: int = 1500) -> list[str]:
    """按段落/长度切分长文本，避免超出聊天平台单条消息长度限制。"""
    text = text.strip()
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        cut = remaining.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunk = remaining[:cut].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[cut:].lstrip("\n")
    if remaining.strip():
        chunks.append(remaining.strip())
    return chunks


async def _send_text_result(content: str, footer: str) -> None:
    chunks = _split_text(content)
    if len(chunks) == 1:
        await UniMessage.text(f"{chunks[0]}\n\n{footer}").finish(reply_to=True)

    for index, chunk in enumerate(chunks):
        await UniMessage.text(chunk).send(reply_to=index == 0)
    await UniMessage.text(footer).finish()


chat = on_alconna(Alconna("一言", Args["content", MultiVar(str)]))


@chat.handle()
async def handle_chat(content: Match[tuple[str, ...]]) -> None:
    if hint := _config_hint():
        await UniMessage.text(hint).finish(reply_to=True)

    prompt = " ".join(str(part) for part in content.result).strip()
    if not prompt:
        await UniMessage.text("请在一言后输入要聊的内容").finish(reply_to=True)

    logger.debug(f"文心一言收到提问：{prompt}")
    await UniMessage.text("文心一言正在思考中……").send(reply_to=True)

    started = time.perf_counter()
    try:
        result = await client.chat(prompt)
    except ErnieAPIError as exc:
        logger.warning(f"文心一言请求失败：{exc}")
        await UniMessage.text(f"请求失败：{exc}").finish(reply_to=True)
    except Exception:  # 避免插件异常导致机器人无响应
        logger.opt(exception=True).error("文心一言请求出现未知错误")
        await UniMessage.text("请求失败，请稍后重试").finish(reply_to=True)

    elapsed = time.perf_counter() - started
    logger.info(
        f"文心一言生成完成，用时 {elapsed:.2f} 秒"
        + (f"，finish_reason={result.finish_reason}" if result.finish_reason else "")
    )

    footer = f"思考完成，用时 {elapsed:.2f} 秒"
    if config.wenxin_sendpic:
        image = await markdown_to_image(result.content)
        if image:
            await UniMessage([Image(raw=image), Text(f"\n{footer}")]).finish(
                reply_to=True
            )

    await _send_text_result(result.content, footer)


draw = on_alconna(Alconna("绘图", Args["prompt", MultiVar(str)]))


@draw.handle()
async def handle_draw(prompt: Match[tuple[str, ...]]) -> None:
    if hint := _config_hint(image=True):
        await UniMessage.text(hint).finish(reply_to=True)

    text = " ".join(str(part) for part in prompt.result).strip()
    if not text:
        await UniMessage.text("请在绘图后输入画面描述").finish(reply_to=True)

    logger.debug(f"文心一言收到绘图请求：{text}")
    await UniMessage.text("文心一言正在作画中……").send(reply_to=True)

    started = time.perf_counter()
    try:
        url = await client.text_to_image(text)
    except ErnieAPIError as exc:
        logger.warning(f"文心一言绘图失败：{exc}")
        await UniMessage.text(f"作画失败：{exc}").finish(reply_to=True)
    except Exception:  # 避免插件异常导致机器人无响应
        logger.opt(exception=True).error("文心一言绘图出现未知错误")
        await UniMessage.text("作画失败，请稍后重试").finish(reply_to=True)

    elapsed = time.perf_counter() - started
    logger.info(f"文心一言绘图完成，用时 {elapsed:.2f} 秒")
    await UniMessage(
        [Image(url=url), Text(f"作画完成，用时 {elapsed:.2f} 秒")]
    ).finish(reply_to=True)


@get_driver().on_startup
async def _check_config() -> None:
    if legacy := config.legacy_options():
        logger.warning(
            "检测到旧版配置项 {}。v2.0 起仅支持千帆 V2 API Key 鉴权，"
            "请删除这些配置并改用 wenxin_api_key。".format("、".join(legacy))
        )

    if hint := _config_hint():
        logger.warning(f"文心一言插件尚未就绪：{hint}")
        return

    logger.info(
        f"文心一言插件已加载：对话模型 {config.wenxin_model}，"
        f"绘图模型 {config.wenxin_image_model}"
    )


@get_driver().on_shutdown
async def _close_client() -> None:
    await client.aclose()
