from typing import Optional, List
from sqlmodel import select, update

from kirinchat.database.models.resume import ResumeTable
from kirinchat.database.session import async_session_getter


class ResumeDao:

    @classmethod
    async def create_resume(cls, resume: ResumeTable) -> ResumeTable:
        async with async_session_getter() as s:
            s.add(resume)
            await s.commit()
            await s.refresh(resume)
            return resume

    @classmethod
    async def select_by_id(cls, resume_id: str) -> Optional[ResumeTable]:
        async with async_session_getter() as session:
            statement = select(ResumeTable).where(ResumeTable.id == resume_id)
            result = await session.exec(statement)
            return result.first()

    @classmethod
    async def select_by_hash(cls, file_hash: str) -> Optional[ResumeTable]:
        async with async_session_getter() as session:
            statement = select(ResumeTable).where(ResumeTable.file_hash == file_hash)
            result = await session.exec(statement)
            return result.first()

    @classmethod
    async def select_by_user(cls, user_id: str) -> List[ResumeTable]:
        async with async_session_getter() as session:
            statement = (
                select(ResumeTable)
                .where(ResumeTable.user_id == user_id)
                .order_by(ResumeTable.create_time.desc())
            )
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def update_status(cls, resume_id: str, status: str, error_message: str = ""):
        async with async_session_getter() as session:
            statement = (
                update(ResumeTable)
                .where(ResumeTable.id == resume_id)
                .values(status=status, error_message=error_message)
            )
            await session.exec(statement)
            await session.commit()

    @classmethod
    async def update_analysis(cls, resume_id: str, raw_text: str, analysis_result: dict, score: float):
        async with async_session_getter() as session:
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
            await session.exec(statement)
            await session.commit()

    @classmethod
    async def delete_resume(cls, resume_id: str):
        async with async_session_getter() as session:
            statement = select(ResumeTable).where(ResumeTable.id == resume_id)
            result = await session.exec(statement)
            resume = result.first()
            if resume:
                await session.delete(resume)
                await session.commit()
