from nonebot import get_driver,get_plugin_config,require,on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.log import logger

import httpx
import json

from .config import PluginConfig

require("nonebot_plugin_saa")
from nonebot_plugin_saa import Text

config = get_plugin_config(PluginConfig)

token = ""

wenxin_ak = config.wenxin_ak
wenxin_sk = config.wenxin_sk
wenxin_model = config.wenxin_model
wenxin_sendpic = config.wenxin_sendpic


if wenxin_sendpic == True:
    require("nonebot_plugin_htmlrender")
    from nonebot_plugin_htmlrender import md_to_pic
    from nonebot_plugin_saa import Image

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

__plugin_meta__ = PluginMetadata(
    name="文心一言",
    description="Nonebot框架下的文心一言聊天插件",
    usage="一言 调用文心一言API进行对话生成",
    config=PluginConfig,
    type="application",
    homepage="https://github.com/Noctulus/nonebot-plugin-ernie"
)
#通过access key与secret key获取access token
def get_token():
    global token
    url = "https://aip.baidubce.com/oauth/2.0/token?client_id="+wenxin_ak+"&client_secret="+wenxin_sk+"&grant_type=client_credentials"

    payload = json.dumps("")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    logger.info(f"正在更新token")
    try:
        rsq = httpx.post(url, headers=headers, data=payload)
        token = rsq.json().get("access_token")
    except:
        logger.error("token更新失败，请检查wenxin_ak和wenxin_sk是否正确配置")

    logger.info(f"token已刷新：{token}")



#access token有效期默认为30天，通过计划任务刷新
driver = get_driver()
@driver.on_startup
async def update_token():
    get_token()
    try:
        scheduler.add_job(get_token, "interval", days=30)
    except:
        logger.error("计划任务创建失败")

#获取对话生成结果
async def get_completion(content):

    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/" + wenxin_model +"?access_token=" + token

    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    #异步请求
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload, timeout=60)
        result = response.json()
    
        return(result['result'])

#定义响应操作
chat = on_command("一言", block=False, priority=1)

@chat.handle()
async def _(msg: Message = CommandArg()):
    content = msg.extract_plain_text()

    if token == "" or token is None:
        await Text("尚未配置文心一言 API！请联系机器人管理员", at_sender=True).finish()
    await Text("文心一言正在思考中……").send()

    try:
        res_text = await get_completion(content)
    except Exception as error:
        await Text(str(error)).finish()    
        
    if wenxin_sendpic == True:
        res_img = await md_to_pic(md=res_text)
        await Image(res_img).finish(reply=True)
    else:
        await Text(res_text).finish(reply=True)
    