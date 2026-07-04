from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field


class ToolParam(BaseModel):
    """工具参数 schema 描述"""
    name: str
    type: str = "string"
    description: str = ""
    required: bool = False


class ToolSpec(BaseModel):
    """工具的 OpenAPI 风格描述（传给 LLM 的 function calling）"""
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=lambda: {
        "type": "object",
        "properties": {},
        "required": [],
    })


class ToolResult(BaseModel):
    success: bool = True
    data: Any = None
    error: str | None = None
    format: str = "text"  # text | table | chart | html


class BaseTool(ABC):
    """所有 Tool 的基类"""

    @property
    @abstractmethod
    def spec(self) -> ToolSpec:
        ...

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        ...

    def to_openai_tool(self) -> dict:
        s = self.spec
        return {
            "type": "function",
            "function": {
                "name": s.name,
                "description": s.description,
                "parameters": s.parameters,
            },
        }
