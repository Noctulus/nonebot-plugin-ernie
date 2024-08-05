from pydantic import BaseModel


class PluginConfig(BaseModel):
    """Plugin Config Here"""    
    wenxin_ak: str = ""
    wenxin_sk: str = ""