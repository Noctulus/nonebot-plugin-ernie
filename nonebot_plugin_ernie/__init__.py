from nonebot import get_plugin_config,on_command,require
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.log import logger
import time as t

from .utils import get_completion,get_text_to_img
from .config import PluginConfig
config = get_plugin_config(PluginConfig)

api_key = config.wenxin_api_key
appid = config.wenxin_appid
model = config.wenxin_model
sendpic = config.wenxin_sendpic
timeout = config.wenxin_timeout

require("nonebot_plugin_saa")
from nonebot_plugin_saa import Text,MessageFactory
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


# 定义响应操作
chat = on_command("一言", block=True, priority=1)
@chat.handle()
async def _(msg: Message = CommandArg()):
    content = msg.extract_plain_text()

    if api_key == "" or api_key is None:
        await Text("尚未配置文心一言 API！请联系机器人管理员", at_sender=True).finish()
    await Text("文心一言正在思考中……").send()
    t1 = t.time()

    try:
        res_text = await get_completion(content=content,model=model,api_key=api_key,appid=appid,timeout=timeout)
    except Exception as error:
        await Text(str(error)).finish(reply=True)    

    logger.debug(f"思考用时：{t.time() - t1}s")

    if sendpic == True:
        res_img = await md_to_pic(md=res_text)
        res = Image(res_img)
    else:
        res = Text(res_text + "\n")

    timecost = t.time() - t1
    await MessageFactory([res,Text("思考完成，用时" + str("%.2f" % timecost) + "秒")]).finish(reply=True)

text_to_image = on_command("绘图", block=True, priority=1)
@text_to_image.handle()
async def _(msg: Message = CommandArg()):
    content = msg.extract_plain_text()
    if api_key == "" or api_key is None:
        await Text("尚未配置文心一言 API！请联系机器人管理员", at_sender=True).finish()
    await Text("文心一言正在作画中……").send()
    t1 = t.time()

    try:
        res_url = await get_text_to_img(prompt=content,api_key=api_key,appid=appid,timeout=timeout)
    except Exception as error:
        await Text(str(error)).finish(reply=True)    

    res=Image(res_url)
    timecost = t.time() - t1
    logger.debug(f"作画用时：{timecost}s")
    await MessageFactory([res,Text("作画完成，用时" + str("%.2f" % timecost) + "秒")]).finish(reply=True)