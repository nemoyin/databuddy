from __future__ import annotations
from pydantic import BaseModel
from typing import Any


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] = {}
    id: str | int


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Any = None
    error: dict | None = None
    id: str | int | None


class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: dict = {"type": "object", "properties": {}}


class MCPListToolsResult(BaseModel):
    tools: list[MCPTool]
