# JWBuddy — 纪检监察智能体客户端平台

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)](https://fastapi.tiangolo.com)
[![Tauri](https://img.shields.io/badge/Tauri-2.x-purple)](https://tauri.app)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

JWBuddy 是一套面向纪检监察部门的**通用智能体客户端平台**，类似 Claude Code / Codex / WorkBuddy，支持自然语言驱动的数据查询分析、文档编写、模型建设，具备 Skill/MCP/Tool 扩展体系和多智能体编排能力。

> 📌 **当前状态:** MVP 开发完成（**104 项测试全部通过**）
>
> 📖 **设计文档:** [`docs/superpowers/specs/2026-06-23-jwbuddy-agent-platform-design.md`](docs/superpowers/specs/2026-06-23-jwbuddy-agent-platform-design.md)
>
> 📋 **实施计划:** [`docs/superpowers/plans/2026-06-23-jwbuddy-mvp-plan.md`](docs/superpowers/plans/2026-06-23-jwbuddy-mvp-plan.md)

---

## 目录

- [项目定位](#项目定位)
- [核心架构](#核心架构)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [功能模块](#功能模块)
- [部署架构](#部署架构)
- [路线图](#路线图)

---

## 项目定位

为纪检监察部门打造一套**通用智能体客户端平台**：

- **自然语言驱动的数据分析** — 纪检人员用对话即可查询数据、发现异常、生成图表报告
- **插件化扩展体系** — 所有业务能力（养老、三资、招投标、教育、四风、信访等）以 Skill/MCP/Tool 形式接入
- **多形态客户端** — Desktop（主力工作台）、CLI（批量自动化）、App（移动查阅）
- **私有化部署** — 内网 910B 集群推理 + 政务云大模型双轨并行

### 目标用户

| 阶段 | 用户范围 | 规模 |
|------|---------|------|
| MVP 试点 | 某科室 | ~10 人 |
| 推广阶段 | 全省 21 市州纪检部门 | ~1000 人 |

### 部署环境

| 环境 | 说明 | 优先级 |
|------|------|--------|
| 政务外网 | 非敏感数据，政务云 LLM | 第一优先级 |
| 内网 | 涉密数据，910B 私有推理 | 第二优先级 |

---

## 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                   客户端层 (Client)                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Desktop   │  │    CLI     │  │    App     │            │
│  │  (Tauri)   │  │  (Click)   │  │  (Flutter) │            │
│  └─────┬──────┘  └─────┬──────┘  └──────┬─────┘            │
│        └───────────────┼────────────────┘                   │
│                   HTTP / WebSocket                          │
├─────────────────────────────────────────────────────────────┤
│                   Agent 运行时层 (Core)                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Orchestrator (多 Agent 调度 / 任务编排 / 会话管理)  │    │
│  ├─────────┬──────────┬──────────┬───────────────────┤    │
│  │ Planner │ Executor │  Memory  │  Tool Executor    │    │
│  └─────────┴──────────┴──────────┴───────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                  能力扩展层 (Extensibility)                   │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐     │
│  │   Skills   │  │  MCP Srv   │  │     Tools        │     │
│  │  (插件化)  │  │ (标准协议) │  │ (内置 + 自定义)  │     │
│  └────────────┘  └────────────┘  └──────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                 数据与推理层 (Data & Inference)               │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐     │
│  │ LLM 网关   │  │  向量库    │  │  数据源适配层    │     │
│  │(910B/云端) │  │ (Milvus)   │  │(SQL/文档/PDF/图) │     │
│  └────────────┘  └────────────┘  └──────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│    横切: 🔐 安全审计  │  📊 监控管理  │  ⚙️ 配置中心        │
└─────────────────────────────────────────────────────────────┘
```

### 核心设计原则

| 原则 | 说明 |
|------|------|
| **插件化优先** | 所有业务能力 = Skill/MCP/Tool，底座不耦合业务 |
| **国产化全栈** | 910B + DeepSeek/Qwen + 国产数据库适配 |
| **内外网分离** | 核心逻辑同构，数据源和模型分别适配 |
| **安全审计** | 所有 Agent 操作可追溯、可回放、可审批 |

---

## 快速开始

### 环境要求

- Python >= 3.12
- Node.js >= 20
- Rust >= 1.80（仅 Desktop 构建时需要）
- PostgreSQL >= 15（可选，MVP 可用 SQLite）
- Redis >= 7（可选）

### 1. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn jwbuddy.main:app --reload --port 8000
```

验证:

```bash
curl http://localhost:8000/health
# {"status":"ok","app":"JWBuddy"}
```

### 2. 启动 Desktop

```bash
cd desktop
npm install
npm run tauri dev
```

### 3. 使用 CLI

```bash
cd cli
pip install click rich httpx
python -m jwb ask "你好"
python -m jwb sessions
python -m jwb connect
```

### 运行测试

```bash
cd backend
python -m pytest -v
# 104 passed
```

---

## 项目结构

```
jwbuddy/
├── backend/                           # Python 后端
│   ├── src/jwbuddy/
│   │   ├── main.py                    # FastAPI 入口
│   │   ├── config.py                  # 配置管理
│   │   ├── agent/                     # Agent 运行时
│   │   │   ├── runtime.py             # ReAct Agent 循环
│   │   │   ├── orchestrator.py        # 多 Agent 编排
│   │   │   ├── planner.py             # 任务规划器
│   │   │   └── memory.py              # 会话记忆
│   │   ├── tools/                     # 工具系统
│   │   │   ├── base.py                # 工具基类
│   │   │   ├── registry.py            # 工具注册表
│   │   │   ├── sql_query.py           # NL→SQL 引擎
│   │   │   ├── chart.py               # 可视化生成
│   │   │   └── document.py            # 文档解析
│   │   ├── skills/                    # Skill 系统
│   │   │   ├── loader.py              # Skill 加载器
│   │   │   └── manager.py             # Skill 管理器
│   │   ├── mcp/                       # MCP 协议
│   │   │   ├── server.py              # MCP Server
│   │   │   └── client.py              # MCP Client
│   │   ├── llm/                       # LLM 网关
│   │   │   ├── gateway.py             # 路由网关
│   │   │   └── backends.py            # 后端实现
│   │   ├── data/                      # 数据层
│   │   │   ├── connection.py          # 数据库连接
│   │   │   ├── schema.py              # Schema 发现
│   │   │   └── security.py            # SQL 安全过滤
│   │   ├── security/
│   │   │   └── audit.py               # 审计日志
│   │   └── api/                       # API 层
│   │       ├── chat.py                # 聊天 SSE API
│   │       ├── session.py             # 会话管理
│   │       └── admin.py               # 管理 API
│   ├── skills/sample/                 # 示例 Skill
│   └── tests/                         # 54 项测试
├── desktop/                           # Desktop (Tauri + React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx          # 聊天面板
│   │   │   ├── MessageBubble.tsx      # 消息气泡
│   │   │   ├── DataTable.tsx          # 数据表格
│   │   │   ├── ChartRenderer.tsx      # 图表渲染
│   │   │   ├── HistorySidebar.tsx     # 历史会话
│   │   │   └── DataSourceDialog.tsx   # 数据源配置
│   │   ├── hooks/
│   │   │   ├── useChat.ts             # 聊天 Hook
│   │   │   └── useSession.ts          # 会话 Hook
│   │   └── api/client.ts              # API 客户端
│   └── src-tauri/                     # Tauri 壳
├── cli/                               # CLI 命令行工具
│   └── src/jwb/
│       ├── cli.py                     # Click 命令
│       └── client.py                  # API 客户端
└── docs/
    ├── superpowers/specs/              # 设计文档
    ├── superpowers/plans/              # 实施计划
    └── deployment.md                   # 部署指南
```

---

## 技术栈

| 领域 | 技术 |
|------|------|
| Agent 框架 | Python, FastAPI, Pydantic |
| LLM 网关 | OpenAI 兼容接口 (vLLM / 政务云 API) |
| 模型 | DeepSeek-V3, Qwen2.5, BGE-M3 |
| Desktop | Tauri 2.x, React 18, Ant Design 5 |
| CLI | Click, Rich |
| 可视化 | ECharts 5 |
| 协议 | MCP (Model Context Protocol) |
| 数据库 | PostgreSQL, SQLAlchemy 2.0 |
| 向量库 | Milvus |
| 缓存 | Redis |
| 部署 | Docker, Nginx |

---

## 功能模块

### 数据分析引擎

自然语言驱动的数据查询与分析：

```
用户提问 → NL→SQL 转换 (LLM + Schema 注入 + 安全过滤)
        → 数据查询执行 (SQL 校验 → 沙箱执行 → 结果封装)
        → 后处理展示 (LLM 分析 → 表格/图表/报告)
```

**MVP 内置工具:**

| 工具 | 说明 |
|------|------|
| `sql_query` | 自然语言 → SQL → 查询结构化数据 |
| `chart_generate` | 根据数据自动生成 ECharts 图表 |
| `document_parse` | PDF/Word/文本文件解析 |
| `vector_search` | 语义搜索（法规/案例库） |

### 多 Agent 编排

```
用户请求 → Planner 分解任务
          ├─ 单任务 → Agent 直接执行
          └─ 多任务 → Orchestrator → Worker Agent 并行执行
                                    → 结果聚合
```

### Skill / MCP / Tool 扩展体系

```
用户交互层 → Skills (面向业务场景编排)
               ├─ 养老资金分析 skill
               ├─ 招投标围标分析 skill
               └─ 信访分析 skill
               ↓
          Tools / MCP (原子能力执行)
               ├─ sql_query / vector_search
               ├─ document_parse / chart_generate
               └─ MCP Server (外部数据桥接)
```

### 安全体系

| 关注点 | 方案 |
|--------|------|
| SQL 安全 | 只读查询校验，禁止 DDL/DML，超时控制 |
| 审计日志 | 所有 Agent 操作全记录（谁、时间、内容、结果）|
| 路径安全 | 文件上传防路径遍历 |
| 认证 | Admin API Key 验证 |
| CORS | 白名单来源限制 |

---

## 部署架构

### 双环境部署

| 环境 | 组件 | 数据 |
|------|------|------|
| 政务外网 | Agent 服务 + 政务云 LLM + App | 非敏感数据 |
| 内网 | Agent 服务 + 910B 集群 + Milvus + PostgreSQL | 涉密数据 |
| 内外网之间 | 物理隔离 / 光闸 | 不互通 |

### MVP 推荐规格（10人试点）

| 组件 | 规格 |
|------|------|
| Agent 服务 | 8C 32G × 2 |
| 910B 推理 | 共享已有集群 |
| PostgreSQL | 4C 16G 500G |
| Milvus | 4C 16G |
| Desktop 客户端 | 普通办公 PC |

详细部署参见: [`docs/deployment.md`](docs/deployment.md)

---

## 配置

通过环境变量配置（前缀 `JWB_`）:

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `JWB_HOST` | 服务监听地址 | `0.0.0.0` |
| `JWB_PORT` | 服务端口 | `8000` |
| `JWB_LLM_INTERNAL_BASE_URL` | 内网 LLM 地址 | `http://localhost:8001/v1` |
| `JWB_LLM_INTERNAL_MODEL` | 内网模型名 | `deepseek-v3` |
| `JWB_LLM_CLOUD_BASE_URL` | 政务云 LLM 地址 | (空) |
| `JWB_DATABASE_URL` | 数据库连接串 | `postgresql+asyncpg://...` |
| `JWB_REDIS_URL` | Redis 地址 | `redis://localhost:6379/0` |
| `JWB_MILVUS_HOST` | Milvus 地址 | `localhost` |
| `JWB_AUDIT_LOG_PATH` | 审计日志路径 | `logs/audit.jsonl` |
| `JWB_SQL_READONLY_ENABLED` | SQL 只读限制 | `true` |
| `JWB_SQL_MAX_ROWS` | 查询最大行数 | `1000` |
| `JWB_SQL_TIMEOUT_SECONDS` | 查询超时秒数 | `30` |
| `JWB_ADMIN_API_KEY` | 管理 API 密钥 | (空) |

---

## 路线图

### ✅ MVP (已完成)

- [x] Python 后端框架 (FastAPI + 配置系统)
- [x] LLM 网关 (内网/云端双轨路由)
- [x] 工具框架 (BaseTool + ToolRegistry)
- [x] ReAct Agent 运行时（支持原生 function calling）
- [x] SSE 流式 Chat API + 会话管理
- [x] NL→SQL 数据分析引擎
- [x] ECharts 可视化生成
- [x] 文档解析 (PDF/Word/Excel/文本)
- [x] 文件上传 API（反路径遍历保护）
- [x] 文件内 SQL 查询引擎（xlsx/csv → SQLite）
- [x] Skill 加载与管理
- [x] 领域 Skill 样例（养老资金分析、招投标围标分析）
- [x] MCP 协议 Server/Client（含 HTTP Endpoint）
- [x] 多 Agent 编排器
- [x] Desktop 桌面应用 (Tauri + React + ECharts)
- [x] CLI 命令行工具 (Click + Rich)
- [x] 审计日志系统
- [x] Admin API（数据源管理 + 审计查询）
- [x] 104 项自动化测试

### 🚧 规划中

- [ ] 内网 910B 推理适配
- [ ] 政务云 LLM 对接
- [ ] 移动端 App (Flutter)
- [ ] 领域 Skill 开发（养老、三资、招投标、教育、四风、信访）
- [ ] OAuth2 + LDAP 认证集成
- [ ] 关联分析引擎（图数据库）
- [ ] Docker Compose 一键部署
- [ ] 全省 1000 人规模性能测试

---

## 协议

MIT License

---

*JWBuddy — 纪检监察智能助手*
