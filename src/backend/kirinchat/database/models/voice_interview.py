from datetime import datetime, date
from typing import Optional, List, Dict
from uuid import uuid4
from sqlmodel import Field, Column, JSON, DateTime, Text, text
from kirinchat.database.models.base import SQLModelSerializable


class VoiceInterviewSessionTable(SQLModelSerializable, table=True):
    __tablename__ = "voice_interview_session"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, description="Session ID")
    user_id: str = Field(description="User ID")
    skill_id: str = Field(description="Skill ID (e.g. python-backend, frontend)")
    difficulty: str = Field(description="Difficulty: easy/medium/hard")
    resume_id: Optional[str] = Field(default=None, description="Linked resume ID")
    planned_duration: int = Field(description="Planned duration in minutes")
    current_phase: str = Field(default="INTRO", description="Current phase: INTRO/TECH/PROJECT/HR/COMPLETED")
    status: str = Field(default="IN_PROGRESS", description="Status: IN_PROGRESS/PAUSED/COMPLETED")
    evaluate_status: str = Field(default="PENDING", description="Evaluate status: PENDING/PROCESSING/COMPLETED/FAILED")
    evaluate_error: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True), description="Evaluation error message")
    llm_provider: Optional[str] = Field(default=None, description="LLM provider used")
    phases_enabled: Dict = Field(sa_column=Column(JSON, nullable=False), description="Enabled phases e.g. {intro:true,tech:true}")
    start_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True), description="Start time")
    end_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True), description="End time")
    paused_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True), description="Paused at")
    resumed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True), description="Resumed at")
    actual_duration: Optional[int] = Field(default=None, description="Actual duration in seconds")
    update_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP')),
        description="Update time"
    )
    create_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        description="Create time"
    )


class VoiceInterviewMessageTable(SQLModelSerializable, table=True):
    __tablename__ = "voice_interview_message"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, description="Message ID")
    session_id: str = Field(description="Session ID")
    phase: str = Field(description="Phase when this message was created")
    user_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True), description="ASR recognized text")
    ai_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True), description="AI generated text")
    sequence_num: int = Field(description="Message sequence number")
    timestamp: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True), description="Message timestamp")
    create_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        description="Create time"
    )


class VoiceInterviewEvaluationTable(SQLModelSerializable, table=True):
    __tablename__ = "voice_interview_evaluation"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, description="Evaluation ID")
    session_id: str = Field(description="Session ID")
    overall_score: Optional[float] = Field(default=None, description="Overall score 0-100")
    overall_feedback: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True), description="Overall feedback")
    category_scores: Optional[Dict] = Field(default=None, sa_column=Column(JSON, nullable=True), description="Category scores for radar chart")
    question_evaluations: Optional[List] = Field(default=None, sa_column=Column(JSON, nullable=True), description="Per-question evaluations")
    strengths: Optional[List[str]] = Field(default=None, sa_column=Column(JSON, nullable=True), description="Strengths list")
    improvements: Optional[List[str]] = Field(default=None, sa_column=Column(JSON, nullable=True), description="Improvements list")
    reference_answers: Optional[List] = Field(default=None, sa_column=Column(JSON, nullable=True), description="Reference answers")
    interviewer_role: Optional[str] = Field(default=None, description="Interviewer role")
    interview_date: Optional[date] = Field(default=None, description="Interview date")
    create_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        description="Create time"
    )
