from __future__ import annotations
from typing import Any
from collections import deque


class ConversationMemory:
    """短期会话记忆（滑动窗口）"""

    def __init__(self, max_messages: int = 50, max_tokens: int = 8000):
        self.messages: list[dict[str, str]] = []
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self._metadata: dict[str, Any] = {}

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return len(text) // 4  # rough estimate

    def add_message(self, role: str, content: str, **kwargs):
        msg: dict = {"role": role, "content": content}
        msg.update(kwargs)
        self.messages.append(msg)
        # Enforce max_tokens
        while len(self.messages) > 1 and self._estimate_tokens(str(self.messages)) > self.max_tokens:
            if len(self.messages) > 2:
                self.messages.pop(1)
            else:
                break
        # Also enforce max_messages
        if len(self.messages) > self.max_messages:
            self.messages = [self.messages[0]] + self.messages[-(self.max_messages - 1):]

    def add_system(self, content: str):
        """插入或替换 system prompt"""
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = content
        else:
            self.messages.insert(0, {"role": "system", "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        return list(self.messages)

    def clear(self):
        self.messages.clear()
        self._metadata.clear()
