from nonebot import get_plugin_config,require
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
import time

from .config import PluginConfig
config = get_plugin_config(PluginConfig)

from .utils import APIHandler
api_handler = APIHandler(config=config)

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import UniMessage,on_alconna,Text,Image,Alconna,Args,Match,MultiVar

if config.wenxin_sendpic:
    require("nonebot_plugin_htmlrender")
    from nonebot_plugin_htmlrender import md_to_pic

__plugin_meta__ = PluginMetadata(
    name="文心一言",
    description="Nonebot框架下的文心一言聊天插件",
    usage=("一言 调用文心一言API进行对话生成\n"
           "绘图 调用文心一言API进行文生图AI绘图"
    ),
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
chat = on_alconna(Alconna("一言",Args["content", MultiVar(str)]))
@chat.handle()
async def _(content: Match[tuple[str, ...]]):
    if error := await check_config():
        await UniMessage([Text(error)]).finish(reply_to=True)
    await UniMessage([Text("文心一言正在思考中")]).send(reply_to=True)

    logger.debug(" ".join(content.result))

    try:
        start_time=time.time()
        if config.wenxin_api_type == "v1":
            res_text = await api_handler.get_v1_completion(content=" ".join(content.result))
        if config.wenxin_api_type == "v2":
            res_text = await api_handler.get_v2_completion(content=" ".join(content.result))
    except Exception as error:
        await UniMessage([Text(error)]).finish(reply_to=True)

    timecost = time.time() - start_time    

    logger.debug(f"思考用时：{timecost}s")

    if config.wenxin_sendpic:
        res_img = await md_to_pic(md=res_text)
        message = UniMessage(
            [
                Image(raw=res_img),
                Text("思考完成，用时" + str("%.2f" % timecost) + "秒")
            ]
        )
    else:
        message = UniMessage(
            [
                Text(res_text + "\n"),
                Text("思考完成，用时" + str("%.2f" % timecost) + "秒")
            ]
        )
    await message.finish(reply_to=True)

text_to_image = on_alconna(Alconna("绘图",Args["prompt", str]))
@text_to_image.handle()
async def _(prompt: Match[str]):
    if error := await check_config():
        await UniMessage([Text(error)]).finish(reply_to=True)
    if config.wenxin_api_type == "v1":
        await UniMessage([Text("当前暂不支持")]).finish(reply_to=True)

    await UniMessage([Text("文心一言正在作画中……")]).send(reply_to=True)
    start_time = time.time()

    try:
        res_url = await api_handler.get_text_to_img(prompt=prompt.result)
    except Exception as error:
        await UniMessage([Text(error)]).finish(reply_to=True)    

    timecost = time.time() - start_time
    logger.debug(f"作画用时：{timecost}s")
    logger.debug(res_url)
    message = UniMessage(
        [
            Image(url=res_url),
            Text("作画完成，用时" + str("%.2f" % timecost) + "秒")
        ]
    )
    await message.finish(reply_to=True)