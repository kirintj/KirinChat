from kirinchat.api.services.skill import SkillService
from kirinchat.database.dao.interview import (
    InterviewSessionDao,
    InterviewQuestionDao,
)
from kirinchat.database.models.interview import InterviewSessionTable


class InterviewService:
    """Service for managing interview sessions and questions."""

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    @classmethod
    async def create_session(cls, user_id, skill_id, difficulty="MEDIUM", question_count=10):
        """Create an interview session after verifying the skill exists."""
        skill = SkillService.get_skill_by_id(skill_id)
        if skill is None:
            raise ValueError(f"Skill not found: {skill_id}")

        session = InterviewSessionTable(
            user_id=user_id,
            skill_id=skill_id,
            difficulty=difficulty,
            question_count=question_count,
            status="CREATED",
        )
        return await InterviewSessionDao.create_session(session)

    @classmethod
    async def get_session(cls, session_id):
        """Get an interview session by ID."""
        return await InterviewSessionDao.select_session_by_id(session_id)

    @classmethod
    async def update_session_status(cls, session_id, status):
        """Update the status of an interview session."""
        await InterviewSessionDao.update_session_status(session_id, status)

    @classmethod
    async def get_user_sessions(cls, user_id):
        """Get all interview sessions for a user."""
        return await InterviewSessionDao.select_sessions_by_user(user_id)

    @classmethod
    async def delete_session(cls, session_id):
        """Delete an interview session and all related data."""
        await InterviewSessionDao.delete_session(session_id)

    # ------------------------------------------------------------------
    # Question management
    # ------------------------------------------------------------------

    @classmethod
    async def get_session_questions(cls, session_id):
        """Get all questions for an interview session."""
        return await InterviewQuestionDao.select_questions_by_session(session_id)

    @classmethod
    async def save_question(cls, question):
        """Save an interview question."""
        return await InterviewQuestionDao.create_question(question)

    @classmethod
    async def submit_answer(cls, question_id, answer):
        """Submit an answer for a question."""
        return await InterviewQuestionDao.update_question_answer(question_id, answer)

    # ------------------------------------------------------------------
    # Progress tracking
    # ------------------------------------------------------------------

    @classmethod
    async def calculate_progress(cls, session_id):
        """Calculate interview progress.

        Returns {"current": answered_count, "total": total_count}.
        """
        questions = await InterviewQuestionDao.select_questions_by_session(session_id)
        total = len(questions)
        answered = sum(1 for q in questions if q.user_answer is not None)
        return {"current": answered, "total": total}

    # ------------------------------------------------------------------
    # 历史题目查询（跨 session 去重）
    # ------------------------------------------------------------------

    @classmethod
    async def get_historical_questions(
        cls, user_id: str, skill_id: str, exclude_session_id: str
    ) -> list[str]:
        """获取同技能方向其他 session 的历史题目内容列表。

        用于出题时的跨 session 去重，返回值直接传给 _get_dedup_prompt。
        """
        questions = await InterviewQuestionDao.select_main_questions_by_user_skill(
            user_id, skill_id, exclude_session_id
        )
        return [q.content for q in questions]
