from __future__ import annotations
import json
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from jwbuddy.agent.runtime import AgentRuntime
from jwbuddy.llm.gateway import gateway
from jwbuddy.tools.registry import registry
from jwbuddy.api.session import _sessions, update_session, save_message

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory agents per session (MVP)
_agents: dict[str, AgentRuntime] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    sensitive: bool = False
    files: list[str] = []


def _get_or_create_agent(session_id: str, is_sensitive: bool = False) -> AgentRuntime:
    if session_id not in _sessions:
        # 如果会话不存在，返回 404
        raise HTTPException(status_code=404, detail="Session not found")
    if session_id not in _agents:
        backend = gateway.route(is_sensitive=is_sensitive)
        _agents[session_id] = AgentRuntime(llm=backend, tools=registry)
    return _agents[session_id]


@router.post("")
async def chat(req: ChatRequest):
    agent = _get_or_create_agent(req.session_id, is_sensitive=req.sensitive)

    # 自动命名：首次消息时将用户问题设为会话标题
    sess = _sessions.get(req.session_id)
    if sess and sess.get("title") in ("新会话", ""):
        # 取前 30 个字作为标题
        title = req.message.strip()[:30]
        if len(req.message) > 30:
            title += "..."
        update_session(req.session_id, title=title, message_count=1)
    elif sess:
        update_session(req.session_id, message_count=sess.get("message_count", 0) + 1)

    async def event_generator():
        # 收集最终回复用于持久化
        final_content = ""
        tool_results: list[dict] = []

        async for event in agent.run(req.message, req.session_id, uploaded_files=req.files):
            yield {"event": event["type"], "data": json.dumps(event, ensure_ascii=False)}
            if event["type"] == "text":
                final_content += event.get("content", "")
            elif event["type"] == "tool_result":
                tool_results.append({
                    "name": event.get("name", ""),
                    "format": event.get("format", "text"),
                    "data": event.get("data"),
                })

        # 流结束后持久化消息
        save_message(req.session_id, "user", req.message, files=req.files or [])
        if final_content:
            save_message(req.session_id, "assistant", final_content, format="markdown")
        for tr in tool_results:
            save_message(req.session_id, "tool", "", format=tr["format"], data=tr["data"], name=tr["name"])

    return EventSourceResponse(event_generator())
