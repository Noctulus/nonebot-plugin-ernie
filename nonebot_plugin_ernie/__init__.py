from nonebot import get_plugin_config,on_command,require
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.log import logger
import time

from .config import PluginConfig
config = get_plugin_config(PluginConfig)

from .utils import APIHandler
api_handler = APIHandler(config=config)

require("nonebot_plugin_saa")
from nonebot_plugin_saa import Text,MessageFactory
if config.wenxin_sendpic:
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

if config.wenxin_api_type == "v1":
    from nonebot import  get_driver
    require("nonebot_plugin_apscheduler")
    from nonebot_plugin_apscheduler import scheduler

    @get_driver().on_startup
    async def init_v1():
        try:
            await api_handler.get_access_token()
            scheduler.add_job(api_handler.get_access_token, "interval", days=30)
        except Exception as e:
            logger.error(f"推理服务 API V1 初始化失败：{e}")


async def check_config():
    if config.wenxin_api_type == "v1" and not (config.wenxin_ak and config.wenxin_sk):
        return "请配置千帆API Key和应用ID"
    if config.wenxin_api_type == "v2" and not (config.wenxin_api_key and config.wenxin_appid):
        return "请配置千帆API Key和Secret Key"

# 定义响应操作
chat = on_command("一言", block=True, priority=1)
@chat.handle()
async def _(msg: Message = CommandArg()):
    if error := await check_config():
        await Text(error).finish(at_sender=True)

    content = msg.extract_plain_text()
    await Text("文心一言正在思考中……").send()

    try:
        start_time=time.time()
        if config.wenxin_api_type == "v1":
            res_text = await api_handler.get_v1_completion(content=content)
        if config.wenxin_api_type == "v2":
            res_text = await api_handler.get_v2_completion(content=content)
    except Exception as error:
        await Text(str(error)).finish(reply=True)    

    logger.debug(f"思考用时：{time.time() - start_time}s")

    if config.wenxin_sendpic:
        res_img = await md_to_pic(md=res_text)
        res = Image(res_img)
    else:
        res = Text(res_text + "\n")

    timecost = time.time() - start_time
    await MessageFactory([res,Text("思考完成，用时" + str("%.2f" % timecost) + "秒")]).finish(reply=True)

text_to_image = on_command("绘图", block=True, priority=1)
@text_to_image.handle()
async def _(msg: Message = CommandArg()):
    if error := await check_config():
        await Text(error).finish(at_sender=True)
    if config.wenxin_api_type == "v1":
        await Text("当前 API 配置暂不支持该服务！")

    content = msg.extract_plain_text()
    start_time = time.time()

    try:
        res_url = await api_handler.get_text_to_img(prompt=content)
    except Exception as error:
        await Text(str(error)).finish(reply=True)    

    timecost = time.time() - start_time
    logger.debug(f"作画用时：{timecost}s")
    await Image(res_url).finish(reply=True)