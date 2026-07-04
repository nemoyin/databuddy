import pytest
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult
from jwbuddy.tools.registry import ToolRegistry, registry


class HelloTool(BaseTool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="hello",
            description="Says hello",
            parameters={
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Name"}},
                "required": ["name"],
            },
        )

    async def execute(self, **kwargs) -> ToolResult:
        name = kwargs.get("name", "world")
        return ToolResult(data=f"Hello, {name}!")


@pytest.mark.asyncio
async def test_register_and_execute():
    """TC-3.1 + TC-3.3: Register a tool and execute it."""
    tool = HelloTool()
    registry.register(tool)
    result = await registry.execute("hello", name="JWBuddy")
    assert result.success
    assert result.data == "Hello, JWBuddy!"


def test_duplicate_register_raises_error():
    """TC-3.2: Registering same tool name twice raises ValueError."""
    fresh_registry = ToolRegistry()
    tool = HelloTool()
    fresh_registry.register(tool)
    with pytest.raises(ValueError, match="already registered"):
        fresh_registry.register(tool)


@pytest.mark.asyncio
async def test_execute_unregistered_tool():
    """TC-3.4: Executing an unregistered tool returns success=False."""
    fresh_registry = ToolRegistry()
    result = await fresh_registry.execute("not_exist")
    assert not result.success
    assert "not found" in result.error


def test_openai_tools_export():
    """TC-3.5: openai_tools() exports OpenAI function-calling format list."""
    fresh_registry = ToolRegistry()
    tool = HelloTool()
    fresh_registry.register(tool)
    tools = fresh_registry.openai_tools()
    assert isinstance(tools, list)
    assert len(tools) == 1
    assert tools[0]["type"] == "function"
    assert tools[0]["function"]["name"] == "hello"
    assert "parameters" in tools[0]["function"]


def test_custom_tool_extension():
    """TC-3.6: Implement a BaseTool subclass and verify spec/execute work."""
    class EchoTool(BaseTool):
        @property
        def spec(self) -> ToolSpec:
            return ToolSpec(
                name="echo",
                description="Echoes input text",
                parameters={
                    "type": "object",
                    "properties": {"text": {"type": "string", "description": "Text to echo"}},
                    "required": ["text"],
                },
            )

        async def execute(self, **kwargs) -> ToolResult:
            return ToolResult(data=kwargs.get("text", ""))

    fresh_registry = ToolRegistry()
    fresh_registry.register(EchoTool())

    # Check spec
    assert fresh_registry.get("echo").spec.name == "echo"

    # Check openai_tools format
    tools = fresh_registry.openai_tools()
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "echo"
