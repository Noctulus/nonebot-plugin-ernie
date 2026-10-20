"""百度千帆（文心一言）API 客户端。

只使用千帆 V2 的 OpenAI 兼容接口：

* ``POST /chat/completions``
* ``POST /images/generations``

鉴权方式为 ``Authorization: Bearer <API Key>``，不再需要 AK/SK 或 AppID。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from nonebot.log import logger

from .config import PluginConfig

__all__ = ["ChatResult", "ErnieAPIError", "QianfanClient"]

_HTTP_HINTS = {
    400: "请求参数有误",
    401: "API Key 无效或未授权，请检查 wenxin_api_key",
    403: "没有访问该资源的权限，请检查 API Key 的授权范围",
    404: "接口或模型不存在，请检查 wenxin_model / wenxin_base_url",
    429: "请求过于频繁或配额已用尽，请稍后再试",
    500: "千帆服务内部错误",
    502: "千帆网关错误",
    503: "千帆服务暂时不可用",
}


class ErnieAPIError(RuntimeError):
    """调用千帆 API 失败。"""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.request_id = request_id

    def __str__(self) -> str:
        text = self.message
        if self.code and self.code not in text:
            text = f"{text}（{self.code}）"
        if self.request_id:
            text = f"{text} [request_id={self.request_id}]"
        return text


@dataclass(slots=True)
class ChatResult:
    """一次对话生成的结果。"""

    content: str
    reasoning: str = ""
    usage: dict[str, Any] | None = None
    finish_reason: str | None = None
    flag: int = 0


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _extract_error(data: Any) -> tuple[str, str | None, str | None]:
    """从千帆的错误响应中提取 (message, code, request_id)。"""
    if not isinstance(data, dict):
        return "", None, None

    error = data.get("error")
    if isinstance(error, dict):
        message = _as_text(error.get("message") or error.get("code"))
        code = _as_text(error.get("code") or error.get("type")) or None
        request_id = _as_text(
            error.get("request_id")
            or data.get("request_id")
            or data.get("requestId")
            or data.get("id")
        ) or None
        return message, code, request_id

    message = _as_text(data.get("message") or data.get("error_msg"))
    code = _as_text(data.get("code") or data.get("error_code")) or None
    request_id = _as_text(
        data.get("request_id") or data.get("requestId") or data.get("id")
    ) or None
    return message, code, request_id


class QianfanClient:
    """轻量的异步千帆 API 客户端。"""

    def __init__(
        self,
        config: PluginConfig,
        *,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = config
        self._base_url = (config.wenxin_base_url or "").strip().rstrip("/")
        if not self._base_url:
            self._base_url = "https://qianfan.baidubce.com/v2"
        self._owns_client = http_client is None
        if http_client is not None:
            self._client = http_client
        else:
            client_kwargs: dict[str, Any] = {
                "timeout": httpx.Timeout(
                    config.wenxin_timeout,
                    connect=min(10.0, config.wenxin_timeout),
                ),
                "follow_redirects": True,
                # 不使用环境变量中的代理，避免 socks:// 等 httpx 不支持的协议
                # 导致插件在启动时直接崩溃；需要代理时显式配置 wenxin_proxy。
                "trust_env": False,
            }
            if proxy := config.wenxin_proxy.strip():
                client_kwargs["proxy"] = proxy
            try:
                self._client = httpx.AsyncClient(**client_kwargs)
            except ValueError as exc:
                raise RuntimeError(f"wenxin_proxy 配置无效：{exc}") from exc

    async def aclose(self) -> None:
        """关闭内部持有的 HTTP 客户端。"""
        if self._owns_client:
            await self._client.aclose()

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.wenxin_api_key.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.config.wenxin_api_key.strip():
            raise ErnieAPIError("尚未配置 wenxin_api_key")

        url = f"{self._base_url}{path}"
        try:
            response = await self._client.post(url, json=payload, headers=self._headers)
        except httpx.TimeoutException as exc:
            raise ErnieAPIError(
                f"请求超时（{self.config.wenxin_timeout:g} 秒），"
                "请稍后重试或调大 wenxin_timeout"
            ) from exc
        except httpx.HTTPError as exc:
            raise ErnieAPIError(f"网络请求失败：{exc}") from exc

        try:
            data = response.json()
        except ValueError:
            data = None

        if response.status_code >= 400:
            message, code, request_id = _extract_error(data)
            hint = _HTTP_HINTS.get(
                response.status_code, f"HTTP {response.status_code}"
            )
            detail = message or response.text.strip()[:200]
            text = f"{hint}：{detail}" if detail else hint
            raise ErnieAPIError(text, code=code, request_id=request_id)

        if not isinstance(data, dict):
            raise ErnieAPIError("千帆返回了无法解析的响应")

        # 少数情况下 HTTP 状态码为 200，但响应体里仍然是错误结构。
        if data.get("error") or (
            data.get("code")
            and not data.get("choices")
            and not data.get("data")
        ):
            message, code, request_id = _extract_error(data)
            raise ErnieAPIError(
                message or "千帆返回了错误响应",
                code=code,
                request_id=request_id,
            )

        return data

    async def chat(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> ChatResult:
        """发起一次单轮对话。"""
        prompt = prompt.strip()
        if not prompt:
            raise ErnieAPIError("对话内容不能为空")

        messages: list[dict[str, str]] = []
        system = (
            self.config.wenxin_system_prompt
            if system_prompt is None
            else system_prompt
        ).strip()
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.config.wenxin_model,
            "messages": messages,
        }
        if self.config.wenxin_temperature is not None:
            payload["temperature"] = self.config.wenxin_temperature
        if self.config.wenxin_max_tokens is not None:
            payload["max_tokens"] = self.config.wenxin_max_tokens

        data = await self._post("/chat/completions", payload)

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ErnieAPIError("千帆未返回对话结果")

        choice = choices[0] if isinstance(choices[0], dict) else {}
        message = choice.get("message")
        message = message if isinstance(message, dict) else {}

        content = _as_text(message.get("content")).strip()
        reasoning = _as_text(message.get("reasoning_content"))
        finish_reason = _as_text(
            choice.get("finish_reason") or choice.get("finish_reason ")
        ) or None
        try:
            flag = int(choice.get("flag") or 0)
        except (TypeError, ValueError):
            flag = 0

        # flag: 2 禁聊但可展示；3 禁止上屏；4 撤屏。
        if flag in (3, 4):
            raise ErnieAPIError("生成内容触发了安全策略，已被拦截")
        if not content:
            if finish_reason == "content_filter":
                raise ErnieAPIError("生成内容触发了安全策略，已被拦截")
            raise ErnieAPIError("千帆返回了空内容")

        usage = data.get("usage")
        if not isinstance(usage, dict):
            usage = None
        if usage:
            logger.debug(
                "千帆 token 用量：prompt={} completion={} total={}".format(
                    usage.get("prompt_tokens"),
                    usage.get("completion_tokens"),
                    usage.get("total_tokens"),
                )
            )

        return ChatResult(
            content=content,
            reasoning=reasoning,
            usage=usage,
            finish_reason=finish_reason,
            flag=flag,
        )

    async def text_to_image(self, prompt: str) -> str:
        """调用文生图接口，返回图片 URL。"""
        prompt = prompt.strip()
        if not prompt:
            raise ErnieAPIError("绘图描述不能为空")

        payload: dict[str, Any] = {
            "model": self.config.wenxin_image_model,
            "prompt": prompt,
            "n": 1,
        }
        if self.config.wenxin_image_size:
            payload["size"] = self.config.wenxin_image_size

        data = await self._post("/images/generations", payload)

        items = data.get("data")
        if not isinstance(items, list) or not items:
            raise ErnieAPIError("千帆未返回图片")

        item = items[0] if isinstance(items[0], dict) else {}
        if _as_text(item.get("task_status")).upper() == "FAILED":
            code = _as_text(item.get("task_error_code"))
            raise ErnieAPIError(
                "图片生成失败" + (f"（{code}）" if code else ""),
                code=code or None,
            )

        url = _as_text(item.get("url"))
        if not url:
            raise ErnieAPIError("千帆未返回图片地址")
        return url
