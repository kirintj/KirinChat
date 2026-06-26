from sqlmodel import select, update

from kirinchat.database.models.interview import (
    InterviewSessionTable,
    InterviewQuestionTable,
    EvaluationReportTable,
    EvaluationQuestionDetailTable,
)
from kirinchat.database.session import session_getter


class InterviewSessionDao:

    @classmethod
    async def create_session(cls, session: InterviewSessionTable):
        with session_getter() as s:
            s.add(session)
            s.commit()
            s.refresh(session)
            return session

    @classmethod
    async def select_session_by_id(cls, session_id: str):
        with session_getter() as session:
            statement = select(InterviewSessionTable).where(
                InterviewSessionTable.id == session_id
            )
            result = session.exec(statement).first()
            return result

    @classmethod
    async def update_session_status(cls, session_id: str, status: str):
        with session_getter() as session:
            statement = (
                update(InterviewSessionTable)
                .where(InterviewSessionTable.id == session_id)
                .values(status=status)
            )
            session.exec(statement)
            session.commit()

    @classmethod
    async def select_sessions_by_user(cls, user_id: str):
        with session_getter() as session:
            statement = select(InterviewSessionTable).where(
                InterviewSessionTable.user_id == user_id
            )
            result = session.exec(statement).all()
            return result

    @classmethod
    async def delete_session(cls, session_id: str):
        with session_getter() as session:
            # Delete related questions
            q_stmt = select(InterviewQuestionTable).where(
                InterviewQuestionTable.session_id == session_id
            )
            for q in session.exec(q_stmt).all():
                session.delete(q)

            # Delete related evaluation reports
            r_stmt = select(EvaluationReportTable).where(
                EvaluationReportTable.session_id == session_id
            )
            for r in session.exec(r_stmt).all():
                session.delete(r)

            # Delete the session itself
            s_stmt = select(InterviewSessionTable).where(
                InterviewSessionTable.id == session_id
            )
            s = session.exec(s_stmt).first()
            if s:
                session.delete(s)

            session.commit()


class InterviewQuestionDao:

    @classmethod
    async def create_question(cls, question: InterviewQuestionTable):
        with session_getter() as session:
            session.add(question)
            session.commit()
            session.refresh(question)
            return question

    @classmethod
    async def select_questions_by_session(cls, session_id: str):
        with session_getter() as session:
            statement = select(InterviewQuestionTable).where(
                InterviewQuestionTable.session_id == session_id
            )
            result = session.exec(statement).all()
            return result

    @classmethod
    async def update_question_answer(cls, question_id: str, answer: str):
        with session_getter() as session:
            statement = (
                update(InterviewQuestionTable)
                .where(InterviewQuestionTable.id == question_id)
                .values(user_answer=answer)
            )
            session.exec(statement)
            session.commit()

    @classmethod
    async def update_question_score(cls, question_id: str, score: float):
        with session_getter() as session:
            statement = (
                update(InterviewQuestionTable)
                .where(InterviewQuestionTable.id == question_id)
                .values(score=score)
            )
            session.exec(statement)
            session.commit()

    @classmethod
    async def select_main_questions_by_user_skill(
        cls, user_id: str, skill_id: str, exclude_session_id: str, limit: int = 50
    ) -> list[InterviewQuestionTable]:
        """查询同用户同技能方向其他 session 的历史 MAIN 题目。

        通过 JOIN interview_session 表筛选 user_id 和 skill_id，
        排除当前 session，按创建时间倒序返回最近 limit 条 ORM 对象。
        """
        with session_getter() as session:
            statement = (
                select(InterviewQuestionTable)
                .join(
                    InterviewSessionTable,
                    InterviewQuestionTable.session_id == InterviewSessionTable.id,
                )
                .where(
                    InterviewSessionTable.user_id == user_id,
                    InterviewSessionTable.skill_id == skill_id,
                    InterviewQuestionTable.type == "MAIN",
                    InterviewQuestionTable.session_id != exclude_session_id,
                )
                .order_by(InterviewQuestionTable.create_time.desc())
                .limit(limit)
            )
            result = session.exec(statement).all()
            return list(result)


class EvaluationReportDao:

    @classmethod
    async def create_report(cls, report: EvaluationReportTable):
        with session_getter() as session:
            session.add(report)
            session.commit()
            session.refresh(report)
            return report

    @classmethod
    async def select_report_by_session(cls, session_id: str):
        with session_getter() as session:
            statement = select(EvaluationReportTable).where(
                EvaluationReportTable.session_id == session_id
            )
            result = session.exec(statement).first()
            return result

    @classmethod
    async def select_report_by_id(cls, report_id: str):
        with session_getter() as session:
            statement = select(EvaluationReportTable).where(
                EvaluationReportTable.id == report_id
            )
            result = session.exec(statement).first()
            return result


class EvaluationQuestionDetailDao:

    @classmethod
    async def batch_create(cls, details: list[EvaluationQuestionDetailTable]):
        """批量创建逐题评估详情。"""
        with session_getter() as session:
            for detail in details:
                session.add(detail)
            session.commit()

    @classmethod
    async def select_by_evaluation_id(cls, evaluation_id: str) -> list[EvaluationQuestionDetailTable]:
        """按评估报告 ID 查询所有逐题详情。"""
        with session_getter() as session:
            statement = select(EvaluationQuestionDetailTable).where(
                EvaluationQuestionDetailTable.evaluation_id == evaluation_id
            )
            result = session.exec(statement).all()
            return list(result)

    @classmethod
    async def select_by_question_id(cls, question_id: str):
        """按题目 ID 查询单题评估详情。"""
        with session_getter() as session:
            statement = select(EvaluationQuestionDetailTable).where(
                EvaluationQuestionDetailTable.question_id == question_id
            )
            result = session.exec(statement).first()
            return result
