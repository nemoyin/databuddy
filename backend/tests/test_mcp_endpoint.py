"""Tests for MCP HTTP endpoint (exposing MCPServer via FastAPI)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport
from jwbuddy.main import app


@pytest.mark.asyncio
async def test_mcp_list_tools_endpoint():
    """MCP HTTP endpoint returns tool list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert "tools" in data["result"]
    # tools list may be empty in test (no lifespan init), but structure is correct
    assert isinstance(data["result"]["tools"], list)


@pytest.mark.asyncio
async def test_mcp_call_tool_endpoint():
    """MCP HTTP endpoint calls registered tool."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "document_parse", "arguments": {"file_path": "/nonexistent/test.pdf"}},
                "id": 2,
            },
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    assert data["id"] == 2


@pytest.mark.asyncio
async def test_mcp_unknown_method():
    """MCP endpoint returns error for unknown method."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "method": "bogus", "id": 3},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == -32601
