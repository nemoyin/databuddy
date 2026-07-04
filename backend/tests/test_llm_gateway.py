"""Tests for LLM Gateway routing and chat (TC-2.1 ~ TC-2.7)."""
from __future__ import annotations

import os
import pytest
from unittest.mock import AsyncMock, patch
from jwbuddy.llm.gateway import LLMGateway
from jwbuddy.llm.backends import LLMResult


@pytest.fixture(autouse=True)
def _openai_key():
    """Set a fake API key so AsyncOpenAI doesn't raise at construction."""
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    yield


class TestRouting:
    """TC-2.1 ~ TC-2.4: Gateway routing decisions."""

    @pytest.mark.asyncio
    async def test_route_internal_for_sensitive(self):
        """TC-2.1: Sensitive data always routes to internal backend."""
        g = LLMGateway()
        backend = g.route(is_sensitive=True)
        assert backend == g.internal

    @pytest.mark.asyncio
    async def test_route_internal_for_reasoning(self):
        """TC-2.2: Complex reasoning always routes to internal backend."""
        g = LLMGateway()
        backend = g.route(requires_reasoning=True)
        assert backend == g.internal

    @pytest.mark.asyncio
    async def test_route_cloud_when_configured(self, monkeypatch):
        """TC-2.3: Normal request routes to cloud when cloud is configured."""
        monkeypatch.setenv("JWB_LLM_CLOUD_BASE_URL", "https://cloud.example.com/v1")
        monkeypatch.setenv("JWB_LLM_CLOUD_API_KEY", "cloud-api-key")
        from jwbuddy.config import Settings
        # Re-create gateway with patched settings
        import jwbuddy.llm.gateway as gw_mod
        monkeypatch.setattr(gw_mod.settings, "llm_cloud_base_url", "https://cloud.example.com/v1")
        monkeypatch.setattr(gw_mod.settings, "llm_cloud_api_key", "cloud-api-key")
        monkeypatch.setattr(gw_mod.settings, "llm_fallback_enabled", True)

        g = LLMGateway()
        backend = g.route(is_sensitive=False, requires_reasoning=False)
        assert backend == g.cloud

    @pytest.mark.asyncio
    async def test_route_fallback_when_cloud_unconfigured(self, monkeypatch):
        """TC-2.4: Falls back to internal when cloud API key is empty."""
        monkeypatch.setattr("jwbuddy.llm.gateway.settings.llm_cloud_base_url", "")
        monkeypatch.setattr("jwbuddy.llm.gateway.settings.llm_cloud_api_key", "")
        monkeypatch.setattr("jwbuddy.llm.gateway.settings.llm_fallback_enabled", True)

        g = LLMGateway()
        backend = g.route(is_sensitive=False, requires_reasoning=False)
        assert backend == g.internal


class TestChat:
    """TC-2.5 ~ TC-2.7: Chat execution through gateway."""

    @pytest.mark.asyncio
    async def test_basic_chat(self):
        """TC-2.5: Basic chat returns LLMResult with non-empty content."""
        g = LLMGateway()

        with patch.object(g, "route") as mock_route:
            mock_backend = AsyncMock()
            mock_backend.chat.return_value = LLMResult(
                content="你好！有什么可以帮你的？",
                model="test-model",
            )
            mock_route.return_value = mock_backend

            result = await g.chat(
                messages=[{"role": "user", "content": "你好"}],
            )

        assert result.content != ""
        assert "你好" in result.content

    @pytest.mark.asyncio
    async def test_chat_with_tools(self):
        """TC-2.6: Chat with tools returns result that may contain tool_calls or text."""
        g = LLMGateway()

        with patch.object(g, "route") as mock_route:
            mock_backend = AsyncMock()
            mock_backend.chat.return_value = LLMResult(
                content="",
                model="test-model",
                tool_calls=[{
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "sql_query", "arguments": '{"sql": "SELECT * FROM data"}'},
                }],
            )
            mock_route.return_value = mock_backend

            result = await g.chat(
                messages=[{"role": "user", "content": "查询数据"}],
                tools=[{"type": "function", "function": {"name": "sql_query"}}],
            )

        # Result should have tool_calls or content (non-empty either way)
        assert result.tool_calls is not None
        assert result.tool_calls[0]["function"]["name"] == "sql_query"
