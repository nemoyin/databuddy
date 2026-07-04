from __future__ import annotations
from jwbuddy.tools.base import BaseTool, ToolResult


class ToolRegistry:
    """全局工具注册表"""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        if tool.spec.name in self._tools:
            raise ValueError(f"Tool '{tool.spec.name}' already registered")
        self._tools[tool.spec.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def openai_tools(self) -> list[dict]:
        return [t.to_openai_tool() for t in self._tools.values()]

    async def execute(self, tool_name: str, **kwargs) -> ToolResult:
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(success=False, error=f"Tool '{tool_name}' not found")
        return await tool.execute(**kwargs)


registry = ToolRegistry()
