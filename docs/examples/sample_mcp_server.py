"""
JWBuddy 示例 MCP Server
========================
可作为独立进程运行，通过 MCP 协议暴露自定义 Tool。

启动: python sample_mcp_server.py
测试: curl -X POST http://localhost:8001/mcp -H "Content-Type: application/json" \
         -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
"""
from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(title="JWBuddy Sample MCP Server")


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


# ── 示例 Tool 实现 ──────────────────────────────────

TOOLS = [
    {
        "name": "hello",
        "description": "返回问候语",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "名称"},
            },
        },
    },
    {
        "name": "calculator",
        "description": "执行四则运算",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "第一个数"},
                "b": {"type": "number", "description": "第二个数"},
                "op": {
                    "type": "string",
                    "description": "运算符: add/sub/mul/div",
                    "enum": ["add", "sub", "mul", "div"],
                },
            },
            "required": ["a", "b", "op"],
        },
    },
    {
        "name": "echo",
        "description": "返回传入的参数（用于测试连接）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "要回显的消息"},
            },
        },
    },
]


async def call_tool_handler(name: str, arguments: dict) -> dict:
    if name == "hello":
        name_val = arguments.get("name", "World")
        return {
            "content": [{"type": "text", "text": f"Hello, {name_val}!"}],
            "isError": False,
        }
    elif name == "calculator":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        op = arguments.get("op", "add")
        ops = {"add": a + b, "sub": a - b, "mul": a * b}
        if op == "div":
            if b == 0:
                return {"content": [{"type": "text", "text": "除数不能为 0"}], "isError": True}
            ops["div"] = a / b
        return {
            "content": [{"type": "text", "text": str(ops[op])}],
            "isError": False,
        }
    elif name == "echo":
        return {
            "content": [{"type": "text", "text": json.dumps(arguments, ensure_ascii=False)}],
            "isError": False,
        }
    else:
        return {
            "content": [{"type": "text", "text": f"未知工具: {name}"}],
            "isError": True,
        }


# ── MCP 端点 ────────────────────────────────────────


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()
    req = MCPRequest(**body)

    if req.method == "tools/list":
        return MCPResponse(result={"tools": TOOLS}, id=req.id).model_dump(exclude_none=True)
    elif req.method == "tools/call":
        result = await call_tool_handler(
            req.params.get("name", ""),
            req.params.get("arguments", {}),
        )
        return MCPResponse(result=result, id=req.id).model_dump(exclude_none=True)
    else:
        return MCPResponse(
            error={"code": -32601, "message": f"未知方法: {req.method}"},
            id=req.id,
        ).model_dump(exclude_none=True)


if __name__ == "__main__":
    import uvicorn

    print("JWBuddy Sample MCP Server running on http://localhost:8001")
    print("Try: curl -X POST http://localhost:8001/mcp ...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
