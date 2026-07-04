from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

API_BASE = "http://localhost:8000"


class JWBClient:
    """JWBuddy API 客户端"""

    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        self._http = httpx.AsyncClient(timeout=60)

    async def create_session(self, title: str = "CLI 会话") -> dict:
        resp = await self._http.post(f"{self.base_url}/sessions", json={"title": title})
        return resp.json()

    async def chat_stream(self, session_id: str, message: str) -> AsyncIterator[str]:
        async with self._http.stream(
            "POST",
            f"{self.base_url}/chat",
            json={"session_id": session_id, "message": message},
        ) as resp:
            buffer = ""
            async for chunk in resp.aiter_bytes():
                buffer += chunk.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            if event.get("type") == "text":
                                yield event["content"]
                            elif event.get("type") == "tool_call":
                                yield f"\n[使用工具: {event['name']}]\n"
                        except json.JSONDecodeError:
                            pass

    async def close(self):
        await self._http.aclose()
