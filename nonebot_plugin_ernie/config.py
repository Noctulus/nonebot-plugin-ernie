from pydantic import BaseModel


class PluginConfig(BaseModel):
    """Plugin Config Here"""    
    wenxin_ak: str = ""
    wenxin_sk: str = ""
    wenxin_model: str ="ernie-4.0-turbo-8k"