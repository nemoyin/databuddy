from __future__ import annotations
import json
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult

CHART_PROMPT = """根据数据和用户需求，生成 ECharts 图表配置。

数据: {data}
用户要求: {question}

返回 JSON 格式:
{{
    "chart_type": "bar|line|pie|scatter|table",
    "title": "图表标题",
    "option": {{ ECharts option object }}
}}

注意:
- option 是完整的 ECharts option（不含 container）
- 优先级: 柱状图 > 折线图 > 饼图
- 柱状图用 xAxis/yAxis, 饼图用 series.data
"""


class ChartTool(BaseTool):
    """根据数据自动生成 ECharts 图表"""

    def __init__(self, llm_gateway):
        self._llm = llm_gateway

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="chart_generate",
            description="根据结构化数据生成 ECharts 可视化图表配置",
            parameters={
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "JSON 格式的数据"},
                    "question": {"type": "string", "description": "用户的图表需求"},
                    "chart_type": {
                        "type": "string",
                        "description": "图表类型: bar/line/pie/table",
                        "enum": ["bar", "line", "pie", "table"],
                    },
                },
                "required": ["data", "question"],
            },
        )

    async def execute(self, **kwargs) -> ToolResult:
        data = kwargs.get("data", "[]")
        question = kwargs.get("question", "数据可视化")
        chart_type = kwargs.get("chart_type", "auto")

        prompt = CHART_PROMPT.format(data=data, question=question)
        result = await self._llm.chat(
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse chart config
        chart_config = self._parse_chart_config(result.content)
        if not chart_config:
            chart_config = {
                "chart_type": "table",
                "title": question,
                "option": {},
            }

        return ToolResult(
            success=True,
            data=chart_config,
            format="chart",
        )

    def _parse_chart_config(self, content: str) -> dict | None:
        import re
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None
