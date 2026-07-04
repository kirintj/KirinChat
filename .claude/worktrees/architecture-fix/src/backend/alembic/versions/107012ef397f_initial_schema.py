"""initial_schema

Revision ID: 107012ef397f
Revises:
Create Date: 2026-06-27 12:35:37.172770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '107012ef397f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create all initial tables."""

    # --- agent ---
    op.create_table(
        "agent",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("logo_url", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=True, index=True),
        sa.Column("is_custom", sa.Boolean(), nullable=False),
        sa.Column("system_prompt", sa.String(length=255), nullable=False),
        sa.Column("llm_id", sa.String(length=255), nullable=False),
        sa.Column("enable_memory", sa.Boolean(), nullable=False),
        sa.Column("mcp_ids", sa.JSON(), nullable=True),
        sa.Column("tool_ids", sa.JSON(), nullable=True),
        sa.Column("agent_skill_ids", sa.JSON(), nullable=True),
        sa.Column("knowledge_ids", sa.JSON(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- agent_skill ---
    op.create_table(
        "agent_skill",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("as_tool_name", sa.String(length=255), nullable=True),
        sa.Column("folder", sa.JSON(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- dialog ---
    op.create_table(
        "dialog",
        sa.Column("dialog_id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("agent_id", sa.String(length=255), nullable=False),
        sa.Column("agent_type", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("summary_last_time", sa.DateTime(), nullable=False, server_default=sa.text("'1970-01-01 00:00:00'")),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- evaluation_report ---
    op.create_table(
        "evaluation_report",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("category_scores", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=True),
        sa.Column("improvements", sa.JSON(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- history ---
    op.create_table(
        "history",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("dialog_id", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=255), nullable=False),
        sa.Column("token_usage", sa.Integer(), nullable=False),
        sa.Column("events", sa.JSON(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- interview_question ---
    op.create_table(
        "interview_question",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("user_answer", sa.Text(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- interview_session ---
    op.create_table(
        "interview_session",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("agent_id", sa.String(length=255), nullable=True),
        sa.Column("skill_id", sa.String(length=255), nullable=False),
        sa.Column("difficulty", sa.String(length=255), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=255), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- knowledge ---
    op.create_table(
        "knowledge",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- knowledge_file ---
    op.create_table(
        "knowledge_file",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("knowledge_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("oss_url", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- llm ---
    op.create_table(
        "llm",
        sa.Column("llm_id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("llm_type", sa.String(length=255), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=False),
        sa.Column("base_url", sa.String(length=255), nullable=False),
        sa.Column("api_key", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- mcp_server ---
    op.create_table(
        "mcp_server",
        sa.Column("mcp_server_id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("server_name", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("user_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("mcp_as_tool_name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=False),
        sa.Column("logo_url", sa.String(length=255), nullable=False),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("tools", sa.JSON(), nullable=True),
        sa.Column("params", sa.JSON(), nullable=True),
        sa.Column("imported_config", sa.JSON(), nullable=True),
        sa.Column("config_enabled", sa.Boolean(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- mcp_stdio_server ---
    op.create_table(
        "mcp_stdio_server",
        sa.Column("mcp_server_id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("mcp_server_path", sa.String(length=255), nullable=False),
        sa.Column("mcp_server_command", sa.String(length=255), nullable=False),
        sa.Column("mcp_server_env", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- mcp_user_config ---
    op.create_table(
        "mcp_user_config",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("mcp_server_id", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- memory_history ---
    op.create_table(
        "memory_history",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("memory_id", sa.String(length=255), nullable=False),
        sa.Column("old_memory", sa.Text(), nullable=True),
        sa.Column("new_memory", sa.Text(), nullable=True),
        sa.Column("event", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.Column("actor_id", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=255), nullable=True),
    )

    # --- message_down ---
    op.create_table(
        "message_down",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("user_input", sa.Text(), nullable=True),
        sa.Column("agent_output", sa.Text(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- message_like ---
    op.create_table(
        "message_like",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("user_input", sa.Text(), nullable=True),
        sa.Column("agent_output", sa.Text(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- register_mcp_server ---
    op.create_table(
        "register_mcp_server",
        sa.Column("id", sa.String(length=64), nullable=False, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("transport", sa.String(length=255), nullable=False),
        sa.Column("remote_url", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_time", sa.DateTime(), nullable=False),
        sa.Column("updated_time", sa.DateTime(), nullable=False),
    )

    # --- register_mcp_task ---
    op.create_table(
        "register_mcp_task",
        sa.Column("id", sa.String(length=64), nullable=False, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=True),
        sa.Column("register_mcp_id", sa.String(length=255), nullable=True),
        sa.Column("messages", sa.JSON(), nullable=True),
        sa.Column("created_time", sa.DateTime(), nullable=False),
        sa.Column("updated_time", sa.DateTime(), nullable=False),
    )

    # --- register_mcp_tool (has FK to register_mcp_server) ---
    op.create_table(
        "register_mcp_tool",
        sa.Column("id", sa.String(length=64), nullable=False, primary_key=True),
        sa.Column("register_mcp_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=1024), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parameters", sa.Text(), nullable=True),
        sa.Column("api_info", sa.JSON(), nullable=True),
        sa.Column("created_time", sa.DateTime(), nullable=False),
        sa.Column("updated_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["register_mcp_id"], ["register_mcp_server.id"]),
    )

    # --- resume ---
    op.create_table(
        "resume",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=False),
        sa.Column("file_hash", sa.String(length=255), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=False),
        sa.Column("analysis_result", sa.JSON(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- role ---
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column("role_name", sa.String(length=255), nullable=False),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("role_name", name="group_role_name_uniq"),
    )

    # --- tool ---
    op.create_table(
        "tool",
        sa.Column("tool_id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("logo_url", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("openapi_schema", sa.JSON(), nullable=True),
        sa.Column("is_user_defined", sa.Boolean(), nullable=False),
        sa.Column("auth_config", sa.JSON(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- usage_stats ---
    op.create_table(
        "usage_stats",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("agent", sa.String(length=255), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- user ---
    op.create_table(
        "user",
        sa.Column("user_id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("user_name", sa.String(length=255), nullable=False),
        sa.Column("user_email", sa.String(length=255), nullable=False),
        sa.Column("user_avatar", sa.String(length=255), nullable=False),
        sa.Column("user_description", sa.String(length=255), nullable=False),
        sa.Column("user_password", sa.String(length=255), nullable=False),
        sa.Column("delete", sa.Boolean(), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- user_role ---
    op.create_table(
        "user_role",
        sa.Column("id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.String(length=255), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- workspace_session ---
    op.create_table(
        "workspace_session",
        sa.Column("session_id", sa.String(length=255), nullable=False, primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("agent", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("contexts", sa.JSON(), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    """Downgrade schema - drop all tables in reverse dependency order."""
    op.drop_table("workspace_session")
    op.drop_table("user_role")
    op.drop_table("user")
    op.drop_table("usage_stats")
    op.drop_table("tool")
    op.drop_table("role")
    op.drop_table("resume")
    op.drop_table("register_mcp_tool")
    op.drop_table("register_mcp_task")
    op.drop_table("register_mcp_server")
    op.drop_table("message_like")
    op.drop_table("message_down")
    op.drop_table("memory_history")
    op.drop_table("mcp_user_config")
    op.drop_table("mcp_stdio_server")
    op.drop_table("mcp_server")
    op.drop_table("llm")
    op.drop_table("knowledge_file")
    op.drop_table("knowledge")
    op.drop_table("interview_session")
    op.drop_table("interview_question")
    op.drop_table("history")
    op.drop_table("evaluation_report")
    op.drop_table("dialog")
    op.drop_table("agent_skill")
    op.drop_table("agent")
