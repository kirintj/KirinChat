from sqlmodel import select, update

from kirinchat.database.models.interview import (
    InterviewSessionTable,
    InterviewQuestionTable,
    EvaluationReportTable,
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
