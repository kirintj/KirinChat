from typing import Optional
from loguru import logger
from sqlmodel import SQLModel, create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

from kirinchat.database.models.agent import AgentTable
from kirinchat.database.models.history import HistoryTable
from kirinchat.database.models.memory_history import MemoryHistoryTable
from kirinchat.database.models.user import SystemUser
from kirinchat.database.models.knowledge import KnowledgeTable
from kirinchat.database.models.knowledge_file import KnowledgeFileTable
from kirinchat.database.models.tool import ToolTable
from kirinchat.database.models.dialog import DialogTable
from kirinchat.database.models.mcp_server import MCPServerTable, MCPServerStdioTable
from kirinchat.database.models.mcp_user_config import MCPUserConfigTable
from kirinchat.database.models.user_role import UserRole
from kirinchat.database.models.llm import LLMTable
from kirinchat.database.models.message import MessageDownTable, MessageLikeTable
from kirinchat.database.models.role import Role
from kirinchat.database.models.workspace_session import WorkSpaceSession
from kirinchat.database.models.usage_stats import UsageStats
from kirinchat.database.models.agent_skill import AgentSkill
from kirinchat.database.models.register_mcp import RegisterMcpServer
from kirinchat.database.models.register_task import RegisterMcpTask
from kirinchat.database.models.register_mcp_tool import RegisterMcpTool
from kirinchat.database.models.resume import ResumeTable  # noqa: F401
from kirinchat.database.models.voice_interview import (  # noqa: F401
    VoiceInterviewSessionTable,
    VoiceInterviewMessageTable,
    VoiceInterviewEvaluationTable,
)
from kirinchat.settings import app_settings


_engine = None
_async_engine = None


def _validate_endpoint(endpoint: Optional[str], name: str) -> str:
    """Validate a MySQL endpoint string, raising a clear error if missing/invalid."""
    if not endpoint or not isinstance(endpoint, str):
        raise RuntimeError(
            f"MySQL {name} 未配置。请在环境变量中设置 "
            f"MYSQL_ENDPOINT / MYSQL_ASYNC_ENDPOINT，"
            f"或修改 kirinchat/config.yaml 中的 mysql.{name} 字段。"
        )
    # SQLAlchemy URL 必须形如 dialect+driver://...
    if "://" not in endpoint:
        raise RuntimeError(
            f"MySQL {name} 格式无效: {endpoint!r}。"
            f"期望格式: mysql+pymysql://<user>:<password>@<host>:<port>/<database>"
        )
    return endpoint


def _build_connect_args():
    return {
        "charset": "utf8mb4",
        "use_unicode": True,
        "init_command": "SET SESSION time_zone = '+08:00'",
    }


def get_engine():
    """Lazily build / return the synchronous engine after YAML config is loaded."""
    global _engine
    if _engine is None:
        endpoint = _validate_endpoint(
            app_settings.mysql.get("endpoint"), "endpoint"
        )
        logger.info(f"Creating sync MySQL engine -> {endpoint}")
        _engine = create_engine(
            url=endpoint,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args=_build_connect_args(),
        )
    return _engine


def get_async_engine():
    """Lazily build / return the async engine after YAML config is loaded."""
    global _async_engine
    if _async_engine is None:
        endpoint = _validate_endpoint(
            app_settings.mysql.get("async_endpoint"), "async_endpoint"
        )
        logger.info(f"Creating async MySQL engine -> {endpoint}")
        _async_engine = create_async_engine(
            url=endpoint,
            pool_recycle=3600,
            connect_args=_build_connect_args(),
        )
    return _async_engine


# Backward-compatible module-level names: call accessors on first use.
class _LazyEngineProxy:
    def __init__(self, getter):
        self._getter = getter

    def __getattr__(self, item):
        return getattr(self._getter(), item)


engine = _LazyEngineProxy(get_engine)
async_engine = _LazyEngineProxy(get_async_engine)


def ensure_mysql_database(endpoint: str=None) -> None:
    """
    Ensure MySQL database exists.
    This function is safe to call on every startup.
    """
    from urllib.parse import urlparse, urlunparse

    if not endpoint:
        endpoint = app_settings.mysql.get('endpoint')
    if not endpoint:
        logger.warning(
            "MySQL endpoint 未配置，跳过 ensure_mysql_database。"
            "请设置 MYSQL_ENDPOINT 或修改 kirinchat/config.yaml 中的 mysql.endpoint。"
        )
        return
    parsed = urlparse(endpoint)

    database = parsed.path.lstrip("/")
    if not database:
        raise ValueError("MySQL endpoint must include database name")

    bootstrap_url = urlunparse((
        "mysql+pymysql",
        f"{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 3306}",
        "/",
        "",
        "",
        ""
    ))

    logger.info(f"Checking MySQL database `{database}`")

    engine = create_engine(
        bootstrap_url,
        isolation_level="AUTOCOMMIT",
        connect_args={
            "charset": "utf8mb4",
            "init_command": "SET SESSION time_zone = '+08:00'"
        }
    )

    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    f"""
                    CREATE DATABASE IF NOT EXISTS `{database}`
                    DEFAULT CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci
                    """
                )
            )
        logger.success(f"MySQL database `{database}` is ready")
    finally:
        engine.dispose()
