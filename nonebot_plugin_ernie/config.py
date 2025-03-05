from pydantic import BaseModel


class PluginConfig(BaseModel):
    """Plugin Config Here"""    
    wenxin_api_key: str = ""
    wenxin_appid: str = ""
    wenxin_model: str ="ernie-4.0-turbo-8k"
    wenxin_sendpic: bool = False
    wenxin_timeout: float = 60