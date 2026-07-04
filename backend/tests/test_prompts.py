"""Tests for LLM prompt templates."""
from __future__ import annotations

from jwbuddy.llm.prompts import (
    SYSTEM_PROMPT,
    NL_SQL_PROMPT,
    CHART_PROMPT,
    PLANNER_PROMPT,
)


def test_system_prompt_contains_role():
    assert "JWBuddy" in SYSTEM_PROMPT
    assert "纪检监察" in SYSTEM_PROMPT


def test_nl_sql_prompt_renders():
    prompt = NL_SQL_PROMPT.format(
        schema="表: users\n  - id: integer",
        question="查询所有用户",
        max_rows=100,
        timeout=30,
    )
    assert "users" in prompt
    assert "100" in prompt
    assert "30" in prompt
    assert "SELECT" in prompt


def test_chart_prompt_renders():
    prompt = CHART_PROMPT.format(
        data='[{"name": "Alice", "age": 30}]',
        question="年龄分布",
    )
    assert "Alice" in prompt
    assert "ECharts" in prompt


def test_planner_prompt_renders():
    prompt = PLANNER_PROMPT.format(
        request="分析信访数据",
        tools="sql_query, chart_generate",
    )
    assert "信访" in prompt
    assert "sql_query" in prompt
    assert "tasks" in prompt
