import pytest
from unittest.mock import AsyncMock
from jwbuddy.agent.runtime import AgentRuntime, SYSTEM_PROMPT
from jwbuddy.agent.memory import ConversationMemory
from jwbuddy.llm.backends import LLMResult
from jwbuddy.tools.registry import ToolRegistry
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult


# ---- Helper: create a simple tool for testing ----
class MockEchoTool(BaseTool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="echo",
            description="Echoes input",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Text to echo"}},
                "required": ["text"],
            },
        )

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(data={"echo": kwargs.get("text", "")})


class MockErrorTool(BaseTool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="error_tool",
            description="Always fails",
            parameters={"type": "object", "properties": {}, "required": []},
        )

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=False, error="模拟工具执行失败")


# ---- Existing tests ----


@pytest.mark.asyncio
async def test_memory_add_system():
    """TC-4.9: System prompt is added to memory."""
    mem = ConversationMemory()
    mem.add_system("You are a test bot.")
    assert len(mem.messages) == 1
    assert mem.messages[0]["role"] == "system"


@pytest.mark.asyncio
async def test_memory_sliding_window():
    """TC-4.8: Messages beyond max_messages are truncated, system prompt preserved."""
    mem = ConversationMemory(max_messages=5)
    mem.add_system("System")
    for i in range(10):
        mem.add_message("user", f"msg{i}")
    assert len(mem.messages) <= 5
    assert mem.messages[-1]["content"] == "msg9"


@pytest.mark.asyncio
async def test_parse_tool_call_json():
    """TC-4.6: Parse JSON format tool call from LLM output."""
    runtime = AgentRuntime.__new__(AgentRuntime)
    result = runtime._parse_tool_call('{"name": "sql_query", "args": {"sql": "SELECT 1"}}')
    assert result is not None
    assert result["name"] == "sql_query"


@pytest.mark.asyncio
async def test_parse_tool_call_code_block():
    """TC-4.7: Parse code block format tool call from LLM output."""
    runtime = AgentRuntime.__new__(AgentRuntime)
    result = runtime._parse_tool_call('```json\n{"name": "hello", "args": {"name": "test"}}\n```')
    assert result is not None
    assert result["name"] == "hello"


# ---- New Agent Runtime tests (TC-4.1 ~ TC-4.5) ----


@pytest.mark.asyncio
async def test_agent_direct_answer_no_tools():
    """TC-4.1: Agent returns text reply without invoking any tools."""
    mock_llm = AsyncMock()
    mock_llm.chat.return_value = LLMResult(
        content="你好！我是 JWBuddy，有什么可以帮你的？",
        model="test-model",
    )
    tools = ToolRegistry()
    agent = AgentRuntime(llm=mock_llm, tools=tools)

    events = []
    async for event in agent.run("你好"):
        events.append(event)

    # Should get text reply and done event, no tool calls
    event_types = [e["type"] for e in events]
    assert "text" in event_types
    assert "done" in event_types
    assert "tool_call" not in event_types


@pytest.mark.asyncio
async def test_agent_runs_tool_task():
    """TC-4.2: Agent invokes a tool and returns results when needed."""
    mock_llm = AsyncMock()
    # First call: LLM returns tool_calls
    mock_llm.chat.side_effect = [
        LLMResult(
            content="",
            model="test-model",
            tool_calls=[{
                "id": "call_1",
                "type": "function",
                "function": {"name": "echo", "arguments": '{"text": "hello world"}'},
            }],
        ),
        # Second call: LLM returns final text after tool result
        LLMResult(
            content="工具返回了: hello world",
            model="test-model",
        ),
    ]
    tools = ToolRegistry()
    tools.register(MockEchoTool())
    agent = AgentRuntime(llm=mock_llm, tools=tools)

    events = []
    async for event in agent.run("请用 echo 工具"):
        events.append(event)

    event_types = [e["type"] for e in events]
    assert "tool_call" in event_types
    assert "tool_result" in event_types
    assert "text" in event_types
    assert "done" in event_types


@pytest.mark.asyncio
async def test_agent_tool_call_id_passed():
    """TC-4.3: tool_call_id is correctly passed in memory."""
    mock_llm = AsyncMock()
    mock_llm.chat.side_effect = [
        LLMResult(
            content="",
            model="test-model",
            tool_calls=[{
                "id": "call_abc123",
                "type": "function",
                "function": {"name": "echo", "arguments": '{"text": "test"}'},
            }],
        ),
        LLMResult(content="Done.", model="test-model"),
    ]
    tools = ToolRegistry()
    tools.register(MockEchoTool())
    agent = AgentRuntime(llm=mock_llm, tools=tools)

    async for _ in agent.run("测试", session_id="test-session"):
        pass

    # Check that the tool message has tool_call_id
    memory = agent._memories["test-session"]
    tool_messages = [m for m in memory.messages if m["role"] == "tool"]
    assert len(tool_messages) > 0
    assert "tool_call_id" in tool_messages[0]
    assert tool_messages[0]["tool_call_id"] == "call_abc123"


@pytest.mark.asyncio
async def test_agent_error_handling():
    """TC-4.4: Agent reports error when tool fails, does not crash."""
    mock_llm = AsyncMock()
    mock_llm.chat.side_effect = [
        LLMResult(
            content="",
            model="test-model",
            tool_calls=[{
                "id": "call_err",
                "type": "function",
                "function": {"name": "error_tool", "arguments": "{}"},
            }],
        ),
        # After error, LLM should still produce a response
        LLMResult(content="工具执行出错了，请检查。", model="test-model"),
    ]
    tools = ToolRegistry()
    tools.register(MockErrorTool())
    agent = AgentRuntime(llm=mock_llm, tools=tools)

    events = []
    async for event in agent.run("测试错误处理"):
        events.append(event)

    event_types = [e["type"] for e in events]
    # Should have error event but NOT crash
    assert "error" in event_types
    # Should still complete (done event)
    assert "done" in event_types or "text" in event_types


@pytest.mark.asyncio
async def test_agent_multi_turn_conversation():
    """TC-4.5: Multi-turn conversation maintains context across messages."""
    mock_llm = AsyncMock()
    mock_llm.chat.side_effect = [
        LLMResult(content="第一轮回复", model="test-model"),
        LLMResult(content="第二轮回复，引用历史", model="test-model"),
    ]
    tools = ToolRegistry()
    agent = AgentRuntime(llm=mock_llm, tools=tools)

    # Turn 1
    events_1 = []
    async for event in agent.run("第一个问题", session_id="multi-turn"):
        events_1.append(event)
    assert "done" in [e["type"] for e in events_1]

    # Turn 2 (same session)
    events_2 = []
    async for event in agent.run("第二个问题，延续上下文", session_id="multi-turn"):
        events_2.append(event)
    assert "done" in [e["type"] for e in events_2]

    # Verify LLM was called with accumulated history
    # Second call should include messages from both turns
    second_call_messages = mock_llm.chat.call_args_list[1][1]["messages"]
    user_messages = [m for m in second_call_messages if m["role"] == "user"]
    assert len(user_messages) >= 2  # Both questions should be in history


@pytest.mark.asyncio
async def test_agent_system_prompt_with_files():
    """TC-4.9: System prompt includes uploaded file list when files are provided."""
    mock_llm = AsyncMock()
    mock_llm.chat.return_value = LLMResult(content="收到文件", model="test-model")
    tools = ToolRegistry()
    agent = AgentRuntime(llm=mock_llm, tools=tools)

    async for _ in agent.run("分析文件", session_id="file-session", uploaded_files=["data.xlsx", "report.pdf"]):
        pass

    # Check system prompt contains file info
    memory = agent._memories["file-session"]
    system_msg = memory.messages[0]["content"]
    assert "data.xlsx" in system_msg
    assert "report.pdf" in system_msg
    assert "query_file" in system_msg
