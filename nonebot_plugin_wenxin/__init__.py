from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message,MessageSegment
from nonebot import logger

import requests
import json
import aiohttp

from .config import Config

from nonebot import require

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

__plugin_meta = PluginMetadata(
    name="文心一言",
    description="Nonebot框架下的文心一言聊天插件",
    usage="一言 调用文心一言API进行对话生成",
    config=Config,
    supported_adapters={"~onebot.v11"},
    type="application"
)

global_config = get_driver().config
config = Config.parse_obj(global_config)

token = ""

wenxin_ak = config.wenxin_ak
wenxin_sk = config.wenxin_sk

#通过access key与secret key获取access token
def get_token():
    global token
    url = "https://aip.baidubce.com/oauth/2.0/token?client_id="+wenxin_ak+"&client_secret="+wenxin_sk+"&grant_type=client_credentials"

    payload = json.dumps("")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    logger.info(f"正在更新token{url}")
    try:
        rsq = requests.request("POST", url, headers=headers, data=payload)
        token = rsq.json().get("access_token")
    except:
        logger.error("token更新失败，请检查wenxin_ak和wenxin_sk是否正确配置")

    logger.info(f"token已刷新：{token}")



#access token有效期默认为30天，通过计划任务刷新
driver = get_driver()
@driver.on_startup
async def _():
    get_token()
    try:
        scheduler.add_job(get_token, "interval", days=30)
    except:
        logger.error("计划任务创建失败")

#获取对话生成结果
async def get_completion(content):

    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=" + token

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
    async with aiohttp.ClientSession() as client:
        response = await client.post(url, headers=headers, data=payload)
        result = await response.json()
    
        return(result['result'])

#定义响应操作
chat = on_command("一言", block=False, priority=1)

@chat.handle()
async def _(msg: Message = CommandArg()):
    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat.finish(MessageSegment.text("内容不能为空！"),at_sender=True)

    await chat.send(MessageSegment.text("文心一言正在思考中……"))

    try:
        res = await get_completion(content)
    except Exception as error:
        await chat.finish(str(error))
    
    await chat.finish(MessageSegment.text(res))