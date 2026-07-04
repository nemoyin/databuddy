from __future__ import annotations
import asyncio
import json
import re
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult
from jwbuddy.data.connection import db_manager
from jwbuddy.data.schema import SchemaInspector
from jwbuddy.data.security import validate_readonly
from jwbuddy.config import settings

NL_SQL_PROMPT = """你是一个 SQL 专家。根据用户的问题和数据库 Schema，生成 PostgreSQL SQL 查询。

约束:
1. 只读查询 (SELECT ONLY)
2. 结果限制最多 {max_rows} 行
3. 超时 {timeout} 秒
4. 字段名用双引号引用
5. 返回 JSON 格式: {{"sql": "完整的 SQL 语句"}}

数据库 Schema:
{schema}

用户问题: {question}
"""


class SQLQueryTool(BaseTool):
    """自然语言 → SQL → 执行查询"""

    def __init__(self, llm_gateway, datasource: str = "default"):
        self._llm = llm_gateway
        self._datasource = datasource

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="sql_query",
            description="用自然语言查询数据库，返回结构化数据",
            parameters={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "用户的自然语言查询问题",
                    },
                },
                "required": ["question"],
            },
        )

    async def execute(self, **kwargs) -> ToolResult:
        question = kwargs.get("question", "")
        if not question:
            return ToolResult(success=False, error="查询问题不能为空")

        # Get schema
        engine = db_manager.get_engine(self._datasource)
        if not engine:
            return ToolResult(success=False, error=f"数据源 '{self._datasource}' 未连接")

        tables = await SchemaInspector.get_schema(engine)
        schema_text = SchemaInspector.schema_to_prompt(tables)

        # NL → SQL via LLM
        prompt = NL_SQL_PROMPT.format(
            schema=schema_text,
            question=question,
            max_rows=settings.sql_max_rows,
            timeout=settings.sql_timeout_seconds,
        )
        result = await self._llm.chat(
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse SQL from LLM response
        sql = self._extract_sql(result.content)
        if not sql:
            return ToolResult(success=False, error="无法从问题生成 SQL")

        # Security check
        if settings.sql_readonly_enabled and not validate_readonly(sql):
            return ToolResult(success=False, error="SQL 安全校验失败：只允许只读查询")

        # Execute
        try:
            rows = await asyncio.wait_for(
                db_manager.execute(self._datasource, sql),
                timeout=settings.sql_timeout_seconds,
            )
            return ToolResult(
                success=True,
                data={"sql": sql, "rows": rows[: settings.sql_max_rows], "total": len(rows)},
                format="table",
            )
        except asyncio.TimeoutError:
            return ToolResult(success=False, error=f"查询超时 ({settings.sql_timeout_seconds}s)")
        except Exception as e:
            return ToolResult(success=False, error=f"查询执行失败: {e}")

    def _extract_sql(self, content: str) -> str | None:
        """从 LLM 回复中提取 SQL"""
        # ```sql ... ``` block
        match = re.search(r'```sql\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        # JSON with sql field
        match = re.search(r'"sql"\s*:\s*"((?:[^"\\]|\\.)*)"', content, re.DOTALL)
        if match:
            return match.group(1).strip().replace('\\n', '\n')
        return None
