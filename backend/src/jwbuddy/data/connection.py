from __future__ import annotations

import re

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine


def assert_select_only(sql: str) -> bool:
    """Strict check: query must start with SELECT (after comments)"""
    cleaned = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    cleaned = re.sub(r'--.*$', '', cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()
    return cleaned.upper().startswith("SELECT")


class DatabaseManager:
    """异步数据库连接管理器"""

    def __init__(self):
        self._engines: dict[str, AsyncEngine] = {}

    async def connect(self, name: str, url: str) -> bool:
        """注册并测试连接"""
        try:
            engine = create_async_engine(url, pool_size=5, max_overflow=10)
            async with engine.connect() as conn:
                await conn.execute(sa.text("SELECT 1"))
            self._engines[name] = engine
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {name}: {e}")

    def get_engine(self, name: str) -> AsyncEngine | None:
        return self._engines.get(name)

    async def execute(self, name: str, sql: str) -> list[dict]:
        """执行只读 SQL 查询"""
        engine = self._engines.get(name)
        if not engine:
            raise ValueError(f"Unknown datasource: {name}")
        if not assert_select_only(sql):
            raise ValueError("Security Error: Only SELECT queries are allowed")
        async with engine.connect() as conn:
            result = await conn.execute(sa.text(sql))
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]

    def list_connections(self) -> list[str]:
        return list(self._engines.keys())

    async def dispose_all(self):
        for name, engine in self._engines.items():
            await engine.dispose()
        self._engines.clear()


db_manager = DatabaseManager()
