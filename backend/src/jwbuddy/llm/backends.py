from __future__ import annotations
from abc import ABC, abstractmethod
from typing import AsyncIterator
from openai import AsyncOpenAI


class LLMResult:
    def __init__(self, content: str, model: str, usage: dict | None = None, tool_calls: list[dict] | None = None):
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.tool_calls = tool_calls or None


class LLMBackend(ABC):
    """LLM 后端抽象基类"""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> LLMResult:
        ...

    @abstractmethod
    async def chat_stream(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> AsyncIterator[str]:
        ...


class OpenAICompatibleBackend(LLMBackend):
    """OpenAI 兼容接口后端（vLLM / 政务云）"""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key or None)
        self._model = model

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> LLMResult:
        kwargs = dict(model=self._model, messages=messages, stream=False)
        if tools:
            kwargs["tools"] = tools
        resp = await self.client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        tool_calls = None
        if msg.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
        return LLMResult(
            content=msg.content or "",
            model=self._model,
            usage=resp.usage.model_dump() if resp.usage else {},
            tool_calls=tool_calls,
        )

    async def chat_stream(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> AsyncIterator[str]:
        kwargs = dict(model=self._model, messages=messages, stream=True)
        if tools:
            kwargs["tools"] = tools
        stream = await self.client.chat.completions.create(**kwargs)
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
