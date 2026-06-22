from typing import Optional, List
from sqlmodel import select, update

from kirinchat.database.models.resume import ResumeTable
from kirinchat.database.session import session_getter


class ResumeDao:

    @classmethod
    async def create_resume(cls, resume: ResumeTable) -> ResumeTable:
        with session_getter() as s:
            s.add(resume)
            s.commit()
            s.refresh(resume)
            return resume

    @classmethod
    async def select_by_id(cls, resume_id: str) -> Optional[ResumeTable]:
        with session_getter() as session:
            statement = select(ResumeTable).where(ResumeTable.id == resume_id)
            return session.exec(statement).first()

    @classmethod
    async def select_by_hash(cls, file_hash: str) -> Optional[ResumeTable]:
        with session_getter() as session:
            statement = select(ResumeTable).where(ResumeTable.file_hash == file_hash)
            return session.exec(statement).first()

    @classmethod
    async def select_by_user(cls, user_id: str) -> List[ResumeTable]:
        with session_getter() as session:
            statement = (
                select(ResumeTable)
                .where(ResumeTable.user_id == user_id)
                .order_by(ResumeTable.create_time.desc())
            )
            return session.exec(statement).all()

    @classmethod
    async def update_status(cls, resume_id: str, status: str, error_message: str = ""):
        with session_getter() as session:
            statement = (
                update(ResumeTable)
                .where(ResumeTable.id == resume_id)
                .values(status=status, error_message=error_message)
            )
            session.exec(statement)
            session.commit()

    @classmethod
    async def update_analysis(cls, resume_id: str, raw_text: str, analysis_result: dict, score: float):
        with session_getter() as session:
            statement = (
                update(ResumeTable)
                .where(ResumeTable.id == resume_id)
                .values(
                    raw_text=raw_text,
                    analysis_result=analysis_result,
                    score=score,
                    status="COMPLETED",
                )
            )
            session.exec(statement)
            session.commit()

    @classmethod
    async def delete_resume(cls, resume_id: str):
        with session_getter() as session:
            statement = select(ResumeTable).where(ResumeTable.id == resume_id)
            resume = session.exec(statement).first()
            if resume:
                session.delete(resume)
                session.commit()
