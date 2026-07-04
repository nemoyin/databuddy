from __future__ import annotations
import pytest
from jwbuddy.tools.chart import ChartTool


def test_parse_chart_config_json_block():
    tool = ChartTool.__new__(ChartTool)
    result = tool._parse_chart_config(
        '```json\n{"chart_type": "bar", "title": "测试", "option": {"xAxis": {}}}\n```'
    )
    assert result is not None
    assert result["chart_type"] == "bar"


def test_parse_chart_config_plain_json():
    tool = ChartTool.__new__(ChartTool)
    result = tool._parse_chart_config(
        '{"chart_type": "line", "title": "Test", "option": {"yAxis": {}}}'
    )
    assert result is not None
    assert result["chart_type"] == "line"


def test_parse_chart_config_invalid():
    tool = ChartTool.__new__(ChartTool)
    result = tool._parse_chart_config("这不是 JSON")
    assert result is None


def test_parse_chart_config_code_block_no_lang():
    tool = ChartTool.__new__(ChartTool)
    result = tool._parse_chart_config(
        '```\n{"chart_type": "pie", "title": "Pie", "option": {"series": []}}\n```'
    )
    assert result is not None
    assert result["chart_type"] == "pie"


@pytest.mark.asyncio
async def test_execute_fallback_on_parse_failure():
    """当 LLM 返回无法解析的内容时，应回退为 table 类型"""
    from jwbuddy.llm.backends import LLMResult

    class FakeGateway:
        async def chat(self, messages, **kwargs):
            return LLMResult(content="抱歉，我无法生成图表", model="fake")

    tool = ChartTool(llm_gateway=FakeGateway())
    result = await tool.execute(data='[{"x": 1}]', question="测试")
    assert result.success is True
    assert result.format == "chart"
    assert result.data["chart_type"] == "table"
    assert result.data["title"] == "测试"


@pytest.mark.asyncio
async def test_execute_with_valid_response():
    from jwbuddy.llm.backends import LLMResult

    class FakeGateway:
        async def chat(self, messages, **kwargs):
            return LLMResult(
                content=(
                    '```json\n'
                    '{"chart_type": "bar", "title": "Sales", '
                    '"option": {"xAxis": {"data": ["A","B"]}, "yAxis": {}, "series": [{"data": [10,20]}]}}\n'
                    '```'
                ),
                model="fake",
            )

    tool = ChartTool(llm_gateway=FakeGateway())
    result = await tool.execute(data='[{"x": "A", "y": 10}]', question="柱状图")
    assert result.success is True
    assert result.data["chart_type"] == "bar"
    assert result.data["title"] == "Sales"
    assert "xAxis" in result.data["option"]
