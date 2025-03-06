import json,httpx
from nonebot.log import logger

# 获取对话生成结果
async def get_completion(content,model,api_key,appid,timeout):
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
            response = await client.post(url=url, headers=headers, data=payload, timeout=timeout)
        except httpx.TimeoutException:
            logger.warning("生成超时")
            raise TimeoutError("思考失败，服务器未及时响应！")
        result = response.json()
        logger.debug(f"{response.text}")

        return result["choices"][0]["message"]["content"]

async def get_text_to_img(prompt,api_key,appid,timeout):
    url = "https://qianfan.baidubce.com/v2/images/generations"
    payload = json.dumps(
        {"model": "irag-1.0", "prompt": prompt}
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
        "appid": appid,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=url, headers=headers, data=payload, timeout=timeout)
        except httpx.TimeoutException:
            logger.warning("生成超时")
            raise TimeoutError("思考失败，服务器未及时响应！")
        result = response.json()
        logger.debug(f"{response.text}")

        return result["data"][0]["url"]