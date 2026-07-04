from __future__ import annotations
import json
from jwbuddy.llm.gateway import gateway

PLANNER_PROMPT = """你是任务规划专家。分析用户请求，分解为可并行执行的子任务。

每个子任务应该是独立的、可以被一个 Tool 或 Agent 完成的操作。

用户请求: {request}

可用的工具: {tools}

返回 JSON 格式:
{{
    "tasks": [
        {{
            "id": "task-1",
            "description": "查询信访数据",
            "tool": "sql_query",
            "params": {{ "question": "..." }}
        }}
    ],
    "depends_on": [],
    "reasoning": "分析思路"
}}
"""


class Planner:
    """将用户请求分解为可执行的任务列表"""

    def __init__(self):
        self._llm = gateway

    async def plan(self, request: str, tools_description: str) -> list[dict]:
        """分解任务，返回任务列表"""
        prompt = PLANNER_PROMPT.format(request=request, tools=tools_description)
        result = await self._llm.chat(
            messages=[{"role": "user", "content": prompt}],
            requires_reasoning=True,
        )
        tasks = self._parse_tasks(result.content)
        return tasks or [{
            "id": "task-1",
            "description": request,
            "tool": None,
            "params": {"question": request},
        }]

    def _parse_tasks(self, content: str) -> list[dict] | None:
        import re
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return data.get("tasks", [])
            except json.JSONDecodeError:
                pass
        return None
