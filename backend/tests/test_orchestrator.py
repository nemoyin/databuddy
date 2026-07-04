import pytest
from jwbuddy.agent.planner import Planner


def test_parse_plan():
    planner = Planner.__new__(Planner)
    result = planner._parse_tasks('```json\n{"tasks": [{"id": "t1", "description": "test", "tool": "sql_query", "params": {}}]}\n```')
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == "t1"
