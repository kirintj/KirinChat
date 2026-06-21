from datetime import datetime
from typing import Optional, List, Dict
from uuid import uuid4

from sqlmodel import Field, Column, JSON, DateTime, Text, text

from kirinchat.database.models.base import SQLModelSerializable


class InterviewSessionTable(SQLModelSerializable, table=True):
    __tablename__ = "interview_session"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, description="面试会话ID")
    user_id: str = Field(description="用户ID")
    agent_id: Optional[str] = Field(default=None, description="绑定的Agent ID")
    skill_id: str = Field(description="面试技能ID")
    difficulty: str = Field(default="MEDIUM", description="难度等级: EASY/MEDIUM/HARD")
    question_count: int = Field(default=10, description="题目数量")
    status: str = Field(default="CREATED", description="会话状态: CREATED/IN_PROGRESS/COMPLETED")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")

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


class InterviewQuestionTable(SQLModelSerializable, table=True):
    __tablename__ = "interview_question"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, description="面试题目ID")
    session_id: str = Field(description="所属面试会话ID")
    type: str = Field(default="MAIN", description="题目类型: MAIN/FOLLOW_UP")
    category: str = Field(description="题目分类")
    content: str = Field(sa_column=Column(Text, nullable=False), description="题目内容")
    user_answer: Optional[str] = Field(default=None, sa_column=Column(Text), description="用户回答")
    score: Optional[float] = Field(default=None, description="得分")

    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP')
        ),
        description="创建时间"
    )


class EvaluationReportTable(SQLModelSerializable, table=True):
    __tablename__ = "evaluation_report"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, description="评估报告ID")
    session_id: str = Field(description="所属面试会话ID")
    total_score: float = Field(description="总分")
    category_scores: Dict = Field(sa_column=Column(JSON), description="各分类得分")
    summary: str = Field(sa_column=Column(Text, nullable=False), description="评估总结")
    strengths: List[str] = Field(sa_column=Column(JSON), description="优势项")
    improvements: List[str] = Field(sa_column=Column(JSON), description="改进项")

    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP')
        ),
        description="创建时间"
    )
