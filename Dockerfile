# ============================================================
# Stage 1: 构建前端 (React + Vite)
# ============================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /build
COPY desktop/package.json desktop/package-lock.json ./
RUN npm ci
COPY desktop/ ./
RUN npm run build

# ============================================================
# Stage 2: 后端运行环境 (Python)
# ============================================================
FROM python:3.12-slim

WORKDIR /app

# 安装中文字体（供 fpdf2 PDF 导出使用，~7MB 轻量版）
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# 复制后端源码
COPY backend/ /app/backend/

# 复制前端构建产物到后端预期的路径
# main.py 中：Path(__file__) /../ ../../.. /desktop/dist → /app/desktop/dist
COPY --from=frontend-builder /build/dist/ /app/desktop/dist/

# 安装 Python 依赖
WORKDIR /app/backend
RUN pip install --no-cache-dir -e .

# 创建数据持久化目录
RUN mkdir -p /app/backend/data

# 环境变量（所有配置均通过 JWB_ 前缀的环境变量注入）
ENV JWB_APP_NAME="JWBuddy"
ENV JWB_HOST="0.0.0.0"
ENV JWB_PORT=8000

# LLM 配置 — 通过环境变量覆盖（docker-compose.yml 或 -e 传入）
#   JWB_LLM_INTERNAL_BASE_URL=http://host.docker.internal:8001/v1
#   JWB_LLM_INTERNAL_API_KEY=sk-xxx
#   JWB_LLM_INTERNAL_MODEL=deepseek-v3
#   JWB_LLM_CLOUD_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
#   JWB_LLM_CLOUD_API_KEY=sk-xxx
#   JWB_LLM_CLOUD_MODEL=qwen-plus

# 数据库（可选，默认值不含 pg/redis 仍可启动，仅 sql_query 工具需要）
#   JWB_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
#   JWB_REDIS_URL=redis://host:6379/0

EXPOSE 8000

VOLUME /app/backend/data

CMD ["uvicorn", "jwbuddy.main:app", "--host", "0.0.0.0", "--port", "8000"]
