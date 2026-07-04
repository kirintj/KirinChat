from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import sys
import os

# 添加项目路径，使 alembic 能够导入 kirinchat 包
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 在导入 kirinchat.database 之前，先初始化 app_settings，
# 因为 kirinchat.database.__init__ 会在模块级别使用 app_settings 创建引擎
from kirinchat.settings import app_settings, init_app_settings
import asyncio

# 加载开发环境配置文件，确保 mysql endpoint 等配置可用
# 尝试顺序：config-dev.yaml -> config.yaml
config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kirinchat")
dev_config = os.path.join(config_dir, "config-dev.yaml")
default_config = os.path.join(config_dir, "config.yaml")

if os.path.exists(dev_config):
    asyncio.run(init_app_settings(dev_config))
elif os.path.exists(default_config):
    asyncio.run(init_app_settings(default_config))

from sqlmodel import SQLModel

# 导入所有模型，确保 autogenerate 能检测到所有表
# 必须在设置 target_metadata 之前导入
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
from kirinchat.database.models.resume import ResumeTable
from kirinchat.database.models.interview import (
    InterviewSessionTable,
    InterviewQuestionTable,
    EvaluationReportTable,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 使用 SQLModel 的 metadata 作为目标元数据（autogenerate 会对比此元数据与数据库实际表）
target_metadata = SQLModel.metadata

# 从 app_settings 获取数据库连接 URL 并覆盖 alembic.ini 中的值
db_url = app_settings.mysql.get('endpoint', config.get_main_option("sqlalchemy.url"))
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
