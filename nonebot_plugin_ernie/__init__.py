from nonebot import get_plugin_config,on_command,require
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.log import logger

import httpx
import json

from .config import PluginConfig
config = get_plugin_config(PluginConfig)

api_key = config.wenxin_api_key
appid = config.wenxin_appid
model = config.wenxin_model
sendpic = config.wenxin_sendpic

require("nonebot_plugin_saa")
from nonebot_plugin_saa import Text
if sendpic == True:
    require("nonebot_plugin_htmlrender")
    from nonebot_plugin_htmlrender import md_to_pic
    from nonebot_plugin_saa import Image

__plugin_meta__ = PluginMetadata(
    name="文心一言",
    description="Nonebot框架下的文心一言聊天插件",
    usage="一言 调用文心一言API进行对话生成",
    config=PluginConfig,
    type="application",
    homepage="https://github.com/Noctulus/nonebot-plugin-ernie",
)

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
async def _(msg: Message = CommandArg()):
    content = msg.extract_plain_text()

    if api_key == "" or api_key is None:
        await Text("尚未配置文心一言 API！请联系机器人管理员", at_sender=True).finish()
    await Text("文心一言正在思考中……").send()

    try:
        res_text = await get_completion(content)
    except Exception as error:
        await Text(str(error)).finish()    
        
    if sendpic == True:
        res_img = await md_to_pic(md=res_text)
        await Image(res_img).finish(reply=True)
    else:
        await Text(res_text).finish(reply=True)
