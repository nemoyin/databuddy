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
    admin_api_key: str = ""

    # Paths
    skills_dir: str = str(Path(__file__).parent.parent.parent / "skills")
    data_dir: str = "data"

    model_config = {"env_prefix": "JWB_", "env_file": ".env"}


settings = Settings()
