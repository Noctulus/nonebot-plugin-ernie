from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from nonebot_plugin_ernie.api import ErnieAPIError, QianfanClient
from nonebot_plugin_ernie.config import PluginConfig


def _client(
    handler: Any,
    **config_kwargs: Any,
) -> tuple[QianfanClient, httpx.AsyncClient]:
    config = PluginConfig(wenxin_api_key="test-key", **config_kwargs)
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return QianfanClient(config, http_client=http), http


async def test_chat_success() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers["authorization"]
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "id": "chat-1",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "喵～",
                            "reasoning_content": "先卖个萌",
                        },
                        "finish_reason": "stop",
                        "flag": 0,
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
            },
        )

    client, http = _client(
        handler,
        wenxin_model="ernie-5.1",
        wenxin_system_prompt="你是一只猫娘",
        wenxin_temperature=0.6,
        wenxin_max_tokens=256,
    )
    try:
        result = await client.chat("你好")
    finally:
        await http.aclose()

    assert captured["url"] == "https://qianfan.baidubce.com/v2/chat/completions"
    assert captured["authorization"] == "Bearer test-key"
    assert captured["payload"] == {
        "model": "ernie-5.1",
        "messages": [
            {"role": "system", "content": "你是一只猫娘"},
            {"role": "user", "content": "你好"},
        ],
        "temperature": 0.6,
        "max_tokens": 256,
    }
    assert result.content == "喵～"
    assert result.reasoning == "先卖个萌"
    assert result.finish_reason == "stop"
    assert result.flag == 0
    assert result.usage == {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
    }


async def test_chat_without_system_prompt() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": "ok"}, "finish_reason": "stop"}
                ]
            },
        )

    client, http = _client(handler)
    try:
        await client.chat(" 你好 ")
    finally:
        await http.aclose()

    assert captured["payload"]["messages"] == [{"role": "user", "content": "你好"}]
    assert "temperature" not in captured["payload"]
    assert "max_tokens" not in captured["payload"]


async def test_chat_http_error_is_reported() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "error": {
                    "code": "invalid_token",
                    "message": "Invalid API key",
                }
            },
        )

    client, http = _client(handler)
    try:
        with pytest.raises(ErnieAPIError) as exc_info:
            await client.chat("你好")
    finally:
        await http.aclose()

    error = exc_info.value
    assert error.code == "invalid_token"
    assert "API Key" in str(error)
    assert "Invalid API key" in str(error)


async def test_chat_error_in_200_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"error": {"code": "invalid_request", "message": "bad model"}},
        )

    client, http = _client(handler)
    try:
        with pytest.raises(ErnieAPIError, match="bad model"):
            await client.chat("你好")
    finally:
        await http.aclose()


async def test_chat_timeout_is_reported() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    client, http = _client(handler, wenxin_timeout=3)
    try:
        with pytest.raises(ErnieAPIError, match="超时"):
            await client.chat("你好")
    finally:
        await http.aclose()


async def test_empty_content_is_reported() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": ""}, "flag": 3}]},
        )

    client, http = _client(handler)
    try:
        with pytest.raises(ErnieAPIError, match="安全策略"):
            await client.chat("你好")
    finally:
        await http.aclose()


async def test_text_to_image_success() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "id": "img-1",
                "created": 1735264326,
                "data": [{"url": "https://example.com/cat.png"}],
            },
        )

    client, http = _client(handler, wenxin_image_size="1024x1024")
    try:
        url = await client.text_to_image("一只猫")
    finally:
        await http.aclose()

    assert captured["url"] == "https://qianfan.baidubce.com/v2/images/generations"
    assert captured["payload"] == {
        "model": "qwen-image",
        "prompt": "一只猫",
        "n": 1,
        "size": "1024x1024",
    }
    assert url == "https://example.com/cat.png"


async def test_text_to_image_failure_is_reported() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "task_status": "FAILED",
                        "task_error_code": "image_generation_output_image_unsafe",
                    }
                ]
            },
        )

    client, http = _client(handler)
    try:
        with pytest.raises(ErnieAPIError, match="图片生成失败"):
            await client.text_to_image("一只猫")
    finally:
        await http.aclose()


async def test_missing_api_key_is_reported_before_request() -> None:
    config = PluginConfig()
    http = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: None))
    client = QianfanClient(config, http_client=http)
    try:
        with pytest.raises(ErnieAPIError, match="wenxin_api_key"):
            await client.chat("你好")
    finally:
        await http.aclose()


async def test_base_url_trailing_slash_is_normalized() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"data": [{"url": "https://example.com/a.png"}]})

    client, http = _client(
        handler,
        wenxin_base_url="https://proxy.example.com/v2/",
    )
    try:
        await client.text_to_image("test")
    finally:
        await http.aclose()

    assert captured["url"] == "https://proxy.example.com/v2/images/generations"
