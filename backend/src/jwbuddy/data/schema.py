from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine


class SchemaInspector:
    """数据库 Schema 发现 — 读取表结构和注释"""

    @staticmethod
    async def get_schema(engine: AsyncEngine, schema: str = "public") -> list[dict]:
        """返回表结构列表: [{table, columns: [{name, type, nullable, comment}]}]"""
        import sqlalchemy as sa

        tables = []
        async with engine.connect() as conn:
            # Query table list
            table_rows = await conn.execute(
                sa.text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = :schema AND table_type = 'BASE TABLE'"
                ),
                {"schema": schema},
            )
            for row in table_rows:
                table_name = row[0]
                cols = await conn.execute(
                    sa.text(
                        "SELECT column_name, data_type, is_nullable, "
                        "COALESCE(column_default, '') as col_default, "
                        "COALESCE((SELECT pgd.description FROM pg_catalog.pg_statio_all_tables AS st "
                        "INNER JOIN pg_catalog.pg_description pgd ON pgd.objsubid = c.ordinal_position "
                        "AND pgd.objoid = st.relid WHERE st.schemaname = :schema2 AND st.relname = :tbl), '') as comment "  # noqa
                        "FROM information_schema.columns c "
                        "WHERE c.table_schema = :schema3 AND c.table_name = :tbl4 "
                        "ORDER BY ordinal_position"
                    ),
                    {"schema2": schema, "tbl": table_name, "schema3": schema, "tbl4": table_name},
                )
                columns = [
                    {
                        "name": c[0],
                        "type": c[1],
                        "nullable": c[2] == "YES",
                        "default": c[3],
                        "comment": c[4],
                    }
                    for c in cols
                ]
                tables.append({"table": table_name, "columns": columns})
        return tables

    @staticmethod
    def schema_to_prompt(tables: list[dict]) -> str:
        """将 Schema 转换为 LLM 可读的提示文本"""
        lines = ["数据库表结构如下:"]
        for t in tables:
            lines.append(f"\n表: {t['table']}")
            for col in t["columns"]:
                comment = f" ({col['comment']})" if col["comment"] else ""
                nullable = " NULL" if col["nullable"] else " NOT NULL"
                lines.append(f"  - {col['name']}: {col['type']}{nullable}{comment}")
        return "\n".join(lines)
