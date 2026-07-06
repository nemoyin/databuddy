# JWBuddy 部署指引

## 目录

- [环境要求](#环境要求)
- [快速开始（Docker Compose）](#快速开始docker-compose)
- [手动部署（源码）](#手动部署源码)
- [配置说明](#配置说明)
- [Docker 镜像离线部署](#docker-镜像离线部署)
- [服务验证](#服务验证)
- [数据持久化](#数据持久化)
- [常见问题](#常见问题)

---

## 环境要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | ≥ 3.12 | 后端运行环境 |
| Node.js | ≥ 18 | 前端构建（仅开发需要） |
| Docker | ≥ 24.0 | 容器化部署 |
| LLM API | OpenAI 兼容 | 必选，支持 DeepSeek / 通义千问 / vLLM 等 |

---

## 快速开始（Docker Compose）

### 1. 获取镜像

```bash
# 方式 A：从源码构建（推荐）
git clone git@github.com:nemoyin/databuddy.git
cd databuddy
docker compose build

# 方式 B：加载离线镜像
# docker load -i jwbuddy-latest.tar
```

### 2. 配置 LLM

编辑 `docker-compose.yml`，修改环境变量：

```yaml
environment:
  # ── LLM 配置（必填） ──
  JWB_LLM_INTERNAL_BASE_URL: "https://api.deepseek.com/v1"
  JWB_LLM_INTERNAL_API_KEY: "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  JWB_LLM_INTERNAL_MODEL: "deepseek-chat"

  # ── 云端 LLM（可选，配置后优先使用） ──
  # JWB_LLM_CLOUD_BASE_URL: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  # JWB_LLM_CLOUD_API_KEY: "sk-xxxx"
  # JWB_LLM_CLOUD_MODEL: "qwen-plus"

  # ── 数据库（可选，仅 sql_query 工具需要） ──
  # JWB_DATABASE_URL: "postgresql+asyncpg://user:pass@host:5432/db"
```

### 3. 启动服务

```bash
docker compose up -d
```

访问 **http://localhost:8000** 即可使用。

### 4. 停止服务

```bash
docker compose down
```

---

## 手动部署（源码）

### 1. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux
# .venv\Scripts\activate    # Windows

# 安装依赖
pip install -e .

# 启动服务
uvicorn jwbuddy.main:app --host 0.0.0.0 --port 8000
```

### 2. 前端（开发模式）

```bash
cd desktop
npm install
npm run dev
```

### 3. 前端（生产构建）

```bash
cd desktop
npm run build
# 构建产物在 desktop/dist/，由后端自动托管
```

---

## 配置说明

所有配置通过环境变量注入，前缀为 `JWB_`：

### LLM 配置

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `JWB_LLM_INTERNAL_BASE_URL` | 内网 LLM API 地址 | `http://localhost:8001/v1` |
| `JWB_LLM_INTERNAL_API_KEY` | 内网 API Key | `""` |
| `JWB_LLM_INTERNAL_MODEL` | 内网模型名 | `deepseek-v3` |
| `JWB_LLM_CLOUD_BASE_URL` | 云端 LLM 地址（可选） | `""` |
| `JWB_LLM_CLOUD_API_KEY` | 云端 API Key | `""` |
| `JWB_LLM_CLOUD_MODEL` | 云端模型名 | `qwen-plus` |
| `JWB_LLM_FALLBACK_ENABLED` | 云端优先 | `true` |

> **路由规则**：配置了云端地址+Key → 优先走云端；否则走内网

### 常用 LLM 地址

| 服务商 | Base URL | 示例模型 |
|--------|----------|----------|
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat`, `deepseek-reasoner` |
| **阿里百炼** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus`, `qwen-max` |
| **硅基流动** | `https://api.siliconflow.cn/v1` | `deepseek-v3`, `Qwen/Qwen2.5-7B-Instruct` |
| **Ollama（本地）** | `http://host.docker.internal:11434/v1` | `deepseek-r1` |
| **vLLM（本地）** | `http://host.docker.internal:8000/v1` | 自定义 |

### 数据库配置（可选）

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `JWB_DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://postgres:postgres@localhost:5432/jwbuddy` |
| `JWB_REDIS_URL` | Redis 连接串 | `redis://localhost:6379/0` |

> 不配置数据库仍可启动，仅 `sql_query` 工具无法使用。

### 其他配置

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `JWB_APP_NAME` | 应用名称 | `JWBuddy` |
| `JWB_DEBUG` | 调试模式 | `false` |
| `JWB_HOST` | 监听地址 | `0.0.0.0` |
| `JWB_PORT` | 监听端口 | `8000` |

---

## Docker 镜像离线部署

### 导出镜像

```bash
# 在可联网的构建机上执行
docker save jwbuddy:latest -o jwbuddy-latest.tar
```

### 导入镜像

```bash
# 在离线服务器上执行
docker load -i jwbuddy-latest.tar
```

### 运行容器

```bash
docker run -d --name jwbuddy -p 8000:8000 \
  -e JWB_LLM_CLOUD_BASE_URL="https://api.deepseek.com/v1" \
  -e JWB_LLM_CLOUD_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -e JWB_LLM_CLOUD_MODEL="deepseek-chat" \
  -v jwbuddy_data:/app/backend/data \
  jwbuddy:latest
```

---

## 服务验证

启动后验证三个服务是否正常：

```bash
# 后端 API
curl http://localhost:8000/health
# 期望: {"status":"ok","app":"JWBuddy"}

# Web 前端
curl -o /dev/null -s -w "%{http_code}" http://localhost:8000/
# 期望: 200

# 聊天功能测试
curl -s -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"title":"test"}' | python -c "import sys,json; print(json.load(sys.stdin)['id'])"
```

---

## 数据持久化

| 数据 | 路径 | 持久化方式 |
|------|------|-----------|
| 会话列表 | `backend/data/sessions.json` | Docker volume: `jwbuddy_data` |
| 消息历史 | `backend/data/messages/*.json` | Docker volume: `jwbuddy_data` |
| 上传文件 | `backend/data/uploads/*` | Docker volume: `jwbuddy_data` |
| 审计日志 | `backend/logs/audit.jsonl` | 容器内，建议挂载 |

### 备份数据

```bash
# Docker 卷备份
docker run --rm -v jwbuddy_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/jwbuddy-backup-$(date +%Y%m%d).tar.gz /data
```

---

## 常见问题

### Q: 启动后访问报错 "LLM 连接失败"

检查 LLM 地址是否正确：

```bash
# 测试 LLM API 是否可达
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer sk-xxxxxxxx"
```

### Q: 前端页面白屏

```bash
# 检查前端静态文件是否正常
docker exec jwbuddy ls -la /app/desktop/dist/
# 应包含 index.html 和 assets/ 目录
```

### Q: 上传 CSV 后查询无结果

确保 CSV 文件编码为 UTF-8，文件大小不超过 50MB。

### Q: Docker 端口冲突

```bash
# 修改宿主机映射端口
docker run -d --name jwbuddy -p 8080:8000 jwbuddy:latest
# 访问 http://localhost:8080
```

### Q: 如何查看容器日志

```bash
docker logs -f jwbuddy
```

### Q: 如何更新到新版本

```bash
git pull
docker compose build
docker compose up -d
```
