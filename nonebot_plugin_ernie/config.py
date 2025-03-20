from pydantic import BaseModel,Field 
from typing import Literal


class PluginConfig(BaseModel):
    """Plugin Config Here"""
    # API 类型选择
    wenxin_api_type: Literal["v1","v2"] = Field(
        "v1",
        description="API 类型选择"
    )

    # V1 API 配置
    wenxin_ak: str = Field("", description="推理服务 API V1 使用的 API Key")
    wenxin_sk: str = Field("", description="推理服务 API V1 使用的 secret key")

    # V2 API 配置   
    wenxin_api_key: str = Field("", description="推理服务 API V2 使用的 API Key")
    wenxin_appid: str = Field("", description="推理服务 API V2 使用的 AppID")

    # 通用配置
    wenxin_model: str =Field("ernie-4.0-turbo-8k", description="模型名称")
    wenxin_sendpic: bool = Field(True, description="是否以图片形式发送")
    wenxin_timeout: float = Field(60, description="请求超时时间")