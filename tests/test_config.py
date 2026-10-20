import pytest
from pydantic import ValidationError

from nonebot_plugin_ernie.config import PluginConfig


def test_default_config() -> None:
    config = PluginConfig()

    assert config.wenxin_api_key == ""
    assert config.wenxin_model == "ernie-4.5-turbo-128k"
    assert config.wenxin_image_model == "qwen-image"
    assert config.wenxin_sendpic is False
    assert config.wenxin_timeout == 120.0
    assert config.wenxin_base_url == "https://qianfan.baidubce.com/v2"
    assert config.legacy_options() == []


def test_optional_generation_parameters() -> None:
    config = PluginConfig(
        wenxin_api_key="test-key",
        wenxin_temperature=0.7,
        wenxin_max_tokens=512,
        wenxin_image_size="1024x1024",
    )

    assert config.wenxin_temperature == 0.7
    assert config.wenxin_max_tokens == 512
    assert config.wenxin_image_size == "1024x1024"


def test_legacy_options_are_reported() -> None:
    config = PluginConfig(wenxin_api_type="v1", wenxin_ak="old-ak")

    assert config.legacy_options() == ["wenxin_api_type", "wenxin_ak"]


def test_invalid_timeout_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PluginConfig(wenxin_timeout=0)
