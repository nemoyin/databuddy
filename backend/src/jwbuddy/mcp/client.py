from __future__ import annotations
import json
import httpx
from jwbuddy.mcp.protocol import MCPTool


class MCPClient:
    """MCP 客户端 — 连接外部 MCP 服务"""

    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(timeout=30)

    async def list_tools(self) -> list[MCPTool]:
        """获取远程 MCP 服务提供的工具列表"""
        resp = await self._http.post(
            f"{self.base_url}/mcp",
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        )
        data = resp.json()
        return [MCPTool(**t) for t in data.get("result", {}).get("tools", [])]

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """调用远程 MCP 工具"""
        resp = await self._http.post(
            f"{self.base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
                "id": 2,
            },
        )
        return resp.json().get("result", {})

    async def close(self):
        await self._http.aclose()
