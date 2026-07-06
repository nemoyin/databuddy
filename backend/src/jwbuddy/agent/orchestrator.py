from __future__ import annotations
import asyncio
from typing import AsyncIterator
from jwbuddy.agent.runtime import AgentRuntime
from jwbuddy.agent.planner import Planner
from jwbuddy.tools.registry import registry


class Orchestrator:
    """多 Agent 编排器 — 分解任务 → 并行执行 → 聚合结果"""

    def __init__(self, agent_factory):
        self._planner = Planner()
        self._agent_factory = agent_factory

    async def run(self, message: str) -> AsyncIterator[dict]:
        """编排多 Agent 执行"""
        # Step 1: 规划
        tools_desc = ", ".join(t.spec.name for t in registry.list_tools())
        tasks = await self._planner.plan(message, tools_desc)

        yield {"type": "plan", "tasks": [t["description"] for t in tasks]}

        # Step 2: 并行执行
        results = []
        if len(tasks) > 1:
            # 多任务并行
            async def execute_task(task: dict) -> dict:
                agent = self._agent_factory()
                result_parts = []
                async for event in agent.run(task["description"]):
                    if event["type"] in ("text", "tool_result"):
                        result_parts.append(event)
                return {"task": task, "results": result_parts}

            tasks_coro = [execute_task(t) for t in tasks]
            results = await asyncio.gather(*tasks_coro)
        else:
            # 单任务直接用 Agent
            agent = self._agent_factory()
            async for event in agent.run(message):
                yield event
            return

        # Step 3: 聚合
        summary_parts = []
        for r in results:
            task_desc = r["task"]["description"]
            texts = [e.get("content", "") or str(e.get("data", "")) for e in r["results"]]
            summary_parts.append(f"## {task_desc}\n" + "\n".join(texts))

        aggregated = "\n\n".join(summary_parts)
        aggregated = AgentRuntime._fix_markdown_tables(aggregated)
        yield {"type": "aggregated", "content": aggregated}
        yield {"type": "done", "content": "分析完成"}
