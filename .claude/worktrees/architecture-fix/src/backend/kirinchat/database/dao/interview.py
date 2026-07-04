from datetime import datetime
from typing import Optional, Dict, List
from uuid import uuid4

from sqlalchemy import func, case, select, update
from sqlmodel import Field, Column, JSON, DateTime, Text, text
from sqlalchemy.ext.asyncio import AsyncSession

from kirinchat.database.models.interview import (
    InterviewSessionTable,
    InterviewQuestionTable,
    EvaluationReportTable,
)
from kirinchat.database.models.base import SQLModelSerializable
from kirinchat.database.session import async_session_getter


# In-memory skill cache for N+1 optimization (temporary until DB migration)
_skill_cache: Dict[str, Dict] = {}


class SkillCacheTable(SQLModelSerializable, table=False):
    """Temporary in-memory representation of skills for query optimization."""
    __tablename__ = "skill"

    id: str = Field(primary_key=True)
    name: str
    description: Optional[str] = None
    create_time: Optional[datetime] = None


def update_skill_cache(skills: Dict[str, Dict]):
    """Update the in-memory skill cache with loaded skills."""
    global _skill_cache
    _skill_cache = skills


class InterviewSessionDao:

    @classmethod
    async def create_session(cls, session: InterviewSessionTable):
        async with async_session_getter() as s:
            s.add(session)
            await s.commit()
            await s.refresh(session)
            return session

    @classmethod
    async def select_session_by_id(cls, session_id: str):
        async with async_session_getter() as session:
            statement = select(InterviewSessionTable).where(
                InterviewSessionTable.id == session_id
            )
            result = await session.exec(statement)
            return result.first()

    @classmethod
    async def update_session_status(cls, session_id: str, status: str):
        """异步更新面试会话状态"""
        async with async_session_getter() as session:
            statement = (
                update(InterviewSessionTable)
                .where(InterviewSessionTable.id == session_id)
                .values(status=status)
            )
            await session.exec(statement)
            await session.commit()

    @classmethod
    async def select_sessions_by_user(cls, user_id: str):
        """异步查询用户的所有面试会话"""
        async with async_session_getter() as session:
            statement = select(InterviewSessionTable).where(
                InterviewSessionTable.user_id == user_id
            )
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def delete_session(cls, session_id: str):
        """异步删除面试会话及其关联数据"""
        async with async_session_getter() as session:
            # Delete related questions
            q_stmt = select(InterviewQuestionTable).where(
                InterviewQuestionTable.session_id == session_id
            )
            result = await session.exec(q_stmt)
            for q in result.all():
                await session.delete(q)

            # Delete related evaluation reports
            r_stmt = select(EvaluationReportTable).where(
                EvaluationReportTable.session_id == session_id
            )
            result = await session.exec(r_stmt)
            for r in result.all():
                await session.delete(r)

            # Delete the session itself
            s_stmt = select(InterviewSessionTable).where(
                InterviewSessionTable.id == session_id
            )
            result = await session.exec(s_stmt)
            s = result.first()
            if s:
                await session.delete(s)

            await session.commit()

    @classmethod
    async def select_sessions_with_details(
        cls,
        user_id: str,
        status: str = None,
        skill_id: str = None,
        keyword: str = None,
        difficulty: str = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[List[tuple], int]:
        """
        一次性加载 session + skill_name + total_score（带分页）
        优化 N+1 查询问题
        """
        async with async_session_getter() as session:
            # 构建基础查询
            statement = (
                select(
                    InterviewSessionTable,
                    EvaluationReportTable.total_score,
                )
                .outerjoin(
                    EvaluationReportTable,
                    InterviewSessionTable.id == EvaluationReportTable.session_id
                )
                .where(InterviewSessionTable.user_id == user_id)
            )

            # 应用筛选条件
            if status:
                statement = statement.where(InterviewSessionTable.status == status)
            if skill_id:
                statement = statement.where(InterviewSessionTable.skill_id == skill_id)
            if difficulty:
                statement = statement.where(InterviewSessionTable.difficulty == difficulty)

            # 获取总数
            count_statement = select(func.count()).select_from(statement.subquery())
            total_result = await session.execute(count_statement)
            total = total_result.scalar() or 0

            # 应用分页
            offset = (page - 1) * page_size
            statement = statement.offset(offset).limit(page_size)

            # 执行查询
            result = await session.execute(statement)
            rows = result.all()

            # Enrich with skill names from cache (avoiding N+1)
            enriched_rows = []
            for row in rows:
                session_obj, total_score = row
                skill_name = _skill_cache.get(session_obj.skill_id, {}).get("name", "Unknown")

                # Apply keyword filter if provided
                if keyword and keyword.lower() not in skill_name.lower():
                    continue

                enriched_rows.append((session_obj, skill_name, total_score))

            return enriched_rows, total


class InterviewQuestionDao:

    @classmethod
    async def create_question(cls, question: InterviewQuestionTable):
        """异步创建面试问题"""
        async with async_session_getter() as session:
            session.add(question)
            await session.commit()
            await session.refresh(question)
            return question

    @classmethod
    async def select_questions_by_session(cls, session_id: str):
        """异步查询会话的所有问题"""
        async with async_session_getter() as session:
            statement = select(InterviewQuestionTable).where(
                InterviewQuestionTable.session_id == session_id
            )
            result = await session.exec(statement)
            return result.all()

    @classmethod
    async def update_question_answer(cls, question_id: str, answer: str):
        """异步更新问题答案"""
        async with async_session_getter() as session:
            statement = (
                update(InterviewQuestionTable)
                .where(InterviewQuestionTable.id == question_id)
                .values(user_answer=answer)
            )
            await session.exec(statement)
            await session.commit()

    @classmethod
    async def update_question_score(cls, question_id: str, score: float):
        """异步更新问题评分"""
        async with async_session_getter() as session:
            statement = (
                update(InterviewQuestionTable)
                .where(InterviewQuestionTable.id == question_id)
                .values(score=score)
            )
            await session.exec(statement)
            await session.commit()

    @classmethod
    async def batch_calculate_progress(
        cls,
        session_ids: List[str]
    ) -> Dict[str, float]:
        """
        批量计算所有 session 的进度（百分比）
        优化 N+1 查询问题
        """
        if not session_ids:
            return {}

        async with async_session_getter() as session:
            statement = (
                select(
                    InterviewQuestionTable.session_id,
                    func.count().label('total'),
                    func.sum(
                        case(
                            (InterviewQuestionTable.user_answer.isnot(None), 1),
                            else_=0
                        )
                    ).label('completed')
                )
                .where(InterviewQuestionTable.session_id.in_(session_ids))
                .group_by(InterviewQuestionTable.session_id)
            )

            result = await session.execute(statement)

            # 返回百分比（0.0 - 100.0）
            return {
                row.session_id: (
                    (row.completed / row.total * 100.0)
                    if row.total > 0 else 0.0
                )
                for row in result.all()
            }


class EvaluationReportDao:

    @classmethod
    async def create_report(cls, report: EvaluationReportTable):
        """异步创建评估报告"""
        async with async_session_getter() as session:
            session.add(report)
            await session.commit()
            await session.refresh(report)
            return report

    @classmethod
    async def select_report_by_session(cls, session_id: str):
        """异步查询会话的评估报告"""
        async with async_session_getter() as session:
            statement = select(EvaluationReportTable).where(
                EvaluationReportTable.session_id == session_id
            )
            result = await session.exec(statement)
            return result.first()

    @classmethod
    async def select_report_by_id(cls, report_id: str):
        """异步根据ID查询评估报告"""
        async with async_session_getter() as session:
            statement = select(EvaluationReportTable).where(
                EvaluationReportTable.id == report_id
            )
            result = await session.exec(statement)
            return result.first()
