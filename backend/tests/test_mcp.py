from __future__ import annotations
import pytest
from jwbuddy.mcp.protocol import MCPRequest, MCPResponse, MCPTool, MCPListToolsResult
from jwbuddy.mcp.server import MCPServer
from jwbuddy.mcp.client import MCPClient
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult
from jwbuddy.tools.registry import registry


class HelloTool(BaseTool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="hello",
            description="Says hello",
            parameters={
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Name"}},
                "required": ["name"],
            },
        )

    async def execute(self, **kwargs) -> ToolResult:
        name = kwargs.get("name", "world")
        return ToolResult(data=f"Hello, {name}!")


class ErrorTool(BaseTool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="error_tool",
            description="Always fails",
            parameters={"type": "object", "properties": {}},
        )

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=False, error="Something went wrong")


@pytest.fixture(autouse=True)
def setup_tools():
    """Register test tools before each test and clean up after."""
    hello = HelloTool()
    error_tool = ErrorTool()
    registry.register(hello)
    registry.register(error_tool)
    yield
    # Clean up by popping registered tools
    registry._tools.pop("hello", None)
    registry._tools.pop("error_tool", None)


class TestMCPProtocol:
    def test_mcp_request_model(self):
        req = MCPRequest(method="tools/list", id=1)
        assert req.jsonrpc == "2.0"
        assert req.method == "tools/list"
        assert req.params == {}
        assert req.id == 1

    def test_mcp_request_with_params(self):
        req = MCPRequest(
            method="tools/call",
            params={"name": "hello", "arguments": {"name": "test"}},
            id="abc",
        )
        assert req.params["name"] == "hello"

    def test_mcp_response_model(self):
        resp = MCPResponse(result={"tools": []}, id=1)
        assert resp.jsonrpc == "2.0"
        assert resp.result == {"tools": []}
        assert resp.error is None
        assert resp.id == 1

    def test_mcp_response_with_error(self):
        resp = MCPResponse(
            error={"code": -32601, "message": "Method not found"},
            id=None,
        )
        assert resp.error["code"] == -32601

    def test_mcp_tool_model(self):
        tool = MCPTool(
            name="hello",
            description="Says hello",
            inputSchema={"type": "object", "properties": {}},
        )
        assert tool.name == "hello"
        assert tool.inputSchema["type"] == "object"

    def test_mcp_list_tools_result(self):
        result = MCPListToolsResult(tools=[])
        assert result.tools == []


class TestMCPServer:
    def test_list_tools(self):
        server = MCPServer()
        tools = server.list_tools()
        assert isinstance(tools, list)
        assert len(tools) >= 2
        names = [t["name"] for t in tools]
        assert "hello" in names
        assert "error_tool" in names

    def test_list_tools_structure(self):
        server = MCPServer()
        tools = server.list_tools()
        for t in tools:
            assert "name" in t
            assert "description" in t
            assert "inputSchema" in t
            assert isinstance(t["inputSchema"], dict)

    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        server = MCPServer()
        result = await server.call_tool("hello", {"name": "JWBuddy"})
        assert result["isError"] is False
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"
        assert result["content"][0]["text"] == '"Hello, JWBuddy!"'

    @pytest.mark.asyncio
    async def test_call_tool_not_found(self):
        server = MCPServer()
        result = await server.call_tool("nonexistent", {})
        assert result["isError"] is True

    @pytest.mark.asyncio
    async def test_call_tool_error(self):
        server = MCPServer()
        result = await server.call_tool("error_tool", {})
        assert result["isError"] is True
        assert "Something went wrong" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_handle_request_list_tools(self):
        server = MCPServer()
        req = MCPRequest(method="tools/list", id=1)
        resp = await server.handle_request(req)
        assert resp.id == 1
        assert resp.error is None
        assert "tools" in resp.result
        assert len(resp.result["tools"]) >= 2

    @pytest.mark.asyncio
    async def test_handle_request_call_tool(self):
        server = MCPServer()
        req = MCPRequest(
            method="tools/call",
            params={"name": "hello", "arguments": {"name": "Test"}},
            id=2,
        )
        resp = await server.handle_request(req)
        assert resp.id == 2
        assert resp.error is None
        assert resp.result["isError"] is False

    @pytest.mark.asyncio
    async def test_handle_request_unknown_method(self):
        server = MCPServer()
        req = MCPRequest(method="unknown", id=3)
        resp = await server.handle_request(req)
        assert resp.id == 3
        assert resp.result is None
        assert resp.error["code"] == -32601


class TestMCPClient:
    @pytest.mark.asyncio
    async def test_list_tools(self):
        from unittest.mock import AsyncMock

        server = MCPServer()
        expected_tools = server.list_tools()

        client = MCPClient(name="test", base_url="http://localhost:8000")

        # Mock response where json() is a regular sync function
        async def mock_post(url, json=None, **kwargs):
            class MockResponse:
                def json(self):
                    return {
                        "jsonrpc": "2.0",
                        "result": {"tools": expected_tools},
                        "id": 1,
                    }

            return MockResponse()

        client._http.post = mock_post

        tools = await client.list_tools()
        assert len(tools) == len(expected_tools)
        assert tools[0].name == expected_tools[0]["name"]
        await client.close()

    @pytest.mark.asyncio
    async def test_call_tool(self):
        from unittest.mock import AsyncMock

        client = MCPClient(name="test", base_url="http://localhost:8000")

        async def mock_post(url, json=None, **kwargs):
            class MockResponse:
                def json(self):
                    return {
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [{"type": "text", "text": "Hello, World!"}],
                            "isError": False,
                        },
                        "id": 2,
                    }

            return MockResponse()

        client._http.post = mock_post

        result = await client.call_tool("hello", {"name": "World"})
        assert result["content"][0]["text"] == "Hello, World!"
        await client.close()

    @pytest.mark.asyncio
    async def test_base_url_trailing_slash_stripped(self):
        client = MCPClient(name="test", base_url="http://localhost:8000/")
        assert client.base_url == "http://localhost:8000"
        await client.close()
