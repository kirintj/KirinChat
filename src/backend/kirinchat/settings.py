import os
import re
import yaml
from typing import Literal, Optional, List
from pathlib import Path
from loguru import logger
from types import SimpleNamespace
from pydantic.v1 import BaseSettings, Field, BaseModel
from dotenv import load_dotenv

from kirinchat.schemas.common import MultiModels, ModelConfig, Tools, Rag, StorageConfig, ServerConfig

# 加载 .env 文件（在 Settings 构造前，确保环境变量可用）
_project_root = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(_project_root / ".env")


def _expand_env_vars(value: str) -> str:
    """Expand ${ENV_VAR} placeholders in a string with OS environment variables.

    If the entire string is a single placeholder like "${FOO}", return the
    environment variable value (or empty string if not set).  Otherwise,
    perform inline substitution so that prefixes/suffixes are preserved.
    """
    if not isinstance(value, str):
        return value

    # Full-match: entire value is a single placeholder
    full_match = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", value)
    if full_match:
        env_var = full_match.group(1)
        return os.environ.get(env_var, "")

    # Partial substitution: replace all ${VAR} occurrences
    def _replace(m):
        return os.environ.get(m.group(1), m.group(0))  # keep placeholder if not set

    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", _replace, value)


def _expand_dict_values(data):
    """Recursively expand ${ENV_VAR} placeholders in dict / list / string values."""
    if isinstance(data, dict):
        return {k: _expand_dict_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_expand_dict_values(item) for item in data]
    elif isinstance(data, str):
        return _expand_env_vars(data)
    return data


class CORSConfig(BaseModel):
    """CORS 配置"""
    enabled: bool = True
    allowed_origins: List[str] = ["*"]
    allow_credentials: bool = False
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    max_age: int = 3600


class Settings(BaseSettings):
    redis: dict = {}
    mysql: dict = {}
    langfuse: dict = {}
    whitelist_paths: list = []
    wechat_config: dict = {}
    default_config: dict = {}
    cors: CORSConfig = CORSConfig()

    server: Optional[ServerConfig] = ServerConfig()
    rag: Optional[Rag] = None
    tools: Optional[Tools] = None
    storage: Optional[StorageConfig] = None
    multi_models: Optional[MultiModels] = None

    # MinIO 配置 — 优先从环境变量读取
    minio_endpoint: str = Field("127.0.0.1:19000", env="MINIO_ENDPOINT")
    minio_access_key: str = Field("minioadmin", env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field("minioadmin", env="MINIO_SECRET_KEY")
    minio_bucket: str = Field("kirinchat", env="MINIO_BUCKET")
    minio_secure: bool = Field(False, env="MINIO_SECURE")

    # Celery 配置 — 优先从环境变量读取
    celery_broker_url: str = Field("redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field("redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")

    # DashScope API key (for voice interview TTS/ASR)
    dashscope_api_key: str = Field("", env="DASHSCOPE_API_KEY")

    # MiMo API key (for MiMo ASR/TTS)
    mimo_api_key: str = Field("", env="MIMO_API_KEY")

    # 语音面试配置
    voice_interview: dict = {}

    class Config:
        env_prefix = ""


app_settings = Settings()

async def init_app_settings(file_path: str = None):
    global app_settings

    file_path = file_path or "kirinchat/config.yaml"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data is None:
                logger.error("YAML 文件解析为空")
                return

            # Expand ${ENV_VAR} placeholders from environment
            data = _expand_dict_values(data)

            # 特殊处理multi_models配置
            if "multi_models" in data:
                data["multi_models"] = MultiModels(**data["multi_models"])

            if "tools" in data:
                data["tools"] = Tools(**data["tools"])

            if "rag" in data:
                data["rag"] = Rag(**data["rag"])

            if "storage" in data:
                data["storage"] = StorageConfig(**data["storage"])

            if "server" in data:
                data["server"] = ServerConfig(**data["server"])

            if "cors" in data:
                data["cors"] = CORSConfig(**data["cors"])

            for key, value in data.items():
                setattr(app_settings, key, value)
    except Exception as e:
        logger.error(f"Yaml file loading error: {e}")
