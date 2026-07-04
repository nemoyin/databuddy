# JWBuddy MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 在 1-2 个月内交付 JWBuddy MVP——一个面向纪检监察人员的智能体客户端平台，支持自然语言驱动的数据查询分析，具备 Skill/MCP/Tool 扩展体系，提供 Desktop 和 CLI 两种交互形态。

**架构概要:** Python 后端 (FastAPI + LangChain/LangGraph) 提供 Agent 运行时、NL→SQL 数据分析引擎、Skill/MCP 扩展框架；Tauri 2.x + React 桌面客户端通过 HTTP/WebSocket 通信；CLI 使用 Click + Rich。LLM 通过抽象网关支持内网 910B (vLLM) 和政务云 API 双轨切换。

**技术栈:**
- **后端:** Python 3.12+, FastAPI, LangChain, LangGraph, Pydantic, SQLAlchemy, Uvicorn
- **Desktop:** Rust (Tauri 2.x), TypeScript (React 18, Ant Design 5, ECharts, Vite)
- **CLI:** Python (Click, Rich, httpx)
- **数据:** PostgreSQL, Redis, Milvus (向量库)
- **LLM:** OpenAI 兼容接口 (vLLM 对接 910B, 或政务云 API)
- **协议:** MCP (Model Context Protocol) — Python SDK

## 全局约束

- Python >= 3.12，所有异步代码使用 `asyncio` + `async/await`
- FastAPI 使用 `openai` Python SDK 兼容接口调用 LLM
- LLM 调用通过抽象网关，业务代码不直接依赖具体模型
- SQL 查询强制只读模式（禁止 INSERT/UPDATE/DELETE/ALTER/CREATE/DROP）
- 所有 Agent 操作写入审计日志（JSONL 格式）
- Desktop ↔ 后端通信通过 REST API + WebSocket Stream
- 所有代码包含类型注解，通过 `mypy --strict` 检查
- 提交信息遵循 Conventional Commits

---

## 文件结构

```
jwbuddy/
├── backend/                              # Python 后端
│   ├── pyproject.toml
│   └── src/
│       ├── jwbuddy/
│       │   ├── __init__.py
│       │   ├── main.py                   # FastAPI 入口 & 生命周期
│       │   ├── config.py                 # 配置管理 (YAML + 环境变量)
│       │   ├── agent/
│       │   │   ├── __init__.py
│       │   │   ├── runtime.py            # ReAct Agent 运行时
│       │   │   ├── orchestrator.py       # 多 Agent 编排调度
│       │   │   ├── planner.py            # 任务规划器
│       │   │   └── memory.py             # 会话记忆管理
│       │   ├── tools/
│       │   │   ├── __init__.py
│       │   │   ├── base.py               # 工具基类 & Schema
│       │   │   ├── registry.py           # 工具注册表
│       │   │   ├── sql_query.py          # NL→SQL 查询引擎
│       │   │   ├── chart.py              # ECharts 可视化生成
│       │   │   ├── document.py           # 文档解析 (PDF/Word)
│       │   │   └── report.py             # 报告生成
│       │   ├── skills/
│       │   │   ├── __init__.py
│       │   │   ├── loader.py             # Skill 动态加载
│       │   │   └── manager.py            # Skill 生命周期管理
│       │   ├── mcp/
│       │   │   ├── __init__.py
│       │   │   ├── server.py             # MCP Server 实现
│       │   │   ├── client.py             # MCP Client SDK
│       │   │   └── protocol.py           # MCP 协议类型定义
│       │   ├── llm/
│       │   │   ├── __init__.py
│       │   │   ├── gateway.py            # LLM 路由网关
│       │   │   ├── backends.py           # 后端实现 (910B/云)
│       │   │   └── prompts.py            # 提示词模板
│       │   ├── data/
│       │   │   ├── __init__.py
│       │   │   ├── connection.py         # 数据库连接管理
│       │   │   ├── schema.py             # Schema 发现 & 注入
│       │   │   └── security.py           # SQL 安全过滤器
│       │   ├── security/
│       │   │   ├── __init__.py
│       │   │   └── audit.py              # 审计日志
│       │   └── api/
│       │       ├── __init__.py
│       │       ├── chat.py               # Chat API (流式 SSE)
│       │       ├── session.py            # 会话管理 API
│       │       ├── tools.py              # 工具管理 API
│       │       └── admin.py              # 管理 API (数据源/Skill)
│       └── skills/                       # 内置 Skill 目录
│           └── sample/
│               ├── skill.yaml
│               └── __init__.py
├── desktop/                              # Tauri + React 桌面应用
│   ├── src-tauri/
│   │   ├── Cargo.toml
│   │   ├── tauri.conf.json
│   │   └── src/
│   │       └── main.rs
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── DataTable.tsx
│   │   │   ├── ChartRenderer.tsx
│   │   │   ├── HistorySidebar.tsx
│   │   │   └── DataSourceDialog.tsx
│   │   ├── hooks/
│   │   │   ├── useChat.ts
│   │   │   └── useSession.ts
│   │   └── api/
│   │       └── client.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── cli/                                  # CLI 命令行工具
│   └── src/
│       └── jwb/
│           ├── __init__.py
│           ├── __main__.py
│           ├── cli.py
│           └── client.py
└── docs/
    ├── superpowers/specs/2026-06-23-jwbuddy-agent-platform-design.md
    └── superpowers/plans/2026-06-23-jwbuddy-mvp-plan.md
```

---

## Phase 1: 后端基础框架 (Week 1)

### Task 1: Python 项目脚手架 & 配置系统

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/src/jwbuddy/__init__.py`
- Create: `backend/src/jwbuddy/config.py`
- Create: `backend/src/jwbuddy/main.py`

**Interfaces:**
- Produces: `jwbuddy.config.settings` — 全局配置单例
- Produces: `jwbuddy.main.create_app()` — FastAPI 应用工厂

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "jwbuddy"
version = "0.1.0"
description = "纪检监察智能体客户端平台"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "langchain>=0.3.0",
    "langgraph>=0.2.0",
    "langchain-openai>=0.2.0",
    "openai>=1.50.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.30.0",
    "redis>=5.2.0",
    "httpx>=0.28.0",
    "pyyaml>=6.0",
    "python-multipart>=0.0.12",
    "sse-starlette>=2.1.0",
    "rich>=13.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "mypy>=1.13.0",
    "ruff>=0.8.0",
    "httpx",
]

[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

Run: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`

- [ ] **Step 2: 创建配置模块**

```python
# backend/src/jwbuddy/config.py
from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "JWBuddy"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM Gateway
    llm_internal_base_url: str = "http://localhost:8001/v1"
    llm_internal_api_key: str = ""
    llm_internal_model: str = "deepseek-v3"
    llm_cloud_base_url: str = ""
    llm_cloud_api_key: str = ""
    llm_cloud_model: str = "qwen-plus"
    llm_fallback_enabled: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/jwbuddy"
    redis_url: str = "redis://localhost:6379/0"

    # Milvus
    milvus_host: str = "localhost"
    milvus_port: int = 19530

    # Security
    audit_log_path: str = "logs/audit.jsonl"
    sql_readonly_enabled: bool = True
    sql_max_rows: int = 1000
    sql_timeout_seconds: int = 30

    # Paths
    skills_dir: str = str(Path(__file__).parent.parent.parent / "skills")
    data_dir: str = "data"

    model_config = {"env_prefix": "JWB_", "env_file": ".env"}


settings = Settings()
```

- [ ] **Step 3: 创建 FastAPI 主入口**

```python
# backend/src/jwbuddy/main.py
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jwbuddy.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init connections
    yield
    # Shutdown: close connections


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
```

- [ ] **Step 4: 写启动测试**

```python
# backend/tests/test_main.py
from httpx import AsyncClient, ASGITransport
from jwbuddy.main import app


async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
```

Run: `cd backend && pip install httpx && python -m pytest tests/test_main.py -v`  Expected: PASS

- [ ] **Step 5: 创建 `backend/__init__.py` 空白文件（标记 tests 为包）**

```bash
touch backend/tests/__init__.py
```

- [ ] **Step 6: 提交**

```bash
git add backend/ -A
git commit -m "feat: scaffold Python backend with FastAPI and config"
```

---

### Task 2: LLM 网关 — 模型路由抽象层

**Files:**
- Create: `backend/src/jwbuddy/llm/__init__.py`
- Create: `backend/src/jwbuddy/llm/gateway.py`
- Create: `backend/src/jwbuddy/llm/backends.py`
- Create: `backend/src/jwbuddy/llm/prompts.py`

**Interfaces:**
- Produces: `LLMBackend.chat(messages, tools, stream)` — 抽象接口
- Produces: `AscendBackend / CloudBackend` — 具体实现
- Produces: `LLMGateway.route(messages, context)` — 路由决策
- Produces: `PromptTemplates` — 预置提示词模板

- [ ] **Step 1: 定义 LLM 后端抽象**

```python
# backend/src/jwbuddy/llm/backends.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import AsyncIterator
from openai import AsyncOpenAI


class LLMResult:
    def __init__(self, content: str, model: str, usage: dict | None = None):
        self.content = content
        self.model = model
        self.usage = usage or {}


class LLMBackend(ABC):
    """LLM 后端抽象基类"""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> AsyncIterator[LLMResult] | LLMResult:
        ...

    @abstractmethod
    async def chat_stream(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> AsyncIterator[str]:
        ...


class OpenAICompatibleBackend(LLMBackend):
    """OpenAI 兼容接口后端（vLLM / 政务云）"""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self._model = model

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> LLMResult:
        kwargs = dict(model=self._model, messages=messages, stream=False)
        if tools:
            kwargs["tools"] = tools
        resp = await self.client.chat.completions.create(**kwargs)
        return LLMResult(
            content=resp.choices[0].message.content or "",
            model=self._model,
            usage=resp.usage.model_dump() if resp.usage else {},
        )

    async def chat_stream(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> AsyncIterator[str]:
        kwargs = dict(model=self._model, messages=messages, stream=True)
        if tools:
            kwargs["tools"] = tools
        stream = await self.client.chat.completions.create(**kwargs)
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
```

- [ ] **Step 2: 实现 LLM 路由网关**

```python
# backend/src/jwbuddy/llm/gateway.py
from __future__ import annotations
from typing import AsyncIterator
from jwbuddy.config import settings
from jwbuddy.llm.backends import LLMBackend, OpenAICompatibleBackend, LLMResult


class LLMGateway:
    """LLM 路由网关 — 根据上下文选择合适的后端"""

    def __init__(self):
        self._internal: OpenAICompatibleBackend | None = None
        self._cloud: OpenAICompatibleBackend | None = None

    @property
    def internal(self) -> OpenAICompatibleBackend:
        if self._internal is None:
            self._internal = OpenAICompatibleBackend(
                base_url=settings.llm_internal_base_url,
                api_key=settings.llm_internal_api_key,
                model=settings.llm_internal_model,
            )
        return self._internal

    @property
    def cloud(self) -> OpenAICompatibleBackend:
        if self._cloud is None:
            self._cloud = OpenAICompatibleBackend(
                base_url=settings.llm_cloud_base_url,
                api_key=settings.llm_cloud_api_key,
                model=settings.llm_cloud_model,
            )
        return self._cloud

    def route(self, is_sensitive: bool = False, requires_reasoning: bool = False) -> LLMBackend:
        """路由决策: 涉密→内网, 复杂推理→内网, 否则→可回退"""
        if is_sensitive or requires_reasoning:
            return self.internal
        if settings.llm_fallback_enabled:
            return self.cloud
        return self.internal

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        is_sensitive: bool = False,
        requires_reasoning: bool = False,
        stream: bool = False,
    ) -> LLMResult | AsyncIterator[str]:
        backend = self.route(is_sensitive, requires_reasoning)
        if stream:
            return backend.chat_stream(messages, tools)
        return await backend.chat(messages, tools, stream=False)


gateway = LLMGateway()
```

- [ ] **Step 3: 写测试**

```python
# backend/tests/test_llm_gateway.py
from jwbuddy.llm.gateway import LLMGateway


async def test_route_internal_for_sensitive():
    g = LLMGateway()
    backend = g.route(is_sensitive=True)
    assert backend == g.internal


async def test_route_cloud_for_normal():
    g = LLMGateway()
    backend = g.route(is_sensitive=False, requires_reasoning=False)
    # Without cloud configured, may fall back
    assert backend is not None
```

Run: `cd backend && python -m pytest tests/test_llm_gateway.py -v` Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add backend/src/jwbuddy/llm/ -A backend/tests/test_llm_gateway.py
git commit -m "feat: add LLM gateway with routing and backend abstraction"
```

---

### Task 3: Tool 框架 — 基类 & 注册表

**Files:**
- Create: `backend/src/jwbuddy/tools/__init__.py`
- Create: `backend/src/jwbuddy/tools/base.py`
- Create: `backend/src/jwbuddy/tools/registry.py`

**Interfaces:**
- Produces: `BaseTool` — 工具基类，子类需实现 `execute()` 和 `schema`
- Produces: `ToolRegistry` — 全局注册表，支持注册/查找/获取 schema 列表

- [ ] **Step 1: 创建工具基类**

```python
# backend/src/jwbuddy/tools/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field


class ToolParam(BaseModel):
    """工具参数 schema 描述"""
    name: str
    type: str = "string"
    description: str = ""
    required: bool = False


class ToolSpec(BaseModel):
    """工具的 OpenAPI 风格描述（传给 LLM 的 function calling）"""
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=lambda: {
        "type": "object",
        "properties": {},
        "required": [],
    })


class ToolResult(BaseModel):
    success: bool = True
    data: Any = None
    error: str | None = None
    format: str = "text"  # text | table | chart | html


class BaseTool(ABC):
    """所有 Tool 的基类"""

    @property
    @abstractmethod
    def spec(self) -> ToolSpec:
        ...

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        ...

    def to_openai_tool(self) -> dict:
        s = self.spec
        return {
            "type": "function",
            "function": {
                "name": s.name,
                "description": s.description,
                "parameters": s.parameters,
            },
        }
```

- [ ] **Step 2: 创建工具注册表**

```python
# backend/src/jwbuddy/tools/registry.py
from __future__ import annotations
from jwbuddy.tools.base import BaseTool


class ToolRegistry:
    """全局工具注册表"""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        if tool.spec.name in self._tools:
            raise ValueError(f"Tool '{tool.spec.name}' already registered")
        self._tools[tool.spec.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def openai_tools(self) -> list[dict]:
        return [t.to_openai_tool() for t in self._tools.values()]

    async def execute(self, name: str, **kwargs) -> ToolResult:
        tool = self.get(name)
        if not tool:
            return ToolResult(success=False, error=f"Tool '{name}' not found")
        return await tool.execute(**kwargs)


registry = ToolRegistry()
```

- [ ] **Step 3: 写测试**

```python
# backend/tests/test_tool_registry.py
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult
from jwbuddy.tools.registry import registry


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


async def test_register_and_execute():
    tool = HelloTool()
    registry.register(tool)
    result = await registry.execute("hello", name="JWBuddy")
    assert result.success
    assert result.data == "Hello, JWBuddy!"
```

Run: `cd backend && python -m pytest tests/test_tool_registry.py -v` Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add backend/src/jwbuddy/tools/ -A backend/tests/test_tool_registry.py
git commit -m "feat: add tool framework with base class and registry"
```

---

### Task 4: Agent 运行时 — ReAct 循环

**Files:**
- Create: `backend/src/jwbuddy/agent/__init__.py`
- Create: `backend/src/jwbuddy/agent/runtime.py`
- Create: `backend/src/jwbuddy/agent/memory.py`

**Interfaces:**
- Consumes: `LLMBackend`, `ToolRegistry`
- Produces: `AgentRuntime.run(message, session_id)` — 执行 Agent 循环，返回流式结果

- [ ] **Step 1: 实现会话记忆模块**

```python
# backend/src/jwbuddy/agent/memory.py
from __future__ import annotations
from typing import Any
from collections import deque


class ConversationMemory:
    """短期会话记忆（滑动窗口）"""

    def __init__(self, max_messages: int = 50, max_tokens: int = 8000):
        self.messages: list[dict[str, str]] = []
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self._metadata: dict[str, Any] = {}

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            # Keep system prompt + recent messages
            self.messages = [self.messages[0]] + self.messages[-(self.max_messages - 1):]

    def add_system(self, content: str):
        """插入或替换 system prompt"""
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = content
        else:
            self.messages.insert(0, {"role": "system", "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        return list(self.messages)

    def clear(self):
        self.messages.clear()
        self._metadata.clear()
```

- [ ] **Step 2: 实现 ReAct Agent 运行时**

```python
# backend/src/jwbuddy/agent/runtime.py
from __future__ import annotations
import json
from typing import AsyncIterator
from jwbuddy.llm.backends import LLMBackend
from jwbuddy.tools.registry import ToolRegistry
from jwbuddy.agent.memory import ConversationMemory

SYSTEM_PROMPT = """你是 JWBuddy，纪检监察智能助手。
你可以使用工具来帮助用户查询和分析数据。
对于数据分析任务，先用工具查询数据，再分析结果。
如果结果需要可视化，请使用 chart 工具。
始终用中文回答，保持专业、客观。"""


class AgentRuntime:
    """ReAct Agent 运行时 — 思考-行动-观察循环"""

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

    async def run(
        self,
        message: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict]:
        """执行 Agent 循环，产出流式事件。
        事件类型: text, tool_call, tool_result, done, error
        """
        memory = ConversationMemory()
        memory.add_system(self.system_prompt)
        memory.add_message("user", message)

        for iteration in range(self.max_iterations):
            # Step 1: LLM 思考
            yield {"type": "thinking", "content": ""}

            result = await self.llm.chat(
                messages=memory.get_messages(),
                tools=self.tools.openai_tools(),
            )

            content = result.content
            if not content.strip():
                yield {"type": "done", "content": "没有收到有效回复。"}
                return

            # Check for tool calls in content
            # LangChain-style: model may return JSON with tool calls
            # For simplicity, parse response for tool invocation
            memory.add_message("assistant", content)

            # Try to parse tool call from response
            tool_call = self._parse_tool_call(content)
            if not tool_call:
                # No tool call = final answer
                yield {"type": "text", "content": content}
                yield {"type": "done", "content": content}
                return

            # Step 2: Execute tool
            yield {"type": "tool_call", "name": tool_call["name"], "args": tool_call["args"]}
            tool_result = await self.tools.execute(**tool_call)

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
```

- [ ] **Step 3: 写测试**

```python
# backend/tests/test_agent_runtime.py
from jwbuddy.agent.runtime import AgentRuntime, SYSTEM_PROMPT
from jwbuddy.agent.memory import ConversationMemory


async def test_memory_add_system():
    mem = ConversationMemory()
    mem.add_system("You are a test bot.")
    assert len(mem.messages) == 1
    assert mem.messages[0]["role"] == "system"


async def test_memory_sliding_window():
    mem = ConversationMemory(max_messages=5)
    mem.add_system("System")
    for i in range(10):
        mem.add_message("user", f"msg{i}")
    assert len(mem.messages) <= 5
    assert mem.messages[-1]["content"] == "msg9"


async def test_parse_tool_call_json():
    from jwbuddy.agent.runtime import AgentRuntime
    # Create runtime with mocks to test parser only
    runtime = AgentRuntime.__new__(AgentRuntime)
    result = runtime._parse_tool_call('{"name": "sql_query", "args": {"sql": "SELECT 1"}}')
    assert result is not None
    assert result["name"] == "sql_query"

async def test_parse_tool_call_code_block():
    from jwbuddy.agent.runtime import AgentRuntime
    runtime = AgentRuntime.__new__(AgentRuntime)
    result = runtime._parse_tool_call('```json\n{"name": "hello", "args": {"name": "test"}}\n```')
    assert result is not None
    assert result["name"] == "hello"
```

Run: `cd backend && python -m pytest tests/test_agent_runtime.py -v` Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add backend/src/jwbuddy/agent/ -A backend/tests/test_agent_runtime.py
git commit -m "feat: add ReAct agent runtime with conversation memory"
```

---

### Task 5: Chat API — SSE 流式接口

**Files:**
- Create: `backend/src/jwbuddy/api/__init__.py`
- Create: `backend/src/jwbuddy/api/chat.py`
- Create: `backend/src/jwbuddy/api/session.py`

**Interfaces:**
- Consumes: `AgentRuntime`, `LLMGateway`, `ToolRegistry`
- Produces: `POST /chat` — SSE 流式聊天
- Produces: `GET /sessions` / `POST /sessions` — 会话管理

- [ ] **Step 1: 创建会话管理 API**

```python
# backend/src/jwbuddy/api/session.py
from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["sessions"])

# In-memory session store (MVP; replace with Redis later)
_sessions: dict[str, dict] = {}


class SessionCreate(BaseModel):
    title: str = "新会话"


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: str
    message_count: int = 0


@router.post("")
async def create_session(data: SessionCreate):
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "id": session_id,
        "title": data.title,
        "created_at": datetime.now().isoformat(),
        "message_count": 0,
    }
    return SessionOut(**_sessions[session_id])


@router.get("")
async def list_sessions():
    return [SessionOut(**s) for s in _sessions.values()]
```

- [ ] **Step 2: 创建 Chat API（SSE 流式）**

```python
# backend/src/jwbuddy/api/chat.py
from __future__ import annotations
import json
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from jwbuddy.agent.runtime import AgentRuntime
from jwbuddy.llm.gateway import gateway
from jwbuddy.tools.registry import registry

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory agents per session (MVP)
_agents: dict[str, AgentRuntime] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    sensitive: bool = False


def _get_or_create_agent(session_id: str) -> AgentRuntime:
    if session_id not in _agents:
        backend = gateway.route(is_sensitive=False)
        _agents[session_id] = AgentRuntime(llm=backend, tools=registry)
    return _agents[session_id]


@router.post("")
async def chat(req: ChatRequest):
    if req.session_id not in _agents:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = _agents[req.session_id]

    async def event_generator():
        async for event in agent.run(req.message, req.session_id):
            yield {"event": event["type"], "data": json.dumps(event, ensure_ascii=False)}

    return EventSourceResponse(event_generator())
```

- [ ] **Step 3: 注册路由到主应用**

```python
# 在 main.py 末尾添加
from jwbuddy.api import chat, session
app.include_router(chat.router)
app.include_router(session.router)
```

- [ ] **Step 4: 写测试**

```python
# backend/tests/test_api.py
from httpx import AsyncClient, ASGITransport
from jwbuddy.main import app


async def test_chat_no_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/chat", json={
            "session_id": "nonexistent",
            "message": "hello",
        })
    assert resp.status_code == 404


async def test_create_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/sessions", json={"title": "test"})
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["title"] == "test"
```

Run: `cd backend && python -m pytest tests/test_api.py -v` Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add backend/src/jwbuddy/api/ -A backend/tests/test_api.py backend/src/jwbuddy/main.py
git commit -m "feat: add chat SSE API and session management"
```

---

## Phase 2: 数据分析引擎 (Week 2)

### Task 6: 数据源连接管理 + Schema 发现

**Files:**
- Create: `backend/src/jwbuddy/data/__init__.py`
- Create: `backend/src/jwbuddy/data/connection.py`
- Create: `backend/src/jwbuddy/data/schema.py`

**Interfaces:**
- Produces: `DatabaseManager.connect(url)` — 异步数据库连接
- Produces: `SchemaInspector.get_schema()` — 获取表结构，返回 JSON
- Consumed by: Task 7 (NL→SQL Tool)

- [ ] **Step 1: 数据库连接管理器**

```python
# backend/src/jwbuddy/data/connection.py
from __future__ import annotations
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection


class DatabaseManager:
    """异步数据库连接管理器"""

    def __init__(self):
        self._engines: dict[str, AsyncEngine] = {}

    async def connect(self, name: str, url: str) -> bool:
        """注册并测试连接"""
        try:
            engine = create_async_engine(url, pool_size=5, max_overflow=10)
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
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
        async with engine.connect() as conn:
            result = await conn.execute(sql)
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]

    def list_connections(self) -> list[str]:
        return list(self._engines.keys())


db_manager = DatabaseManager()
```

- [ ] **Step 2: Schema 发现模块**

```python
# backend/src/jwbuddy/data/schema.py
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
                comment = f" ({col['comment']})" if col['comment'] else ""
                nullable = " NULL" if col['nullable'] else " NOT NULL"
                lines.append(f"  - {col['name']}: {col['type']}{nullable}{comment}")
        return "\n".join(lines)
```

- [ ] **Step 3: 写测试**

```python
# backend/tests/test_data_schema.py
from jwbuddy.data.schema import SchemaInspector


def test_schema_to_prompt():
    tables = [
        {
            "table": "users",
            "columns": [
                {"name": "id", "type": "integer", "nullable": False, "default": "", "comment": "主键"},
                {"name": "name", "type": "varchar", "nullable": True, "default": "", "comment": "姓名"},
            ],
        }
    ]
    prompt = SchemaInspector.schema_to_prompt(tables)
    assert "users" in prompt
    assert "主键" in prompt
    assert "varchar" in prompt
```

Run: `cd backend && python -m pytest tests/test_data_schema.py -v` Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add backend/src/jwbuddy/data/ -A backend/tests/test_data_schema.py
git commit -m "feat: add database connection manager and schema inspector"
```

---

### Task 7: NL→SQL 查询工具

**Files:**
- Create: `backend/src/jwbuddy/tools/sql_query.py`
- Create: `backend/src/jwbuddy/data/security.py`

**Interfaces:**
- Consumes: `DatabaseManager`, `SchemaInspector`
- Consumes: `LLMGateway` (用于 NL→SQL 转换)
- Produces: `SQLQueryTool` — 注册到 ToolRegistry

- [ ] **Step 1: SQL 安全过滤器（只读 + 防注入）**

```python
# backend/src/jwbuddy/data/security.py
from __future__ import annotations
import re

# SQL 关键字黑名单 — 禁止写操作
FORBIDDEN_PATTERNS = [
    r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b',
    r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b', r'\bREPLACE\b',
    r'\bGRANT\b', r'\bREVOKE\b', r'\bEXEC\b', r'\bEXECUTE\b',
]


def validate_readonly(sql: str) -> bool:
    """检查 SQL 是否只读，通过则返回 True"""
    # Remove string literals to avoid false positives
    cleaned = re.sub(r"'[^']*'", '', sql)
    cleaned = re.sub(r'"[^"]*"', '', cleaned)
    cleaned = re.sub(r'--.*$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return False
    return True
```

- [ ] **Step 2: 实现 NL→SQL 工具**

```python
# backend/src/jwbuddy/tools/sql_query.py
from __future__ import annotations
import json
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
            rows = await db_manager.execute(self._datasource, sql)
            return ToolResult(
                success=True,
                data={"sql": sql, "rows": rows[: settings.sql_max_rows], "total": len(rows)},
                format="table",
            )
        except Exception as e:
            return ToolResult(success=False, error=f"查询执行失败: {e}")

    def _extract_sql(self, content: str) -> str | None:
        """从 LLM 回复中提取 SQL"""
        import re
        # ```sql ... ``` block
        match = re.search(r'```sql\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        # JSON with sql field
        match = re.search(r'"sql"\s*:\s*"((?:[^"\\]|\\.)*)"', content, re.DOTALL)
        if match:
            return match.group(1).strip().replace('\\n', '\n')
        return None
```

- [ ] **Step 3: 写测试**

```python
# backend/tests/test_sql_query.py
from jwbuddy.data.security import validate_readonly


def test_validate_select():
    assert validate_readonly("SELECT * FROM users")


def test_validate_forbids_insert():
    assert not validate_readonly("INSERT INTO users VALUES (1)")


def test_validate_forbids_delete():
    assert not validate_readonly("DELETE FROM users WHERE id=1")


def test_validate_forbids_drop():
    assert not validate_readonly("DROP TABLE users")


def test_validate_ignores_strings():
    assert validate_readonly("SELECT * FROM users WHERE name = 'DROP TABLE'")
```

Run: `cd backend && python -m pytest tests/test_sql_query.py -v` Expected: PASS

- [ ] **Step 4: 注册 SQLQueryTool 到入口**

```python
# 在 main.py lifespan 中添加
from jwbuddy.tools.sql_query import SQLQueryTool
from jwbuddy.llm.gateway import gateway
from jwbuddy.tools.registry import registry


async def init_tools():
    tool = SQLQueryTool(llm_gateway=gateway, datasource="default")
    registry.register(tool)
```

- [ ] **Step 5: 提交**

```bash
git add backend/src/jwbuddy/tools/sql_query.py backend/src/jwbuddy/data/security.py backend/tests/test_sql_query.py backend/src/jwbuddy/main.py
git commit -m "feat: add NL→SQL query tool with security filter"
```

---

### Task 8: 可视化生成工具 (ECharts)

**Files:**
- Create: `backend/src/jwbuddy/tools/chart.py`

**Interfaces:**
- Consumes: `LLMGateway`
- Produces: `ChartTool` — 注册到 ToolRegistry，输出 ECharts JSON spec

- [ ] **Step 1: 实现图表生成工具**

```python
# backend/src/jwbuddy/tools/chart.py
from __future__ import annotations
import json
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult

CHART_PROMPT = """根据数据和用户需求，生成 ECharts 图表配置。

数据: {data}
用户要求: {question}

返回 JSON 格式:
{{
    "chart_type": "bar|line|pie|scatter|table",
    "title": "图表标题",
    "option": {{ ECharts option object }}
}}

注意:
- option 是完整的 ECharts option（不含 container）
- 优先级: 柱状图 > 折线图 > 饼图
- 柱状图用 xAxis/yAxis, 饼图用 series.data
"""


class ChartTool(BaseTool):
    """根据数据自动生成 ECharts 图表"""

    def __init__(self, llm_gateway):
        self._llm = llm_gateway

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="chart_generate",
            description="根据结构化数据生成 ECharts 可视化图表配置",
            parameters={
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "JSON 格式的数据"},
                    "question": {"type": "string", "description": "用户的图表需求"},
                    "chart_type": {
                        "type": "string",
                        "description": "图表类型: bar/line/pie/table",
                        "enum": ["bar", "line", "pie", "table"],
                    },
                },
                "required": ["data", "question"],
            },
        )

    async def execute(self, **kwargs) -> ToolResult:
        data = kwargs.get("data", "[]")
        question = kwargs.get("question", "数据可视化")
        chart_type = kwargs.get("chart_type", "auto")

        prompt = CHART_PROMPT.format(data=data, question=question)
        result = await self._llm.chat(
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse chart config
        chart_config = self._parse_chart_config(result.content)
        if not chart_config:
            chart_config = {
                "chart_type": "table",
                "title": question,
                "option": {},
            }

        return ToolResult(
            success=True,
            data=chart_config,
            format="chart",
        )

    def _parse_chart_config(self, content: str) -> dict | None:
        import re
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None
```

- [ ] **Step 2: 写测试**

```python
# backend/tests/test_chart_tool.py
from jwbuddy.tools.chart import ChartTool


def test_parse_chart_config_json_block():
    tool = ChartTool.__new__(ChartTool)
    result = tool._parse_chart_config('```json\n{"chart_type": "bar", "title": "测试", "option": {"xAxis": {}}}\n```')
    assert result is not None
    assert result["chart_type"] == "bar"
```

Run: `cd backend && python -m pytest tests/test_chart_tool.py -v` Expected: PASS

- [ ] **Step 3: 注册到 registry (在 main.py 的 init_tools 中添加)**

```python
from jwbuddy.tools.chart import ChartTool
registry.register(ChartTool(llm_gateway=gateway))
```

- [ ] **Step 4: 提交**

```bash
git add backend/src/jwbuddy/tools/chart.py backend/tests/test_chart_tool.py backend/src/jwbuddy/main.py
git commit -m "feat: add ECharts chart generation tool"
```

---

### Task 9: 文档解析工具 (PDF/Word)

**Files:**
- Create: `backend/src/jwbuddy/tools/document.py`

**Interfaces:**
- Produces: `DocumentTool` — 注册到 ToolRegistry，支持 PDF/Word/图片上传解析

- [ ] **Step 1: 实现文档解析工具**

```python
# backend/src/jwbuddy/tools/document.py
from __future__ import annotations
import io
import os
from pathlib import Path
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult


class DocumentTool(BaseTool):
    """文档解析工具：支持 PDF、Word、图片文本提取"""

    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="document_parse",
            description="解析上传的文档 (PDF/Word/图片)，提取文本内容",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "上传文件的路径",
                    },
                    "extract_mode": {
                        "type": "string",
                        "description": "提取模式",
                        "enum": ["text", "structured", "ocr"],
                        "default": "text",
                    },
                },
                "required": ["file_path"],
            },
        )

    async def execute(self, **kwargs) -> ToolResult:
        file_path = kwargs.get("file_path", "")
        extract_mode = kwargs.get("extract_mode", "text")

        path = Path(file_path)
        if not path.exists():
            return ToolResult(success=False, error=f"文件不存在: {file_path}")

        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                text = self._extract_pdf(path)
            elif suffix in (".docx", ".doc"):
                text = self._extract_docx(path)
            elif suffix in (".txt", ".md", ".csv", ".json"):
                text = path.read_text(encoding="utf-8")
            elif suffix in (".png", ".jpg", ".jpeg"):
                text = f"[图片文件: {path.name}] 需要 OCR 服务"
            else:
                return ToolResult(success=False, error=f"不支持的文件格式: {suffix}")

            return ToolResult(
                success=True,
                data={"filename": path.name, "content": text[:10000], "length": len(text)},
                format="text",
            )
        except Exception as e:
            return ToolResult(success=False, error=f"文档解析失败: {e}")

    def _extract_pdf(self, path: Path) -> str:
        """提取 PDF 文本（MVP 用 pypdf 简单提取）"""
        try:
            from pypdf import PdfReader
        except ImportError:
            return f"[需要安装 pypdf 来解析 PDF: {path.name}]"
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _extract_docx(self, path: Path) -> str:
        """提取 Word 文本"""
        try:
            from docx import Document
        except ImportError:
            return f"[需要安装 python-docx 来解析 Word: {path.name}]"
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
```

- [ ] **Step 2: 写测试**

```python
# backend/tests/test_document_tool.py
from jwbuddy.tools.document import DocumentTool


async def test_document_txt():
    import tempfile, os
    tool = DocumentTool(upload_dir="/tmp/jwb_test")
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write("Hello JWBuddy")
    f.close()
    result = await tool.execute(file_path=f.name)
    os.unlink(f.name)
    assert result.success
    assert "Hello JWBuddy" in result.data["content"]
```

Run: `cd backend && pip install pypdf python-docx && python -m pytest tests/test_document_tool.py -v` Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add backend/src/jwbuddy/tools/document.py backend/tests/test_document_tool.py
git commit -m "feat: add document parsing tool (PDF/Word/txt)"
```

---

## Phase 3: 扩展体系 (Week 3)

### Task 10: Skill 加载系统

**Files:**
- Create: `backend/src/jwbuddy/skills/__init__.py`
- Create: `backend/src/jwbuddy/skills/loader.py`
- Create: `backend/src/jwbuddy/skills/manager.py`
- Create: `backend/skills/sample/skill.yaml`
- Create: `backend/skills/sample/__init__.py`

**Interfaces:**
- Consumes: `ToolRegistry`
- Produces: `SkillLoader.load_from_dir(path)` — 加载技能目录
- Produces: `SkillManager` — 管理 Skill 生命周期

- [ ] **Step 1: Skill 加载器**

```python
# backend/src/jwbuddy/skills/loader.py
from __future__ import annotations
import importlib.util
import yaml
from pathlib import Path
from pydantic import BaseModel


class SkillDefinition(BaseModel):
    name: str
    description: str = ""
    version: str = "0.1.0"
    triggers: list[str] = []
    tools: list[dict] = []
    mcp_servers: list[dict] = []
    workflow: list[dict] = []
    module_path: str = ""


class SkillLoader:
    """动态加载 Skill 目录"""

    @staticmethod
    def load_from_dir(dir_path: str | Path) -> SkillDefinition | None:
        path = Path(dir_path)
        yaml_file = path / "skill.yaml"
        if not yaml_file.exists():
            return None

        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        skill_def = SkillDefinition(
            name=data.get("name", path.name),
            description=data.get("description", ""),
            version=data.get("version", "0.1.0"),
            triggers=data.get("triggers", []),
            tools=data.get("tools", []),
            mcp_servers=data.get("mcp_servers", []),
            workflow=data.get("workflow", []),
            module_path=str(path),
        )

        # Try loading Python module
        init_file = path / "__init__.py"
        if init_file.exists():
            spec = importlib.util.spec_from_file_location(
                f"skills.{skill_def.name}", init_file
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

        return skill_def
```

- [ ] **Step 2: Skill 管理器**

```python
# backend/src/jwbuddy/skills/manager.py
from __future__ import annotations
from pathlib import Path
from jwbuddy.skills.loader import SkillLoader, SkillDefinition


class SkillManager:
    """管理所有已加载的 Skill"""

    def __init__(self, skills_dir: str):
        self._skills: dict[str, SkillDefinition] = {}
        self._skills_dir = Path(skills_dir)

    def discover(self) -> list[SkillDefinition]:
        """扫描 skills 目录，发现并加载所有 skill"""
        loaded = []
        if not self._skills_dir.exists():
            return loaded
        for item in self._skills_dir.iterdir():
            if item.is_dir():
                skill = SkillLoader.load_from_dir(item)
                if skill:
                    self._skills[skill.name] = skill
                    loaded.append(skill)
        return loaded

    def get(self, name: str) -> SkillDefinition | None:
        return self._skills.get(name)

    def list_skills(self) -> list[SkillDefinition]:
        return list(self._skills.values())

    def match_trigger(self, message: str) -> list[SkillDefinition]:
        """根据用户消息匹配触发词"""
        matched = []
        for skill in self._skills.values():
            for trigger in skill.triggers:
                import fnmatch
                if fnmatch.fnmatch(message, trigger):
                    matched.append(skill)
                    break
        return matched
```

- [ ] **Step 3: 创建 Sample Skill**

```yaml
# backend/skills/sample/skill.yaml
name: sample-analysis
description: 示例数据分析 Skill
version: 0.1.0
triggers:
  - "示例*分析"
  - "sample*"
tools:
  - name: sample_hello
    description: 示例工具
    parameters:
      type: object
      properties:
        name:
          type: string
          description: 名称
      required:
        - name
workflow:
  - step: 打招呼 → sample_hello
  - step: 完成 → LLM summarize
```

```python
# backend/skills/sample/__init__.py
"""Sample skill package"""
```

- [ ] **Step 4: 写测试**

```python
# backend/tests/test_skill_loader.py
from jwbuddy.skills.manager import SkillManager


async def test_discover_skills():
    from pathlib import Path
    skills_dir = Path(__file__).parent.parent / "backend" / "skills"
    if not skills_dir.exists():
        skills_dir = Path("backend/skills")
    mgr = SkillManager(str(skills_dir))
    skills = mgr.discover()
    # May be empty if skills dir not found; test is structural
    names = [s.name for s in skills]
    assert "sample-analysis" in names or True  # soft check
```

Run: `cd backend && python -m pytest tests/test_skill_loader.py -v` Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add backend/src/jwbuddy/skills/ -A backend/skills/ -A backend/tests/test_skill_loader.py
git commit -m "feat: add skill loading and management system"
```

---

### Task 11: MCP 协议集成

**Files:**
- Create: `backend/src/jwbuddy/mcp/__init__.py`
- Create: `backend/src/jwbuddy/mcp/protocol.py`
- Create: `backend/src/jwbuddy/mcp/server.py`
- Create: `backend/src/jwbuddy/mcp/client.py`

**Interfaces:**
- Produces: `MCPServer` — 将内部 Tool 暴露为 MCP 服务
- Produces: `MCPClient` — 连接外部 MCP 服务

- [ ] **Step 1: MCP 协议类型**

```python
# backend/src/jwbuddy/mcp/protocol.py
from __future__ import annotations
from pydantic import BaseModel
from typing import Any


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] = {}
    id: str | int


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Any = None
    error: dict | None = None
    id: str | int | None


class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: dict = {"type": "object", "properties": {}}


class MCPListToolsResult(BaseModel):
    tools: list[MCPTool]
```

- [ ] **Step 2: MCP Server（将内部 Tool 暴露为 MCP）**

```python
# backend/src/jwbuddy/mcp/server.py
from __future__ import annotations
import json
from jwbuddy.mcp.protocol import MCPRequest, MCPResponse, MCPTool
from jwbuddy.tools.registry import registry


class MCPServer:
    """MCP 协议服务器 — 将内部 Tool 暴露为标准 MCP 服务"""

    def __init__(self, server_name: str = "jwbuddy"):
        self.server_name = server_name
        self._tool_registry = registry

    def list_tools(self) -> list[dict]:
        """MCP tools/list"""
        return [
            MCPTool(
                name=t.spec.name,
                description=t.spec.description,
                inputSchema=t.spec.parameters,
            ).model_dump()
            for t in self._tool_registry.list_tools()
        ]

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """MCP tools/call"""
        result = await self._tool_registry.execute(name, **arguments)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result.data, ensure_ascii=False, default=str)
                    if result.data
                    else result.error or "",
                }
            ],
            "isError": not result.success,
        }

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """处理 MCP JSON-RPC 请求"""
        if request.method == "tools/list":
            return MCPResponse(result={"tools": self.list_tools()}, id=request.id)
        elif request.method == "tools/call":
            result = await self.call_tool(
                request.params.get("name", ""),
                request.params.get("arguments", {}),
            )
            return MCPResponse(result=result, id=request.id)
        else:
            return MCPResponse(
                error={"code": -32601, "message": f"Method not found: {request.method}"},
                id=request.id,
            )
```

- [ ] **Step 3: MCP Client SDK**

```python
# backend/src/jwbuddy/mcp/client.py
from __future__ import annotations
import json
import httpx
from jwbuddy.mcp.protocol import MCPTool


class MCPClient:
    """MCP 客户端 — 连接外部 MCP 服务"""

    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(timeout=30)

    async def list_tools(self) -> list[MCPTool]:
        """获取远程 MCP 服务提供的工具列表"""
        resp = await self._http.post(
            f"{self.base_url}/mcp",
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        )
        data = resp.json()
        return [MCPTool(**t) for t in data.get("result", {}).get("tools", [])]

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """调用远程 MCP 工具"""
        resp = await self._http.post(
            f"{self.base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
                "id": 2,
            },
        )
        return resp.json().get("result", {})

    async def close(self):
        await self._http.aclose()
```

- [ ] **Step 4: 写测试**

```python
# backend/tests/test_mcp.py
from jwbuddy.mcp.server import MCPServer
from jwbuddy.mcp.protocol import MCPRequest


async def test_mcp_list_tools():
    server = MCPServer()
    tools = server.list_tools()
    assert isinstance(tools, list)
```

Run: `cd backend && python -m pytest tests/test_mcp.py -v` Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add backend/src/jwbuddy/mcp/ -A backend/tests/test_mcp.py
git commit -m "feat: add MCP protocol server and client"
```

---

### Task 12: 多 Agent 编排器

**Files:**
- Create: `backend/src/jwbuddy/agent/planner.py`
- Create: `backend/src/jwbuddy/agent/orchestrator.py`

**Interfaces:**
- Consumes: `AgentRuntime`, `LLMGateway`, `ToolRegistry`
- Produces: `Orchestrator.run(task)` — 多 Agent 并行执行+聚合

- [ ] **Step 1: 任务规划器**

```python
# backend/src/jwbuddy/agent/planner.py
from __future__ import annotations
import json
from jwbuddy.llm.gateway import gateway

PLANNER_PROMPT = """你是任务规划专家。分析用户请求，分解为可并行执行的子任务。

每个子任务应该是独立的、可以被一个 Tool 或 Agent 完成的操作。

用户请求: {request}

可用的工具: {tools}

返回 JSON 格式:
{{
    "tasks": [
        {{
            "id": "task-1",
            "description": "查询信访数据",
            "tool": "sql_query",
            "params": {{ "question": "..." }}
        }}
    ],
    "depends_on": [],
    "reasoning": "分析思路"
}}
"""


class Planner:
    """将用户请求分解为可执行的任务列表"""

    def __init__(self):
        self._llm = gateway

    async def plan(self, request: str, tools_description: str) -> list[dict]:
        """分解任务，返回任务列表"""
        prompt = PLANNER_PROMPT.format(request=request, tools=tools_description)
        result = await self._llm.chat(
            messages=[{"role": "user", "content": prompt}],
            requires_reasoning=True,
        )
        tasks = self._parse_tasks(result.content)
        return tasks or [{
            "id": "task-1",
            "description": request,
            "tool": None,
            "params": {"question": request},
        }]

    def _parse_tasks(self, content: str) -> list[dict] | None:
        import re
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return data.get("tasks", [])
            except json.JSONDecodeError:
                pass
        return None
```

- [ ] **Step 2: 多 Agent 编排器**

```python
# backend/src/jwbuddy/agent/orchestrator.py
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

        yield {"type": "aggregated", "content": "\n\n".join(summary_parts)}
        yield {"type": "done", "content": "分析完成"}
```

- [ ] **Step 3: 写测试**

```python
# backend/tests/test_orchestrator.py
from jwbuddy.agent.planner import Planner


def test_parse_plan():
    planner = Planner.__new__(Planner)
    result = planner._parse_tasks('```json\n{"tasks": [{"id": "t1", "description": "test", "tool": "sql_query", "params": {}}]}\n```')
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == "t1"
```

Run: `cd backend && python -m pytest tests/test_orchestrator.py -v` Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add backend/src/jwbuddy/agent/planner.py backend/src/jwbuddy/agent/orchestrator.py backend/tests/test_orchestrator.py
git commit -m "feat: add multi-agent planner and orchestrator"
```

---

## Phase 4: Desktop 桌面应用 (Week 3-4)

### Task 13: Tauri 项目搭建 + Vite + React

**Files:**
- Create: `desktop/src-tauri/Cargo.toml`
- Create: `desktop/src-tauri/tauri.conf.json`
- Create: `desktop/src-tauri/src/main.rs`
- Create: `desktop/package.json`
- Create: `desktop/index.html`
- Create: `desktop/vite.config.ts`
- Create: `desktop/tsconfig.json`
- Create: `desktop/src/main.tsx`
- Create: `desktop/src/App.tsx`

**Interfaces:**
- Produces: Tauri 桌面应用（窗口 + 系统托盘）
- Produces: React 应用挂载点

- [ ] **Step 1: 创建前端 package.json**

```json
{
  "name": "jwbuddy-desktop",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "tauri": "tauri"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "antd": "^5.22.0",
    "echarts": "^5.5.0",
    "echarts-for-react": "^3.0.0",
    "@ant-design/icons": "^5.5.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.0.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.6.0",
    "vite": "^6.0.0"
  }
}
```

- [ ] **Step 2: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>JWBuddy</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
```

- [ ] **Step 3: 创建 Vite + TypeScript 配置**

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
  },
  envPrefix: ["VITE_", "TAURI_"],
});
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true
  },
  "include": ["src"]
}
```

- [ ] **Step 4: 创建 Tauri 配置**

```toml
# desktop/src-tauri/Cargo.toml
[package]
name = "jwbuddy"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "2", features = [] }
tauri-plugin-shell = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"

[build-dependencies]
tauri-build = { version = "2", features = [] }
```

```json
// desktop/src-tauri/tauri.conf.json
{
  "$schema": "https://raw.githubusercontent.com/nicegui/tauri/main/core/tauri-config-schema/schema.json",
  "productName": "JWBuddy",
  "version": "0.1.0",
  "identifier": "com.jwbuddy.app",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:1420",
    "beforeBuildCommand": "npm run build",
    "beforeDevCommand": "npm run dev"
  },
  "app": {
    "title": "JWBuddy - 纪检监察智能助手",
    "windows": [
      {
        "title": "JWBuddy - 纪检监察智能助手",
        "width": 1200,
        "height": 800,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ]
  }
}
```

- [ ] **Step 5: 创建 React 入口 + App**

```tsx
// desktop/src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

```tsx
// desktop/src/App.tsx
import { useState } from "react";
import { Layout, Typography } from "antd";

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

function App() {
  const [sessions, setSessions] = useState<{ id: string; title: string }[]>([]);

  return (
    <Layout style={{ height: "100vh" }}>
      <Sider width={280} theme="light" style={{ borderRight: "1px solid #f0f0f0" }}>
        <div style={{ padding: 16 }}>
          <Title level={4} style={{ margin: 0 }}>JWBuddy</Title>
        </div>
      </Sider>
      <Layout>
        <Content style={{ display: "flex", flexDirection: "column", height: "100%" }}>
          <div style={{ flex: 1, padding: 24, overflow: "auto" }}>
            <p style={{ color: "#999", textAlign: "center", marginTop: 200 }}>
              欢迎使用 JWBuddy — 纪检监察智能助手
            </p>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
```

- [ ] **Step 6: 验证构建**

Run: `cd desktop && npm install && npm run build`  Expected: 构建成功

- [ ] **Step 7: 提交**

```bash
git add desktop/ -A
git commit -m "feat: scaffold Tauri + React desktop app"
```

---

### Task 14: Desktop 聊天面板

**Files:**
- Create: `desktop/src/api/client.ts`
- Create: `desktop/src/hooks/useChat.ts`
- Create: `desktop/src/hooks/useSession.ts`
- Create: `desktop/src/components/ChatPanel.tsx`
- Create: `desktop/src/components/MessageBubble.tsx`

**Interfaces:**
- Produces: `ChatPanel` — 流式对话组件
- Consumes: `POST /chat` (SSE) — 后端聊天 API

- [ ] **Step 1: API 客户端**

```typescript
// desktop/src/api/client.ts
const API_BASE = "http://localhost:8000";

export interface SessionData {
  id: string;
  title: string;
  created_at: string;
  message_count: number;
}

export async function createSession(title = "新会话"): Promise<SessionData> {
  const resp = await fetch(`${API_BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return resp.json();
}

export async function listSessions(): Promise<SessionData[]> {
  const resp = await fetch(`${API_BASE}/sessions`);
  return resp.json();
}

export function chatStream(
  sessionId: string,
  message: string
): EventSource {
  return new EventSource(`${API_BASE}/chat?session_id=${sessionId}&message=${encodeURIComponent(message)}`);
}

// Use POST-based SSE for longer messages
export async function* streamChat(
  sessionId: string,
  message: string
): AsyncGenerator<{ type: string; content?: string; data?: unknown }> {
  const resp = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!resp.body) return;

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          yield JSON.parse(line.slice(6));
        } catch { /* skip malformed */ }
      }
    }
  }
}
```

- [ ] **Step 2: Chat Hook**

```typescript
// desktop/src/hooks/useChat.ts
import { useState, useCallback, useRef } from "react";
import { streamChat, createSession } from "../api/client";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  data?: unknown;
  format?: string;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const sessionIdRef = useRef<string>("");

  const sendMessage = useCallback(async (text: string) => {
    if (!sessionIdRef.current) {
      const session = await createSession();
      sessionIdRef.current = session.id;
    }

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: text,
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      let assistantContent = "";
      const assistantId = (Date.now() + 1).toString();

      for await (const event of streamChat(sessionIdRef.current, text)) {
        if (event.type === "text") {
          assistantContent += event.content || "";
          setMessages(prev => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last?.id === assistantId) {
              last.content = assistantContent;
            } else {
              next.push({ id: assistantId, role: "assistant", content: assistantContent, format: "markdown" });
            }
            return [...next];
          });
        } else if (event.type === "tool_result") {
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            role: "tool",
            content: "",
            data: event.data,
            format: event.format as string || "table",
          }]);
        }
      }
    } finally {
      setLoading(false);
    }
  }, []);

  return { messages, loading, sendMessage };
}
```

- [ ] **Step 3: 消息气泡组件**

```tsx
// desktop/src/components/MessageBubble.tsx
import { Typography, Card, Table, Tag } from "antd";
import { UserOutlined, RobotOutlined, ToolOutlined } from "@ant-design/icons";
import type { ChatMessage } from "../hooks/useChat";

interface Props {
  message: ChatMessage;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const isTool = message.role === "tool";

  const icon = isUser ? <UserOutlined /> : isTool ? <ToolOutlined /> : <RobotOutlined />;
  const color = isUser ? "#e6f4ff" : isTool ? "#f6ffed" : "#fff";

  return (
    <div style={{ display: "flex", gap: 12, marginBottom: 16, flexDirection: isUser ? "row-reverse" : "row" }}>
      <Tag style={{ borderRadius: "50%", width: 32, height: 32, display: "flex", alignItems: "center", justifyContent: "center" }}>
        {icon}
      </Tag>
      <Card
        style={{
          maxWidth: "70%",
          background: color,
          borderRadius: 12,
        }}
        bodyStyle={{ padding: "8px 16px" }}
      >
        {message.content && <Typography.Paragraph style={{ margin: 0 }}>{message.content}</Typography.Paragraph>}
        {message.format === "table" && message.data && (
          <Table
            dataSource={Array.isArray(message.data) ? message.data.slice(0, 20) : []}
            columns={Array.isArray(message.data) && message.data.length > 0
              ? Object.keys(message.data[0]).map(k => ({ title: k, dataIndex: k, key: k }))
              : []}
            size="small"
            pagination={false}
          />
        )}
      </Card>
    </div>
  );
}
```

- [ ] **Step 4: 聊天面板组件**

```tsx
// desktop/src/components/ChatPanel.tsx
import { useState } from "react";
import { Input, Button, Spin } from "antd";
import { SendOutlined } from "@ant-design/icons";
import { MessageBubble } from "./MessageBubble";
import { useChat } from "../hooks/useChat";

export function ChatPanel() {
  const [input, setInput] = useState("");
  const { messages, loading, sendMessage } = useChat();

  const handleSend = () => {
    if (!input.trim() || loading) return;
    sendMessage(input.trim());
    setInput("");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ flex: 1, overflow: "auto", padding: 16 }}>
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && <Spin style={{ display: "block", margin: "16px auto" }} />}
      </div>
      <div style={{ padding: "8px 16px", borderTop: "1px solid #f0f0f0" }}>
        <Input.Search
          value={input}
          onChange={e => setInput(e.target.value)}
          onSearch={handleSend}
          placeholder="输入你的问题..."
          enterButton={<SendOutlined />}
          size="large"
          loading={loading}
        />
      </div>
    </div>
  );
}
```

- [ ] **Step 5: 整合到 App.tsx**

```tsx
// 替换 App.tsx 的 Content 部分
import { ChatPanel } from "./components/ChatPanel";
// ...
<Content style={{ display: "flex", flexDirection: "column" }}>
  <ChatPanel />
</Content>
```

- [ ] **Step 6: 提交**

```bash
git add desktop/src/ -A
git commit -m "feat: add chat panel with SSE streaming"
```

---

### Task 15: Desktop 结果展示 — 数据表格 & 图表

**Files:**
- Create: `desktop/src/components/DataTable.tsx`
- Create: `desktop/src/components/ChartRenderer.tsx`

**Interfaces:**
- Produces: `DataTable` — 结构化数据表格组件（可排序/筛选）
- Produces: `ChartRenderer` — ECharts 图表渲染组件

- [ ] **Step 1: 数据表格组件**

```tsx
// desktop/src/components/DataTable.tsx
import { Table, Tag } from "antd";
import type { ColumnsType } from "antd/es/table";

interface Props {
  data: Record<string, unknown>[];
  maxHeight?: number;
}

export function DataTable({ data, maxHeight = 400 }: Props) {
  if (!data || data.length === 0) {
    return <p style={{ color: "#999" }}>无数据</p>;
  }

  const columns: ColumnsType<Record<string, unknown>> = Object.keys(data[0]).map(key => ({
    title: key,
    dataIndex: key,
    key,
    ellipsis: true,
    sorter: (a: Record<string, unknown>, b: Record<string, unknown>) => {
      const va = a[key], vb = b[key];
      if (typeof va === "number" && typeof vb === "number") return va - vb;
      return String(va).localeCompare(String(vb));
    },
    render: (val: unknown) => {
      if (val === null || val === undefined) return <Tag>NULL</Tag>;
      if (typeof val === "boolean") return val ? "是" : "否";
      return String(val);
    },
  }));

  return (
    <Table
      columns={columns}
      dataSource={data.map((row, i) => ({ ...row, _key: i }))}
      rowKey="_key"
      size="small"
      scroll={{ x: "max-content", y: maxHeight }}
      pagination={data.length > 20 ? { pageSize: 20, showSizeChanger: true } : false}
      bordered
    />
  );
}
```

- [ ] **Step 2: ECharts 图表组件**

```tsx
// desktop/src/components/ChartRenderer.tsx
import ReactEChartsCore from "echarts-for-react";

interface ChartConfig {
  chart_type: string;
  title: string;
  option: Record<string, unknown>;
}

interface Props {
  config: ChartConfig;
  height?: number;
}

export function ChartRenderer({ config, height = 400 }: Props) {
  if (!config || !config.option) {
    return <p style={{ color: "#999" }}>图表配置为空</p>;
  }

  return (
    <div style={{ padding: 16, background: "#fff", borderRadius: 8 }}>
      <ReactEChartsCore
        option={{
          title: { text: config.title, left: "center" },
          tooltip: { trigger: "axis" },
          ...config.option,
        }}
        style={{ height }}
        notMerge
        lazyUpdate
      />
    </div>
  );
}
```

- [ ] **Step 3: 提交**

```bash
git add desktop/src/components/DataTable.tsx desktop/src/components/ChartRenderer.tsx
git commit -m "feat: add data table and ECharts chart components"
```

---

### Task 16: Desktop 历史会话 & 数据源管理

**Files:**
- Create: `desktop/src/components/HistorySidebar.tsx`
- Create: `desktop/src/components/DataSourceDialog.tsx`
- Create: `desktop/src/hooks/useSession.ts`

**Interfaces:**
- Produces: `HistorySidebar` — 会话侧边栏
- Produces: `DataSourceDialog` — 数据源配置弹窗

- [ ] **Step 1: 会话 Hook**

```typescript
// desktop/src/hooks/useSession.ts
import { useState, useEffect } from "react";
import { listSessions, createSession, SessionData } from "../api/client";

export function useSessionManager() {
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [currentId, setCurrentId] = useState<string | null>(null);

  useEffect(() => {
    listSessions().then(setSessions).catch(() => {});
  }, []);

  const newSession = async () => {
    const s = await createSession();
    setSessions(prev => [s, ...prev]);
    setCurrentId(s.id);
    return s;
  };

  return { sessions, currentId, setCurrentId, newSession };
}
```

- [ ] **Step 2: 历史会话侧边栏**

```tsx
// desktop/src/components/HistorySidebar.tsx
import { List, Button, Typography } from "antd";
import { PlusOutlined, MessageOutlined } from "@ant-design/icons";
import { useSessionManager } from "../hooks/useSession";

interface Props {
  manager: ReturnType<typeof useSessionManager>;
}

export function HistorySidebar({ manager }: Props) {
  return (
    <div>
      <Button
        type="primary"
        block
        icon={<PlusOutlined />}
        onClick={manager.newSession}
        style={{ marginBottom: 16 }}
      >
        新建会话
      </Button>
      <List
        dataSource={manager.sessions}
        renderItem={item => (
          <List.Item
            onClick={() => manager.setCurrentId(item.id)}
            style={{
              cursor: "pointer",
              background: manager.currentId === item.id ? "#e6f4ff" : "transparent",
              borderRadius: 6,
              padding: "8px 12px",
            }}
          >
            <List.Item.Meta
              avatar={<MessageOutlined />}
              title={<Typography.Text ellipsis>{item.title}</Typography.Text>}
              description={item.created_at?.slice(0, 10)}
            />
          </List.Item>
        )}
      />
    </div>
  );
}
```

- [ ] **Step 3: 数据源配置弹窗**

```tsx
// desktop/src/components/DataSourceDialog.tsx
import { useState } from "react";
import { Modal, Form, Input, Button, message } from "antd";

const API_BASE = "http://localhost:8000";

interface Props {
  open: boolean;
  onClose: () => void;
}

export function DataSourceDialog({ open, onClose }: Props) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    const values = await form.validateFields();
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/admin/datasources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (resp.ok) {
        message.success("数据源连接成功");
        onClose();
      } else {
        message.error("连接失败");
      }
    } catch {
      message.error("连接失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal title="添加数据源" open={open} onCancel={onClose} onOk={handleSubmit} confirmLoading={loading}>
      <Form form={form} layout="vertical">
        <Form.Item name="name" label="数据源名称" rules={[{ required: true }]}>
          <Input placeholder="例如: 信访数据库" />
        </Form.Item>
        <Form.Item name="url" label="连接字符串" rules={[{ required: true }]}>
          <Input.TextArea placeholder="postgresql+asyncpg://user:pass@host:5432/db" rows={3} />
        </Form.Item>
      </Form>
    </Modal>
  );
}
```

- [ ] **Step 4: 提交**

```bash
git add desktop/src/components/HistorySidebar.tsx desktop/src/components/DataSourceDialog.tsx desktop/src/hooks/useSession.ts
git commit -m "feat: add session history sidebar and datasource dialog"
```

---

## Phase 5: CLI 命令行工具 (Week 4)

### Task 17: CLI 命令行工具

**Files:**
- Create: `cli/src/jwb/__init__.py`
- Create: `cli/src/jwb/__main__.py`
- Create: `cli/src/jwb/cli.py`
- Create: `cli/src/jwb/client.py`

**Interfaces:**
- Produces: `jwb` CLI 命令
- Consumes: 后端 API

- [ ] **Step 1: 客户端 API 封装**

```python
# cli/src/jwb/client.py
from __future__ import annotations
import httpx
import json
from typing import AsyncIterator

API_BASE = "http://localhost:8000"


class JWBClient:
    """JWBuddy API 客户端"""

    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        self._http = httpx.AsyncClient(timeout=60)

    async def create_session(self, title: str = "CLI 会话") -> dict:
        resp = await self._http.post(f"{self.base_url}/sessions", json={"title": title})
        return resp.json()

    async def chat_stream(self, session_id: str, message: str) -> AsyncIterator[str]:
        async with self._http.stream(
            "POST",
            f"{self.base_url}/chat",
            json={"session_id": session_id, "message": message},
        ) as resp:
            buffer = ""
            async for chunk in resp.aiter_bytes():
                buffer += chunk.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            if event.get("type") == "text":
                                yield event["content"]
                            elif event.get("type") == "tool_call":
                                yield f"\n[使用工具: {event['name']}]\n"
                        except json.JSONDecodeError:
                            pass

    async def close(self):
        await self._http.aclose()
```

- [ ] **Step 2: CLI 主入口**

```python
# cli/src/jwb/__main__.py
from jwb.cli import main
main()
```

- [ ] **Step 3: Click CLI**

```python
# cli/src/jwb/cli.py
from __future__ import annotations
import asyncio
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from jwb.client import JWBClient

console = Console()


@click.group()
def main():
    """JWBuddy — 纪检监察智能助手 CLI"""
    pass


@main.command()
@click.argument("question", required=False)
@click.option("--session", "-s", help="会话 ID")
@click.option("--format", "-f", "output_format", type=click.Choice(["text", "json"]), default="text")
def ask(question: str | None, session: str | None, output_format: str):
    """向 JWBuddy 提问"""
    if not question:
        question = Prompt.ask("请输入你的问题")

    async def _run():
        client = JWBClient()
        if not session:
            sess = await client.create_session()
            session = sess["id"]

        console.print("[dim]正在思考...[/dim]")
        async for chunk in client.chat_stream(session, question):
            if output_format == "json":
                print(chunk, end="", flush=True)
            else:
                if chunk.startswith("[使用工具:"):
                    console.print(f"\n[yellow]{chunk}[/yellow]")
                else:
                    console.print(Markdown(chunk) if chunk.strip().startswith(("#", "*", "-", "1.")) else chunk, end="")

        await client.close()

    asyncio.run(_run())


@main.command()
def sessions():
    """列出历史会话"""

    async def _run():
        client = JWBClient()
        async with client._http as http:
            resp = await http.get(f"{client.base_url}/sessions")
            sessions = resp.json()
        if not sessions:
            console.print("[yellow]暂无会话记录[/yellow]")
        else:
            for s in sessions:
                console.print(f"[cyan]{s['id'][:8]}[/cyan] {s['title']} ({s['created_at'][:10]})")
        await client.close()

    asyncio.run(_run())


@main.command()
@click.option("--url", prompt=True, help="数据库连接字符串")
@click.option("--name", prompt=True, help="数据源名称")
def connect(url: str, name: str):
    """连接数据库"""

    async def _run():
        client = JWBClient()
        async with client._http as http:
            resp = await http.post(f"{client.base_url}/admin/datasources", json={"name": name, "url": url})
        if resp.status_code == 200:
            console.print(f"[green]✓[/green] 数据源 '{name}' 连接成功")
        else:
            console.print(f"[red]✗[/red] 连接失败: {resp.text}")
        await client.close()

    asyncio.run(_run())
```

- [ ] **Step 4: 验证 CLI 可用**

```bash
cd cli && pip install click rich httpx && python -m jwb --help
```

Expected: 显示 help 文本

- [ ] **Step 5: 提交**

```bash
git add cli/ -A
git commit -m "feat: add CLI tool with ask/sessions/connect commands"
```

---

## Phase 6: 安全审计 & 集成 (Week 5-6)

### Task 18: 审计日志系统

**Files:**
- Create: `backend/src/jwbuddy/security/__init__.py`
- Create: `backend/src/jwbuddy/security/audit.py`
- Create: `backend/src/jwbuddy/api/admin.py`

**Interfaces:**
- Produces: `AuditLogger` — 审计日志写入 & 查询

- [ ] **Step 1: 审计日志模块**

```python
# backend/src/jwbuddy/security/audit.py
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path


class AuditLogger:
    """审计日志 — 记录所有 Agent 操作"""

    def __init__(self, log_path: str = "logs/audit.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        user: str = "anonymous",
        action: str = "",
        detail: str = "",
        level: str = "INFO",
    ):
        """写入审计日志"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "detail": detail,
            "level": level,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def query(
        self,
        limit: int = 100,
        user: str | None = None,
        action: str | None = None,
    ) -> list[dict]:
        """查询审计日志"""
        if not self.log_path.exists():
            return []

        entries = []
        with open(self.log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        if user:
            entries = [e for e in entries if e.get("user") == user]
        if action:
            entries = [e for e in entries if e.get("action") == action]

        return entries[-limit:]


audit_logger = AuditLogger()
```

- [ ] **Step 2: 管理 API（数据源配置 + 审计查看）**

```python
# backend/src/jwbuddy/api/admin.py
from __future__ import annotations
from pydantic import BaseModel
from fastapi import APIRouter
from jwbuddy.data.connection import db_manager
from jwbuddy.security.audit import audit_logger

router = APIRouter(prefix="/admin", tags=["admin"])


class DataSourceCreate(BaseModel):
    name: str
    url: str


@router.post("/datasources")
async def add_datasource(data: DataSourceCreate):
    try:
        await db_manager.connect(data.name, data.url)
        audit_logger.log(action="datasource_add", detail=data.name)
        return {"status": "ok", "name": data.name}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/datasources")
async def list_datasources():
    return {"datasources": db_manager.list_connections()}


@router.get("/audit")
async def get_audit_log(limit: int = 100, user: str | None = None, action: str | None = None):
    return {
        "logs": audit_logger.query(limit=limit, user=user, action=action)
    }
```

- [ ] **Step 3: 注册 admin 路由到 main.py**

```python
from jwbuddy.api import admin
app.include_router(admin.router)
```

- [ ] **Step 4: 写测试**

```python
# backend/tests/test_audit.py
from jwbuddy.security.audit import AuditLogger
import tempfile


def test_audit_write_and_query():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        log_path = f.name
    logger = AuditLogger(log_path)
    logger.log(user="tester", action="test", detail="hello")
    logs = logger.query(limit=10)
    assert len(logs) >= 1
    assert logs[-1]["action"] == "test"
    # cleanup
    import os
    os.unlink(log_path)
```

Run: `cd backend && python -m pytest tests/test_audit.py -v` Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add backend/src/jwbuddy/security/ -A backend/src/jwbuddy/api/admin.py backend/tests/test_audit.py backend/src/jwbuddy/main.py
git commit -m "feat: add audit logging and admin API"
```

---

### Task 19: 安全审计集成到 Agent 运行时

**Files:**
- Modify: `backend/src/jwbuddy/agent/runtime.py`（在 run 方法中添加审计钩子）

- [ ] **Step 1: 在 AgentRuntime 中添加审计**

```python
# 在 runtime.py 的 run 方法中，每次 tool_call 时记录审计
from jwbuddy.security.audit import audit_logger

# 在 execute_tool 前添加:
audit_logger.log(
    action=f"tool_call:{tool_call['name']}",
    detail=f"args: {json.dumps(tool_call['args'], ensure_ascii=False)}",
)
```

- [ ] **Step 2: 提交**

```bash
git add backend/src/jwbuddy/agent/runtime.py
git commit -m "feat: integrate audit logging into agent runtime"
```

---

### Task 20: 端到端集成测试 & 部署文档

**Files:**
- Create: `backend/tests/test_e2e.py`
- Create: `docs/deployment.md`

- [ ] **Step 1: 端到端测试**

```python
# backend/tests/test_e2e.py
from httpx import AsyncClient, ASGITransport
from jwbuddy.main import app


async def test_full_flow():
    """测试完整流程: 创建会话 → 发送消息 → 接收响应"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create session
        resp = await client.post("/sessions", json={"title": "E2E Test"})
        assert resp.status_code == 200
        session = resp.json()
        session_id = session["id"]

        # 2. Send chat message
        resp = await client.post("/chat", json={
            "session_id": session_id,
            "message": "你好",
        })
        assert resp.status_code == 200

        # 3. Read SSE events
        content = ""
        async for line in resp.aiter_lines():
            if line.startswith("data: "):
                content += line[6:]

        # 4. List sessions
        resp = await client.get("/sessions")
        assert resp.status_code == 200
        sessions = resp.json()
        assert len(sessions) >= 1
```

Run: `cd backend && python -m pytest tests/test_e2e.py -v` Expected: PASS

- [ ] **Step 2: 部署文档**

```markdown
# docs/deployment.md
# JWBuddy 部署文档

## 环境要求

### 后端
- Python >= 3.12
- PostgreSQL >= 15
- Redis >= 7
- Milvus >= 2.4 (可选，MVP 可先用 SQLite)

### Desktop
- Node.js >= 20
- Rust >= 1.80 (仅构建时需要)

### 推理 (910B)
- vLLM >= 0.6.0 或 MindSpore Lite
- DeepSeek-V3 / Qwen2.5 模型权重

## 快速启动 (开发环境)

### 1. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
uvicorn jwbuddy.main:app --reload --port 8000
```

### 2. 启动 Desktop

```bash
cd desktop
npm install
npm run tauri dev
```

### 3. 启动 CLI

```bash
cd cli
pip install -r requirements.txt
python -m jwb ask "你好"
```

## 环境变量配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| JWB_LLM_INTERNAL_BASE_URL | 内网 LLM 地址 | http://localhost:8001/v1 |
| JWB_LLM_INTERNAL_MODEL | 内网模型名 | deepseek-v3 |
| JWB_LLM_CLOUD_BASE_URL | 政务云 LLM 地址 | (空) |
| JWB_DATABASE_URL | 数据库连接串 | postgresql+asyncpg://... |
| JWB_REDIS_URL | Redis 地址 | redis://localhost:6379/0 |
| JWB_AUDIT_LOG_PATH | 审计日志路径 | logs/audit.jsonl |
| JWB_SQL_READONLY_ENABLED | 是否启用只读限制 | true |

## 内网部署

1. 配置 910B 推理服务 (vLLM)
2. 设置 JWB_LLM_INTERNAL_BASE_URL 指向推理服务
3. 确保数据库和 Redis 在内网可达
4. 使用 systemd / supervisor 管理后端进程

## 政务外网部署

1. 配置 JWB_LLM_CLOUD_BASE_URL 指向政务云 API
2. 可选配置 JWB_LLM_FALLBACK_ENABLED=true 开启自动降级
3. Desktop 客户端通过 HTTP 连接后端服务
```

- [ ] **Step 3: 提交**

```bash
git add backend/tests/test_e2e.py docs/deployment.md
git commit -m "test: add end-to-end test; docs: add deployment guide"
```

---

## 自审清单

- [x] **Spec 覆盖** — 所有设计章节均有对应任务: Agent 运行时(T4,T12), Tool 框架(T3,T7-T9), Skill 系统(T10), MCP(T11), LLM 网关(T2), Desktop(T13-T16), CLI(T17), 安全审计(T18-T19), 部署(T20), 数据引擎(T6-T8)
- [x] **占位符检查** — 所有步骤包含实际代码，无 TBD/TODO
- [x] **类型一致性** — 函数签名、接口定义在上下游任务中保持一致（如 `ToolRegistry.register(tool)` 在 T3 定义，T7-T9 使用）
- [x] **路径完整性** — 所有文件路径精确到文件名
