from __future__ import annotations
import json
from typing import AsyncIterator
from jwbuddy.llm.backends import LLMBackend
from jwbuddy.tools.registry import ToolRegistry
from jwbuddy.agent.memory import ConversationMemory
from jwbuddy.security.audit import audit_logger

SYSTEM_PROMPT = """你是 JWBuddy，纪检监察智能助手。
你可以使用工具来帮助用户查询和分析数据。

数据分析工作流：
1. 先用 query_file 执行 SELECT * FROM data LIMIT 3 了解列名和数据样例
2. 根据列名和用户问题，编写带 GROUP BY、ORDER BY、聚合函数（SUM/COUNT/AVG/MAX/MIN）的分析型 SQL
3. 将查询结果用中文总结，给出结论和建议
4. 如需要可视化，使用 chart 工具

回答格式要求：
- 当有数据结论时，先展示关键数字，再用表格或列表呈现细节
- 当数据适合可视化时，调用 chart 工具生成图表
- 始终用中文回答，保持专业、客观

表格格式规范（重要）：
- 表格每一行（标题行、分隔行、数据行）之间 **必须换行**
- **禁止**把多行表格写在同一物理行内
- 正确示例：
  | 类别 | 数量 |
  |------|------|
  | A | 10 |
- **禁止**使用「一行内逗号拼接多个字段名」的方式
- 数据查询结果的汇总统计优先用分析性文字而非大表格"""


class AgentRuntime:
    """ReAct Agent 运行时 — 思考-行动-观察循环"""

    @staticmethod
    def _fix_markdown_tables(text: str) -> str:
        """修复 LLM 生成时遗漏换行的 Markdown 表格。

        问题场景：LLM 把表格多行写在同一物理行，如：
          | a | b | |---| | c | d |
        修复后：
          | a | b |
          |---|
          | c | d |
        """
        import re
        # 匹配 pipe + (可选空白) + pipe，中间没有实质性内容
        # 这表示一行结束紧接着下一行开始
        return re.sub(r'\|([ \t]*)\|', '|\n|', text)

    def __init__(
        self,
        llm: LLMBackend,
        tools: ToolRegistry,
        system_prompt: str = SYSTEM_PROMPT,
    ):
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iterations = 10
        self._memories: dict[str, ConversationMemory] = {}

    async def run(
        self,
        message: str,
        session_id: str | None = None,
        uploaded_files: list[str] | None = None,
    ) -> AsyncIterator[dict]:
        """执行 Agent 循环，产出流式事件。
        事件类型: text, tool_call, tool_result, done, error
        """
        if session_id and session_id in self._memories:
            memory = self._memories[session_id]
        else:
            memory = ConversationMemory()
            # Inject file context into system prompt if files are uploaded
            system = self.system_prompt
            if uploaded_files:
                file_list = "\n".join(f"  - {f}" for f in uploaded_files)
                system += f"\n\n用户已上传以下文件，可以使用 query_file 工具进行 SQL 查询分析:\n{file_list}"
            memory.add_system(system)
            if session_id:
                self._memories[session_id] = memory
        memory.add_message("user", message)

        for iteration in range(self.max_iterations):
            # Step 1: LLM 思考
            yield {"type": "thinking", "content": ""}

            try:
                result = await self.llm.chat(
                    messages=memory.get_messages(),
                    tools=self.tools.openai_tools(),
                )
            except Exception as e:
                err_msg = f"LLM 连接失败: {e}"
                yield {"type": "error", "content": err_msg}
                yield {"type": "done", "content": err_msg}
                return

            content = result.content
            if not content.strip() and not result.tool_calls:
                yield {"type": "done", "content": "没有收到有效回复。"}
                return

            # Check for native tool_calls first (OpenAI-compatible format)
            if result.tool_calls:
                # Store assistant message with tool_calls for memory
                memory.add_message("assistant", content, tool_calls=result.tool_calls)
                for tc in result.tool_calls:
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        continue
                    tc_id = tc.get("id", "")
                    tool_call = {"name": tc["function"]["name"], "args": args, "id": tc_id}
                    yield {"type": "tool_call", "name": tool_call["name"], "args": tool_call["args"]}
                    audit_logger.log(
                        action=f"tool_call:{tool_call['name']}",
                        detail=f"args: {json.dumps(tool_call['args'], ensure_ascii=False)}",
                    )
                    tool_result = await self.tools.execute(tool_name=tool_call["name"], **tool_call["args"])

                    if tool_result.success:
                        result_text = json.dumps(tool_result.data, ensure_ascii=False, default=str)
                        yield {
                            "type": "tool_result",
                            "name": tool_call["name"],
                            "format": tool_result.format,
                            "data": tool_result.data,
                        }
                        memory.add_message("tool", result_text, tool_call_id=tc_id, name=tool_call["name"])
                    else:
                        yield {"type": "error", "content": tool_result.error}
                        memory.add_message("tool", f"Error: {tool_result.error}", tool_call_id=tc_id)
                # Continue the loop for next iteration
                continue

            memory.add_message("assistant", content)

            # Try to parse tool call from response text
            tool_call = self._parse_tool_call(content)
            if not tool_call:
                # No tool call = final answer
                content = self._fix_markdown_tables(content)
                yield {"type": "text", "content": content}
                yield {"type": "done", "content": content}
                return

            # Step 2: Execute tool
            yield {"type": "tool_call", "name": tool_call["name"], "args": tool_call["args"]}
            audit_logger.log(
                action=f"tool_call:{tool_call['name']}",
                detail=f"args: {json.dumps(tool_call['args'], ensure_ascii=False)}",
            )
            tool_result = await self.tools.execute(tool_name=tool_call["name"], **tool_call["args"])

            if tool_result.success:
                result_text = json.dumps(tool_result.data, ensure_ascii=False, default=str)
                yield {
                    "type": "tool_result",
                    "name": tool_call["name"],
                    "format": tool_result.format,
                    "data": tool_result.data,
                }
                memory.add_message("tool", result_text)
            else:
                yield {"type": "error", "content": tool_result.error}
                memory.add_message("tool", f"Error: {tool_result.error}")

        yield {"type": "done", "content": "已达到最大迭代次数"}

    def _parse_tool_call(self, content: str) -> dict | None:
        """从 LLM 回复中解析工具调用"""
        # OpenAI function calling format
        import re
        match = re.search(r'{"name":\s*"([^"]+)"\s*,\s*"args":\s*({.*?})}', content, re.DOTALL)
        if match:
            name = match.group(1)
            args = json.loads(match.group(2))
            return {"name": name, "args": args}

        # Or just JSON block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if "name" in data and "args" in data:
                    return data
            except json.JSONDecodeError:
                pass
        return None
