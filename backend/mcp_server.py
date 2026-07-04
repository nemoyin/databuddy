"""JWBuddy MCP Server — 独立暴露内部 Tools 为 MCP 协议"""
from jwbuddy.main import init_tools
from jwbuddy.mcp.server import MCPServer
from jwbuddy.mcp.protocol import MCPRequest
from fastapi import FastAPI, Request

init_tools()
app = FastAPI(title="JWBuddy MCP Server")
_mcp = MCPServer()


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()
    req = MCPRequest(**body)
    resp = await _mcp.handle_request(req)
    return resp.model_dump(exclude_none=True)


@app.get("/health")
async def health():
    return {"status": "ok", "app": "JWBuddy MCP"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
