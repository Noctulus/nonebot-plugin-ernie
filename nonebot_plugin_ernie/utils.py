import json,httpx
from nonebot.log import logger

class APIHandler:
    def __init__(self, config):
        self.config = config
        self.access_token = ""
    async def get_access_token(self):
        url = f"https://aip.baidubce.com/oauth/2.0/token?client_id={self.config.wenxin_ak}&client_secret={self.config.wenxin_sk}&grant_type=client_credentials"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url)
                self.access_token = response.json()["access_token"]
                logger.info("Access token 刷新成功")
                logger.debug(f"{self.access_token}")
        except Exception as e:
            logger.error(f"Access token获取失败：{e}")
            raise
    
    async def get_v1_completion(self, content):
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.config.wenxin_model}?access_token={self.access_token}"
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

        # 异步请求
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url=url, headers=headers, data=payload, timeout=self.config.wenxin_timeout)
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.warning("生成超时")
                raise TimeoutError("思考失败，服务器未及时响应！")
            except httpx.HTTPError as e:
                logger.error(f"HTTP错误：{e}")
                raise Exception(f"HTTP错误：{e}")
            except Exception as e:
                logger.error(f"请求失败：{e}")
                raise Exception(f"请求失败：{e}")
            
            try:
                result = response.json()
                logger.debug(f"{response.text}")

                return result["result"]
            except Exception as e:
                logger.warning(f"JSON解析失败：{e}")
                raise Exception(f"JSON解析失败：{e}")


    # 获取对话生成结果
    async def get_v2_completion(self, content):
        url = "https://qianfan.baidubce.com/v2/chat/completions"
        payload = json.dumps(
            {"model": self.config.wenxin_model, "messages": [{"role": "user", "content": content}]}
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.wenxin_api_key}",
            "appid": self.config.wenxin_appid,
        }

        # 异步请求
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url=url, headers=headers, data=payload, timeout=self.config.wenxin_timeout)
                response.raise_for_status()
            except httpx.TimeoutException:
                logger.warning("生成超时")
                raise TimeoutError("思考失败，服务器未及时响应！")
            except httpx.HTTPError as e:
                logger.error(f"HTTP错误：{e}")
                raise Exception(f"HTTP错误：{e}")
            except Exception as e:
                logger.error(f"请求失败：{e}")
                raise Exception(f"请求失败：{e}")
            
            try:
                result = response.json()
                logger.debug(f"{response.text}")

                return result["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"JSON解析失败：{e}")
                raise Exception(f"JSON解析失败：{e}")

    async def get_text_to_img(self, prompt):
        url = "https://qianfan.baidubce.com/v2/images/generations"
        payload = json.dumps(
            {"model": "irag-1.0", "prompt": prompt}
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.wenxin_api_key}",
            "appid": self.config.wenxin_appid
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url=url, headers=headers, data=payload, timeout=self.config.wenxin_timeout)
            except httpx.TimeoutException:
                logger.warning("生成超时")
                raise TimeoutError("思考失败，服务器未及时响应！")
            except httpx.HTTPError as e:
                logger.error(f"HTTP错误：{e}")
                raise Exception(f"HTTP错误：{e}")
            except Exception as e:
                logger.error(f"请求失败：{e}")
                raise Exception(f"请求失败：{e}")
            
            try:
                result = response.json()
                logger.debug(f"{response.text}")

                return result["data"][0]["url"]
            except Exception as e:
                logger.warning(f"JSON解析失败：{e}")
                raise Exception(f"JSON解析失败：{e}")