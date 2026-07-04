from typing import Optional, List, Dict
from sqlmodel import select, update

from kirinchat.database.models.voice_interview import (
    VoiceInterviewSessionTable,
    VoiceInterviewMessageTable,
    VoiceInterviewEvaluationTable,
)
from kirinchat.database.session import session_getter


class VoiceInterviewSessionDao:

    @classmethod
    async def create_session(cls, session_obj: VoiceInterviewSessionTable) -> VoiceInterviewSessionTable:
        with session_getter() as s:
            s.add(session_obj)
            s.commit()
            s.refresh(session_obj)
            return session_obj

    @classmethod
    async def select_session_by_id(cls, session_id: str) -> Optional[VoiceInterviewSessionTable]:
        with session_getter() as session:
            statement = select(VoiceInterviewSessionTable).where(
                VoiceInterviewSessionTable.id == session_id
            )
            result = session.exec(statement).first()
            return result

    @classmethod
    async def select_sessions_by_user(cls, user_id: str) -> List[VoiceInterviewSessionTable]:
        with session_getter() as session:
            statement = (
                select(VoiceInterviewSessionTable)
                .where(VoiceInterviewSessionTable.user_id == user_id)
                .order_by(VoiceInterviewSessionTable.create_time.desc())
            )
            return session.exec(statement).all()

    @classmethod
    async def update_session_status(cls, session_id: str, status: str):
        with session_getter() as session:
            statement = (
                update(VoiceInterviewSessionTable)
                .where(VoiceInterviewSessionTable.id == session_id)
                .values(status=status)
            )
            session.exec(statement)
            session.commit()

    @classmethod
    async def update_session(cls, session_id: str, **kwargs):
        with session_getter() as session:
            statement = (
                update(VoiceInterviewSessionTable)
                .where(VoiceInterviewSessionTable.id == session_id)
                .values(**kwargs)
            )
            session.exec(statement)
            session.commit()


class VoiceInterviewMessageDao:

    @classmethod
    async def create_message(cls, message: VoiceInterviewMessageTable) -> VoiceInterviewMessageTable:
        with session_getter() as s:
            s.add(message)
            s.commit()
            s.refresh(message)
            return message

    @classmethod
    async def select_messages_by_session(cls, session_id: str) -> List[VoiceInterviewMessageTable]:
        with session_getter() as session:
            statement = (
                select(VoiceInterviewMessageTable)
                .where(VoiceInterviewMessageTable.session_id == session_id)
                .order_by(VoiceInterviewMessageTable.sequence_num.asc())
            )
            return session.exec(statement).all()

    @classmethod
    async def get_next_sequence_num(cls, session_id: str) -> int:
        with session_getter() as session:
            statement = (
                select(VoiceInterviewMessageTable)
                .where(VoiceInterviewMessageTable.session_id == session_id)
                .order_by(VoiceInterviewMessageTable.sequence_num.desc())
            )
            result = session.exec(statement).first()
            if result is None:
                return 1
            return result.sequence_num + 1


class VoiceInterviewEvaluationDao:

    @classmethod
    async def create_evaluation(cls, evaluation: VoiceInterviewEvaluationTable) -> VoiceInterviewEvaluationTable:
        with session_getter() as s:
            s.add(evaluation)
            s.commit()
            s.refresh(evaluation)
            return evaluation

    @classmethod
    async def select_evaluation_by_session(cls, session_id: str) -> Optional[VoiceInterviewEvaluationTable]:
        with session_getter() as session:
            statement = select(VoiceInterviewEvaluationTable).where(
                VoiceInterviewEvaluationTable.session_id == session_id
            )
            result = session.exec(statement).first()
            return result

    @classmethod
    async def update_evaluation(cls, evaluation_id: str, **kwargs):
        with session_getter() as session:
            statement = (
                update(VoiceInterviewEvaluationTable)
                .where(VoiceInterviewEvaluationTable.id == evaluation_id)
                .values(**kwargs)
            )
            session.exec(statement)
            session.commit()
