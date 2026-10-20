"""使用 OneBot V11 适配器模拟一次完整的事件处理。"""

from __future__ import annotations

from typing import Any

import nonebot
import pytest

pytest.importorskip("nonebot.adapters.onebot.v11")

from nonebot.adapters.onebot.v11 import (  # noqa: E402
    Adapter,
    Bot,
    Message,
    MessageEvent,
)
from nonebot_plugin_alconna.consts import ALCONNA_RESULT  # noqa: E402
from nonebot_plugin_alconna.model import CommandResult  # noqa: E402

import nonebot_plugin_ernie as plugin_module  # noqa: E402
from nonebot_plugin_ernie.api import ChatResult, ErnieAPIError  # noqa: E402

nonebot.get_driver().register_adapter(Adapter)


class FakeBot(Bot):
    def __init__(self, adapter: Adapter, self_id: str) -> None:
        super().__init__(adapter, self_id)
        self.sent: list[tuple[str, dict[str, Any]]] = []

    async def call_api(self, api: str, **data: Any) -> Any:
        self.sent.append((api, data))
        return {"message_id": 1}


def _event(text: str) -> MessageEvent:
    message = Message(text)
    return MessageEvent(
        time=0,
        self_id=10000,
        post_type="message",
        sub_type="private",
        user_id=123,
        message_type="private",
        message_id=1,
        message=message,
        original_message=message,
        raw_message=text,
        font=0,
        sender={"user_id": 123, "nickname": "tester"},
        to_me=False,
    )


async def _run(command_name: str, text: str, self_id: str) -> list[str]:
    plugin = nonebot.get_plugin("nonebot_plugin_ernie")
    assert plugin is not None

    matcher_cls = next(
        matcher for matcher in plugin.matcher if matcher.command().name == command_name
    )
    parsed = matcher_cls.command().parse(text)
    assert parsed.matched

    matcher = matcher_cls()
    matcher.state[ALCONNA_RESULT] = CommandResult(result=parsed)

    adapter = nonebot.get_adapter(Adapter)
    bot = FakeBot(adapter, self_id)
    adapter.bot_connect(bot)
    await matcher.run(bot, _event(text), {})

    return [str(data.get("message", "")) for api, data in bot.sent if api == "send_msg"]


async def test_chat_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plugin_module.config, "wenxin_api_key", "test-key")

    async def fake_chat(prompt: str, **_kwargs: Any) -> ChatResult:
        assert prompt == "你好 世界"
        return ChatResult(content="这是回答", finish_reason="stop")

    monkeypatch.setattr(plugin_module.client, "chat", fake_chat)

    sent = await _run("一言", "一言 你好 世界", "10001")

    assert any("正在思考中" in message for message in sent)
    assert any("这是回答" in message and "用时" in message for message in sent)


async def test_draw_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(plugin_module.config, "wenxin_api_key", "test-key")

    async def fake_text_to_image(prompt: str) -> str:
        assert prompt == "一只 猫"
        return "https://example.com/cat.png"

    monkeypatch.setattr(plugin_module.client, "text_to_image", fake_text_to_image)

    sent = await _run("绘图", "绘图 一只 猫", "10002")

    assert any("正在作画中" in message for message in sent)
    assert any("[CQ:image" in message for message in sent)


async def test_chat_handler_renders_markdown_image(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(plugin_module.config, "wenxin_api_key", "test-key")
    monkeypatch.setattr(plugin_module.config, "wenxin_sendpic", True)

    async def fake_chat(_prompt: str, **_kwargs: Any) -> ChatResult:
        return ChatResult(content="# 标题\n\n正文", finish_reason="stop")

    async def fake_render(_markdown: str, **_kwargs: Any) -> bytes:
        return b"\x89PNG\r\n\x1a\n"

    monkeypatch.setattr(plugin_module.client, "chat", fake_chat)
    monkeypatch.setattr(plugin_module, "markdown_to_image", fake_render)

    sent = await _run("一言", "一言 你好", "10003")

    assert any("[CQ:image" in message for message in sent)
    assert any("思考完成" in message for message in sent)


async def test_chat_handler_reports_api_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(plugin_module.config, "wenxin_api_key", "test-key")

    async def fake_chat(_prompt: str, **_kwargs: Any) -> ChatResult:
        raise ErnieAPIError("配额不足", code="quota_exceeded")

    monkeypatch.setattr(plugin_module.client, "chat", fake_chat)

    sent = await _run("一言", "一言 你好", "10004")

    assert any("请求失败" in message and "配额不足" in message for message in sent)
