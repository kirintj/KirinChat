import logging
from datetime import datetime
from typing import Optional

from kirinchat.database.models.voice_interview import (
    VoiceInterviewSessionTable,
    VoiceInterviewMessageTable,
    VoiceInterviewEvaluationTable,
)
from kirinchat.database.dao.voice_interview import (
    VoiceInterviewSessionDao,
    VoiceInterviewMessageDao,
    VoiceInterviewEvaluationDao,
)

logger = logging.getLogger(__name__)


class VoiceInterviewService:

    @classmethod
    async def create_session(
        cls,
        user_id: str,
        skill_id: str,
        difficulty: str,
        planned_duration: int,
        phases: dict,
        resume_id: Optional[str] = None,
    ) -> VoiceInterviewSessionTable:
        session = VoiceInterviewSessionTable(
            user_id=user_id,
            skill_id=skill_id,
            difficulty=difficulty,
            resume_id=resume_id,
            planned_duration=planned_duration,
            phases_enabled=phases,
            current_phase="INTRO",
            status="IN_PROGRESS",
            start_time=datetime.utcnow(),
        )
        return await VoiceInterviewSessionDao.create_session(session)

    @classmethod
    async def get_session(cls, session_id: str) -> Optional[VoiceInterviewSessionTable]:
        return await VoiceInterviewSessionDao.select_session_by_id(session_id)

    @classmethod
    async def list_sessions(cls, user_id: str, status: Optional[str] = None):
        sessions = await VoiceInterviewSessionDao.select_sessions_by_user(user_id)
        if status:
            sessions = [s for s in sessions if s.status == status]
        return sessions

    @classmethod
    async def end_session(cls, session_id: str):
        session = await VoiceInterviewSessionDao.select_session_by_id(session_id)
        if not session:
            return
        end_time = datetime.utcnow()
        actual_duration = int((end_time - session.start_time).total_seconds()) if session.start_time else 0
        await VoiceInterviewSessionDao.update_session(
            session_id,
            status="COMPLETED",
            current_phase="COMPLETED",
            end_time=end_time,
            actual_duration=actual_duration,
        )

    @classmethod
    async def pause_session(cls, session_id: str):
        await VoiceInterviewSessionDao.update_session(
            session_id, status="PAUSED", paused_at=datetime.utcnow()
        )

    @classmethod
    async def resume_session(cls, session_id: str):
        await VoiceInterviewSessionDao.update_session(
            session_id, status="IN_PROGRESS", resumed_at=datetime.utcnow()
        )

    @classmethod
    async def update_phase(cls, session_id: str, phase: str):
        await VoiceInterviewSessionDao.update_session(session_id, current_phase=phase)

    @classmethod
    async def save_message(
        cls,
        session_id: str,
        phase: str,
        user_text: Optional[str],
        ai_text: Optional[str],
    ):
        seq = await VoiceInterviewMessageDao.get_next_sequence_num(session_id)
        msg = VoiceInterviewMessageTable(
            session_id=session_id,
            phase=phase,
            user_text=user_text,
            ai_text=ai_text,
            sequence_num=seq,
            timestamp=datetime.utcnow(),
        )
        return await VoiceInterviewMessageDao.create_message(msg)

    @classmethod
    async def get_messages(cls, session_id: str):
        return await VoiceInterviewMessageDao.select_messages_by_session(session_id)

    @classmethod
    async def get_evaluation(cls, session_id: str):
        return await VoiceInterviewEvaluationDao.select_evaluation_by_session(session_id)

    @classmethod
    async def create_evaluation_placeholder(cls, session_id: str):
        evaluation = VoiceInterviewEvaluationTable(session_id=session_id)
        return await VoiceInterviewEvaluationDao.create_evaluation(evaluation)

    @classmethod
    async def update_evaluation(cls, evaluation_id: str, **kwargs):
        await VoiceInterviewEvaluationDao.update_evaluation(evaluation_id, **kwargs)
