"""端到端集成测试 — 验证完整请求链路。

测试覆盖:
1. 创建会话 (POST /sessions)
2. 发送聊天消息并接收 SSE 响应 (POST /chat)
3. 列出会话 (GET /sessions)

注: Mock LLM 后端以避免对外部推理服务的依赖。
"""

from __future__ import annotations

import os
import json
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from jwbuddy.main import app
from jwbuddy.llm.backends import LLMBackend, LLMResult


class MockLLMBackend(LLMBackend):
    """Mock LLM 后端 — 返回固定回复，不调用真实 API。"""

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> LLMResult:
        return LLMResult(
            content="你好！我是 JWBuddy，有什么可以帮你的？",
            model="mock",
            usage={"total_tokens": 10},
        )

    async def chat_stream(
        self, messages: list[dict], tools: list[dict] | None = None
    ):
        yield "你好！我是 JWBuddy，有什么可以帮你的？"


@pytest.fixture(autouse=True)
def _openai_key():
    """Set a fake API key so AsyncOpenAI doesn't raise at construction,
    in case any code path tries to instantiate the real client."""
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    yield


@pytest.mark.asyncio
async def test_full_flow():
    """测试完整流程: 创建会话 → 发送消息 → 接收 SSE 响应 → 列出会话。"""
    from jwbuddy.api.chat import gateway as chat_gateway

    mock_backend = MockLLMBackend()

    with patch.object(chat_gateway, "route", return_value=mock_backend):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            # 1. Create session
            resp = await client.post(
                "/sessions", json={"title": "E2E Test"}
            )
            assert resp.status_code == 200
            session = resp.json()
            session_id = session["id"]
            assert session["title"] == "E2E Test"
            assert "created_at" in session

            # 2. Send chat message
            resp = await client.post(
                "/chat",
                json={
                    "session_id": session_id,
                    "message": "你好",
                },
            )
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get(
                "content-type", ""
            )

            # 3. Read SSE events
            events = []
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    events.append(data)

            # Should have received events from the agent
            assert len(events) >= 1
            # At minimum, the agent should emit a "thinking" event
            assert any(e["type"] == "thinking" for e in events)
            # Should eventually get a "done" event
            assert any(e["type"] == "done" for e in events)

            # 4. List sessions
            resp = await client.get("/sessions")
            assert resp.status_code == 200
            sessions = resp.json()
            assert isinstance(sessions, list)
            assert len(sessions) >= 1
            ids = [s["id"] for s in sessions]
            assert session_id in ids
