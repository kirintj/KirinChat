import yaml
from typing import Literal, Optional, List
from loguru import logger
from types import SimpleNamespace
from pydantic.v1 import BaseSettings, Field, BaseModel

from kirinchat.schemas.common import MultiModels, ModelConfig, Tools, Rag, StorageConfig, ServerConfig


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
    minio_endpoint: str = Field("localhost:9000", env="MINIO_ENDPOINT")
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
