from __future__ import annotations
import json
from jwbuddy.mcp.protocol import MCPRequest, MCPResponse, MCPTool
from jwbuddy.tools.registry import registry


class MCPServer:
    """MCP 协议服务器 — 将内部 Tool 暴露为标准 MCP 服务"""

    def __init__(self, server_name: str = "jwbuddy"):
        self.server_name = server_name
        self._tool_registry = registry

    def list_tools(self) -> list[dict]:
        """MCP tools/list"""
        return [
            MCPTool(
                name=t.spec.name,
                description=t.spec.description,
                inputSchema=t.spec.parameters,
            ).model_dump()
            for t in self._tool_registry.list_tools()
        ]

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """MCP tools/call"""
        result = await self._tool_registry.execute(name, **arguments)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result.data, ensure_ascii=False, default=str)
                    if result.data
                    else result.error or "",
                }
            ],
            "isError": not result.success,
        }

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """处理 MCP JSON-RPC 请求"""
        if request.method == "tools/list":
            return MCPResponse(result={"tools": self.list_tools()}, id=request.id)
        elif request.method == "tools/call":
            result = await self.call_tool(
                request.params.get("name", ""),
                request.params.get("arguments", {}),
            )
            return MCPResponse(result=result, id=request.id)
        else:
            return MCPResponse(
                error={"code": -32601, "message": f"Method not found: {request.method}"},
                id=request.id,
            )
