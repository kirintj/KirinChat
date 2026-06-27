from sqlmodel import select, update, func, col

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
    async def select_sessions_with_details(
        cls,
        user_id: str,
        status: str = None,
        skill_id: str = None,
        keyword: str = None,
        difficulty: str = None,
        page: int = 1,
        page_size: int = 20,
    ):
        """一次性查询 session + total_score（LEFT JOIN evaluation_report），支持筛选和分页。

        返回 (rows, total) 其中 rows 是 (InterviewSessionTable, total_score) 元组列表。
        注意：keyword 筛选和 skill_name 需要在 Python 层处理（因为 skill 来自文件系统），
        此处仅做 DB 层筛选，keyword 传入时此处不做过滤，交由调用方处理。
        """
        with session_getter() as session:
            # 构建基础查询：LEFT JOIN evaluation_report 获取 total_score
            base_query = (
                select(
                    InterviewSessionTable,
                    EvaluationReportTable.total_score,
                )
                .outerjoin(
                    EvaluationReportTable,
                    InterviewSessionTable.id == EvaluationReportTable.session_id,
                )
                .where(InterviewSessionTable.user_id == user_id)
            )

            # DB 层筛选条件
            if status:
                base_query = base_query.where(InterviewSessionTable.status == status)
            if skill_id:
                base_query = base_query.where(InterviewSessionTable.skill_id == skill_id)
            if difficulty:
                base_query = base_query.where(InterviewSessionTable.difficulty == difficulty)

            # keyword 无法在 DB 层筛选（skill_name 来自文件系统），跳过

            # 计算总数
            count_query = select(func.count()).select_from(
                base_query.subquery()
            )
            total = session.exec(count_query).one()

            # 分页查询
            offset = (max(1, page) - 1) * max(1, page_size)
            paginated = base_query.offset(offset).limit(max(1, page_size))
            result = session.exec(paginated).all()

            rows = [(row[0], row[1]) for row in result]
            return rows, total

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

    @classmethod
    async def batch_calculate_progress(cls, session_ids: list[str]) -> dict:
        """批量计算多个 session 的进度。

        一次查询获取所有相关 question，然后在 Python 层分组统计。
        返回 {session_id: {"current": answered_count, "total": total_count}} 字典。
        """
        if not session_ids:
            return {}
        with session_getter() as session:
            statement = select(InterviewQuestionTable).where(
                col(InterviewQuestionTable.session_id).in_(session_ids)
            )
            questions = session.exec(statement).all()

        progress_map = {}
        for q in questions:
            if q.session_id not in progress_map:
                progress_map[q.session_id] = {"current": 0, "total": 0}
            progress_map[q.session_id]["total"] += 1
            if q.user_answer is not None:
                progress_map[q.session_id]["current"] += 1
        # 确保没有 question 的 session 也有默认值
        for sid in session_ids:
            if sid not in progress_map:
                progress_map[sid] = {"current": 0, "total": 0}
        return progress_map


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
