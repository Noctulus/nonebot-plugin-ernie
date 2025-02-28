from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot import logger
from nonebot.matcher import Matcher

import httpx
import json

from .config import PluginConfig

__plugin_meta__ = PluginMetadata(
    name="文心一言",
    description="Nonebot框架下的文心一言聊天插件",
    usage="一言 调用文心一言API进行对话生成",
    config=PluginConfig,
    type="application",
    homepage="https://github.com/Noctulus/nonebot-plugin-ernie",
)

config = get_plugin_config(PluginConfig)

api_key = config.wenxin_api_key
appid = config.wenxin_appid
model = config.wenxin_model


# 获取对话生成结果
async def get_completion(content):

    url = "https://qianfan.baidubce.com/v2/chat/completions"

    payload = json.dumps(
        {"model": model, "messages": [{"role": "user", "content": content}]}
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
        "appid": appid,
    }

    # 异步请求
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, data=payload, timeout=1)
        except httpx.TimeoutException:
            logger.warning("生成超时")
            raise TimeoutError("思考失败，服务器未及时响应！")
        result = response.json()
        logger.debug(f"{response.text}")

        return result["choices"][0]["message"]["content"]


# 定义响应操作
chat = on_command("一言", block=False, priority=1)


@chat.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    content = msg.extract_plain_text()
    if content == "" or content is None:
        return

    matcher.stop_propagation()

    logger.debug(f"{content}")

    if api_key == "" or api_key is None:
        await matcher.finish("尚未配置文心一言 API！请联系机器人管理员", at_sender=True)
    await matcher.send("文心一言正在思考中……")

    try:
        res = await get_completion(content)
    except Exception as error:
        await matcher.finish(str(error))

    await matcher.finish(res)
