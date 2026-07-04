from __future__ import annotations
import json
import uuid
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["sessions"])

# 会话持久化存储
_DATA_FILE = Path("data/sessions.json")


def _load_sessions() -> dict[str, dict]:
    if _DATA_FILE.exists():
        try:
            return json.loads(_DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_sessions():
    _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    _DATA_FILE.write_text(
        json.dumps(_sessions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# 模块级会话字典（chat.py 中直接引用此变量）
_sessions: dict[str, dict] = _load_sessions()


class SessionCreate(BaseModel):
    title: str = "新会话"


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: str
    message_count: int = 0


def update_session(session_id: str, **kwargs):
    """供 chat.py 调用，更新会话属性（如 message_count、title）"""
    if session_id in _sessions:
        _sessions[session_id].update(kwargs)
        _save_sessions()


@router.post("")
async def create_session(data: SessionCreate):
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "id": session_id,
        "title": data.title,
        "created_at": datetime.now().isoformat(),
        "message_count": 0,
    }
    _save_sessions()
    return SessionOut(**_sessions[session_id])


@router.get("")
async def list_sessions():
    # 按创建时间倒序
    sorted_sessions = sorted(
        _sessions.values(),
        key=lambda s: s.get("created_at", ""),
        reverse=True,
    )
    return [SessionOut(**s) for s in sorted_sessions]


@router.get("/{session_id}")
async def get_session(session_id: str):
    if session_id not in _sessions:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionOut(**_sessions[session_id])
