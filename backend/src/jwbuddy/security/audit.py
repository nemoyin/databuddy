from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class AuditLogger:
    """审计日志 — 记录所有 Agent 操作"""

    def __init__(self, log_path: str = "logs/audit.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        user: str = "anonymous",
        action: str = "",
        detail: str = "",
        level: str = "INFO",
    ):
        """写入审计日志"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "detail": detail,
            "level": level,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def query(
        self,
        limit: int = 100,
        user: str | None = None,
        action: str | None = None,
    ) -> list[dict]:
        """查询审计日志"""
        if not self.log_path.exists():
            return []

        entries = []
        with open(self.log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        if user:
            entries = [e for e in entries if e.get("user") == user]
        if action:
            entries = [e for e in entries if e.get("action") == action]

        return entries[-limit:]


audit_logger = AuditLogger()
