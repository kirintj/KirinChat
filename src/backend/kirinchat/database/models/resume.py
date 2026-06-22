from datetime import datetime
from typing import Optional, Dict, List
from uuid import uuid4

from sqlmodel import Field, Column, JSON, DateTime, Text, text

from kirinchat.database.models.base import SQLModelSerializable


class ResumeTable(SQLModelSerializable, table=True):
    __tablename__ = "resume"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, description="简历ID")
    user_id: str = Field(description="用户ID")
    filename: str = Field(description="原始文件名")
    file_path: str = Field(description="MinIO 存储路径")
    file_size: int = Field(description="文件大小(bytes)")
    content_type: str = Field(description="MIME类型")
    file_hash: str = Field(description="SHA256内容哈希")
    raw_text: Optional[str] = Field(default="", sa_column=Column(Text), description="解析后的纯文本")
    status: str = Field(default="PENDING", description="状态: PENDING/PROCESSING/COMPLETED/FAILED")
    analysis_result: Optional[Dict] = Field(default=None, sa_column=Column(JSON), description="AI分析结果")
    score: Optional[float] = Field(default=None, description="简历评分(0-100)")
    retry_count: int = Field(default=0, description="重试次数")
    error_message: Optional[str] = Field(default="", sa_column=Column(Text), description="失败原因")

    update_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP'),
            onupdate=text('CURRENT_TIMESTAMP')
        ),
        description="修改时间"
    )
    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP')
        ),
        description="创建时间"
    )
