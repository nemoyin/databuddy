# JWBuddy 部署文档

## 环境要求

### 后端
- Python >= 3.12
- PostgreSQL >= 15
- Redis >= 7
- Milvus >= 2.4（可选，MVP 可先用 SQLite 替代）

### Desktop
- Node.js >= 20
- Rust >= 1.80（仅构建时需要，运行时不需要）

### CLI
- Python >= 3.12

### 推理（910B）
- vLLM >= 0.6.0 或 MindSpore Lite
- DeepSeek-V3 / Qwen2.5 模型权重

---

## 快速启动（开发环境）

### 1. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn jwbuddy.main:app --reload --port 8000
```

验证服务是否正常运行:

```bash
curl http://localhost:8000/health
# 预期: {"status":"ok","app":"JWBuddy"}
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

---

## 环境变量配置

所有环境变量统一使用 `JWB_` 前缀。

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `JWB_LLM_INTERNAL_BASE_URL` | 内网 LLM 服务地址 | `http://localhost:8001/v1` |
| `JWB_LLM_INTERNAL_MODEL` | 内网模型名称 | `deepseek-v3` |
| `JWB_LLM_INTERNAL_API_KEY` | 内网模型 API Key | (空) |
| `JWB_LLM_CLOUD_BASE_URL` | 政务云 LLM 服务地址 | (空) |
| `JWB_LLM_CLOUD_MODEL` | 政务云模型名称 | `qwen-plus` |
| `JWB_LLM_CLOUD_API_KEY` | 政务云模型 API Key | (空) |
| `JWB_LLM_FALLBACK_ENABLED` | 是否开启自动降级 | `true` |
| `JWB_DATABASE_URL` | 数据库连接串 | `postgresql+asyncpg://...` |
| `JWB_REDIS_URL` | Redis 地址 | `redis://localhost:6379/0` |
| `JWB_MILVUS_HOST` | Milvus 主机 | `localhost` |
| `JWB_MILVUS_PORT` | Milvus 端口 | `19530` |
| `JWB_AUDIT_LOG_PATH` | 审计日志文件路径 | `logs/audit.jsonl` |
| `JWB_SQL_READONLY_ENABLED` | 是否启用 SQL 只读限制 | `true` |
| `JWB_SQL_MAX_ROWS` | SQL 查询最大返回行数 | `1000` |
| `JWB_SQL_TIMEOUT_SECONDS` | SQL 查询超时时间 | `30` |
| `JWB_SKILLS_DIR` | 技能包目录路径 | `./skills` |
| `JWB_DATA_DIR` | 数据目录 | `data` |
| `JWB_DEBUG` | 调试模式 | `false` |

---

## 部署策略

### 内网部署（涉密环境）

适用于政务内网 / 涉密环境，所有组件部署在内网，不连接公网。

1. **部署 910B 推理服务**

   使用 vLLM 部署模型:

   ```bash
   # 在 910B 服务器上
   docker run --rm --gpus all \
     -v /path/to/models:/models \
     -p 8001:8001 \
     vllm/vllm-openai:latest \
     --model /models/deepseek-v3 \
     --tensor-parallel-size 8 \
     --port 8001
   ```

2. **配置后端环境变量**

   ```bash
   export JWB_LLM_INTERNAL_BASE_URL=http://910b-server:8001/v1
   export JWB_LLM_INTERNAL_MODEL=deepseek-v3
   export JWB_DATABASE_URL=postgresql+asyncpg://jwbuddy:password@db:5432/jwbuddy
   export JWB_REDIS_URL=redis://redis:6379/0
   export JWB_LLM_FALLBACK_ENABLED=false
   ```

3. **确保数据库和 Redis 在内网可达**

   - PostgreSQL 和 Redis 应部署在同一内网或通过专线连接。
   - 数据库连接使用最小权限账户。

4. **使用 systemd / supervisor 管理后端进程**

   systemd 示例 (`/etc/systemd/system/jwbuddy.service`):

   ```ini
   [Unit]
   Description=JWBuddy Backend
   After=network.target postgresql.service redis.service

   [Service]
   Type=simple
   User=jwbuddy
   WorkingDirectory=/opt/jwbuddy/backend
   Environment=JWB_LLM_INTERNAL_BASE_URL=http://910b-server:8001/v1
   ExecStart=/opt/jwbuddy/backend/.venv/bin/uvicorn jwbuddy.main:app --host 0.0.0.0 --port 8000
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

### 政务外网部署（非涉密环境）

适用于政务外网环境，可访问政务云 LLM API。

1. **配置政务云 LLM API**

   ```bash
   export JWB_LLM_CLOUD_BASE_URL=https://gov-cloud-api.example.com/v1
   export JWB_LLM_CLOUD_MODEL=qwen-plus
   export JWB_LLM_CLOUD_API_KEY=your-api-key
   ```

2. **可选: 开启自动降级**

   ```bash
   export JWB_LLM_FALLBACK_ENABLED=true
   ```

   开启后，当政务云 API 不可用时自动降级到内网 LLM。

3. **Desktop 客户端连接**

   Desktop 客户端通过 HTTP 连接后端服务。配置后端地址为内网可访问的域名或 IP。

### Docker Compose 部署（推荐）

项目根目录提供 `docker-compose.yml`，一键启动所有依赖服务:

```bash
docker compose up -d
```

包含的服务:
- `jwbuddy-backend` — FastAPI 应用
- `postgres` — 数据库
- `redis` — 缓存 / 会话存储
- `milvus` — 向量数据库（可选）

---

## 健康检查端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 服务存活检查 |

---

## 安全注意事项

1. **审计日志**: 默认输出到 `logs/audit.jsonl`，生产环境中建议挂载持久卷并配置日志轮转。
2. **SQL 只读**: 默认开启 `JWB_SQL_READONLY_ENABLED=true`，禁止非查询 SQL 操作。
3. **API Key 管理**: LLM API Key 通过环境变量注入，不得硬编码在代码或配置文件中。
4. **数据库权限**: 使用最小权限数据库账户，仅授予应用所需表级的 SELECT/INSERT 权限。
