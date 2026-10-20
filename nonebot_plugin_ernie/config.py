"""插件配置。

配置项均可在 NoneBot 项目的 ``.env`` / ``.env.*`` 文件中以同名（大小写不敏感）
环境变量的形式覆盖。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PluginConfig(BaseModel):
    """文心一言插件配置。"""

    # ---------------------------------------------------------------- 鉴权
    wenxin_api_key: str = Field(
        "",
        description="百度千帆 API Key（形如 bce-v3/ALTAK-...）",
    )

    # ---------------------------------------------------------------- 模型
    wenxin_model: str = Field(
        "ernie-4.5-turbo-128k",
        description="文本生成模型 ID，例如 ernie-5.1、ernie-4.5-turbo-128k",
    )
    wenxin_image_model: str = Field(
        "qwen-image",
        description="图像生成模型 ID，例如 qwen-image、musesteamer-air-image",
    )

    # ---------------------------------------------------------------- 生成参数
    wenxin_system_prompt: str = Field(
        "",
        description="系统提示词（人设），为空则不发送 system 消息",
    )
    wenxin_temperature: float | None = Field(
        None,
        description="采样温度，留空则使用模型默认值",
    )
    wenxin_max_tokens: int | None = Field(
        None,
        gt=0,
        description="最大输出 token 数，留空则使用模型默认值",
    )
    wenxin_image_size: str = Field(
        "",
        description="绘图分辨率，例如 1024x1024；留空则使用模型默认值",
    )

    # ---------------------------------------------------------------- 发送与网络
    wenxin_sendpic: bool = Field(
        False,
        description="是否将回答渲染为 Markdown 图片发送（需要 nonebot-plugin-htmlrender）",
    )
    wenxin_timeout: float = Field(
        120.0,
        gt=0,
        description="请求超时时间（秒）",
    )
    wenxin_base_url: str = Field(
        "https://qianfan.baidubce.com/v2",
        description="千帆 API 基础地址，可改为中转/代理地址",
    )
    wenxin_proxy: str = Field(
        "",
        description="HTTP(S) 代理地址，例如 http://127.0.0.1:7890；留空则直连",
    )

    # ---------------------------------------------------------------- 旧版配置（仅用于迁移提示）
    wenxin_api_type: str = Field(
        "",
        description="[已废弃] 旧版 API 类型选择，v2.0 起仅支持千帆 V2 API",
    )
    wenxin_ak: str = Field("", description="[已废弃] 旧版 V1 API Key")
    wenxin_sk: str = Field("", description="[已废弃] 旧版 V1 Secret Key")
    wenxin_appid: str = Field("", description="[已废弃] 旧版 V2 AppID")

    def legacy_options(self) -> list[str]:
        """返回仍然存在的旧版配置项名称。"""
        names = ("wenxin_api_type", "wenxin_ak", "wenxin_sk", "wenxin_appid")
        return [name for name in names if getattr(self, name)]
