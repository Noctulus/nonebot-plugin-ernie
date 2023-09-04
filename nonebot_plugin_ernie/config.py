from pydantic import BaseModel, Extra
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    wenxin_ak: str = ""
    wenxin_sk: str = ""

plugin_config = Config.parse_obj(get_driver().config.dict())