import yaml
import os
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


def load_config_from_yaml(file_path: str) -> dict:
    """同步加载 YAML 配置文件"""
    try:
        # 尝试多个可能的路径
        possible_paths = [
            file_path,
            os.path.join(os.path.dirname(__file__), "config.yaml"),
            os.path.join(os.getcwd(), "kirinchat", "config.yaml"),
            os.path.join(os.getcwd(), "config.yaml"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        logger.info(f"配置文件加载成功: {path}")
                        return data

        logger.error("未找到配置文件")
        return {}
    except Exception as e:
        logger.error(f"Yaml file loading error: {e}")
        return {}


def init_settings():
    """初始化设置（同步版本）"""
    global app_settings

    data = load_config_from_yaml("kirinchat/config.yaml")
    if not data:
        return

    # 特殊处理multi_models配置
    if "multi_models" in data:
        try:
            data["multi_models"] = MultiModels(**data["multi_models"])
        except Exception as e:
            logger.error(f"multi_models 解析失败: {e}")

    if "tools" in data:
        try:
            data["tools"] = Tools(**data["tools"])
        except Exception as e:
            logger.error(f"tools 解析失败: {e}")

    if "rag" in data:
        try:
            data["rag"] = Rag(**data["rag"])
        except Exception as e:
            logger.error(f"rag 解析失败: {e}")

    if "storage" in data:
        try:
            data["storage"] = StorageConfig(**data["storage"])
        except Exception as e:
            logger.error(f"storage 解析失败: {e}")

    if "server" in data:
        try:
            data["server"] = ServerConfig(**data["server"])
        except Exception as e:
            logger.error(f"server 解析失败: {e}")

    if "cors" in data:
        try:
            data["cors"] = CORSConfig(**data["cors"])
        except Exception as e:
            logger.error(f"cors 解析失败: {e}")

    for key, value in data.items():
        try:
            setattr(app_settings, key, value)
        except Exception as e:
            logger.warning(f"设置 {key} 失败: {e}")


# 创建全局设置对象并立即加载配置
app_settings = Settings()
init_settings()


async def init_app_settings(file_path: str = None):
    """异步版本的配置加载（用于向后兼容）"""
    # 配置已经在模块加载时初始化，这里只是为了兼容
    pass
