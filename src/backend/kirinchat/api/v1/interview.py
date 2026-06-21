from loguru import logger
from fastapi import APIRouter, Depends

from kirinchat.api.services.interview import InterviewService
from kirinchat.api.services.skill import SkillService
from kirinchat.api.services.evaluation import EvaluationService
from kirinchat.core.agents.interview_agent import InterviewAgent
from kirinchat.schemas.interview import (
    InterviewStartReq,
    InterviewStartResp,
    InterviewAnswerReq,
    InterviewAnswerResp,
    InterviewCompleteReq,
    InterviewCompleteResp,
    InterviewSessionResp,
    InterviewSessionDetailResp,
    EvaluationReportResp,
    InterviewHistoryResp,
    SkillDetailResp,
    SkillListResp,
    SkillInfoResp,
    SkillCategoryResp,
    QuestionResp,
)
from kirinchat.api.responses.builder import resp_200, resp_500, UnifiedResponseModel
from kirinchat.api.services.user import UserPayload, get_login_user

router = APIRouter(tags=["Interview"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _question_to_resp(q) -> QuestionResp:
    """Convert an InterviewQuestionTable to a QuestionResp."""
    return QuestionResp(
        id=q.id,
        type=q.type,
        category=q.category,
        content=q.content,
    )


def _session_to_resp(session) -> InterviewSessionResp:
    """Convert an InterviewSessionTable to an InterviewSessionResp."""
    return InterviewSessionResp(
        id=session.id,
        skill_id=session.skill_id,
        status=session.status,
        progress={},
    )


def _skill_to_info(skill: dict) -> SkillInfoResp:
    """Convert a skill dict to SkillInfoResp."""
    return SkillInfoResp(
        id=skill.get("id", ""),
        name=skill.get("name", ""),
        description=skill.get("description", ""),
        icon=skill.get("icon", ""),
        categories=[c.get("key", "") for c in skill.get("categories", [])],
    )


def _skill_to_detail(skill: dict) -> SkillDetailResp:
    """Convert a skill dict to SkillDetailResp with categories and references."""
    categories = [
        SkillCategoryResp(
            key=c.get("key", ""),
            label=c.get("name", ""),
            priority=0,
        )
        for c in skill.get("categories", [])
    ]
    refs = skill.get("references", {})
    references = list(refs.values()) if isinstance(refs, dict) else []
    return SkillDetailResp(
        skill=_skill_to_info(skill),
        categories=categories,
        references=references,
    )


# ---------------------------------------------------------------------------
# Interview endpoints
# ---------------------------------------------------------------------------


@router.post("/interview/start", response_model=UnifiedResponseModel)
async def start_interview(
    req: InterviewStartReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """Start a new interview session and generate the first question."""
    try:
        session = await InterviewService.create_session(
            user_id=login_user.user_id,
            skill_id=req.skill_id,
            difficulty=req.difficulty,
            question_count=req.question_count,
        )

        agent = InterviewAgent(agent_config={})
        await agent.init_interview_agent(skill_id=req.skill_id)
        first_question = await agent.generate_first_question(
            session_id=session.id,
            difficulty=req.difficulty,
        )

        data = InterviewStartResp(
            session_id=session.id,
            first_question=_question_to_resp(first_question),
        )
        return resp_200(data=data.model_dump())
    except ValueError as err:
        logger.warning(f"Start interview validation error: {err}")
        return resp_500(message=str(err))
    except Exception as err:
        logger.error(f"Start interview error: {err}")
        return resp_500(message=str(err))


@router.post("/interview/answer", response_model=UnifiedResponseModel)
async def submit_answer(
    req: InterviewAnswerReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """Submit an answer, optionally generate a follow-up, then the next question."""
    try:
        session = await InterviewService.get_session(req.session_id)
        if session is None:
            return resp_500(message="Session not found")

        # Save the answer
        await InterviewService.submit_answer(req.question_id, req.answer)

        # Get the original question content for follow-up evaluation
        questions = await InterviewService.get_session_questions(req.session_id)
        original_question = ""
        for q in questions:
            if q.id == req.question_id:
                original_question = q.content
                break

        agent = InterviewAgent(agent_config={})
        await agent.init_interview_agent(skill_id=session.skill_id)

        # Try to generate a follow-up question
        follow_up = await agent.generate_follow_up(
            session_id=req.session_id,
            original_question=original_question,
            user_answer=req.answer,
        )

        next_question = None
        is_completed = False

        if follow_up:
            next_question = _question_to_resp(follow_up)
        else:
            # No follow-up; try to generate the next main question
            next_q = await agent.generate_next_question(
                session_id=req.session_id,
                difficulty=session.difficulty,
            )
            if next_q is not None:
                next_question = _question_to_resp(next_q)
            else:
                is_completed = True

        data = InterviewAnswerResp(
            next_question=next_question,
            is_completed=is_completed,
        )
        return resp_200(data=data.model_dump())
    except ValueError as err:
        logger.warning(f"Submit answer validation error: {err}")
        return resp_500(message=str(err))
    except Exception as err:
        logger.error(f"Submit answer error: {err}")
        return resp_500(message=str(err))


@router.get("/interview/session/{session_id}", response_model=UnifiedResponseModel)
async def get_session_detail(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get interview session details including questions and progress."""
    try:
        session = await InterviewService.get_session(session_id)
        if session is None:
            return resp_500(message="Session not found")

        questions = await InterviewService.get_session_questions(session_id)
        progress = await InterviewService.calculate_progress(session_id)

        session_resp = _session_to_resp(session)
        session_resp.progress = progress

        data = InterviewSessionDetailResp(
            session=session_resp,
            questions=[_question_to_resp(q) for q in questions],
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get session detail error: {err}")
        return resp_500(message=str(err))


@router.post("/interview/complete", response_model=UnifiedResponseModel)
async def complete_interview(
    req: InterviewCompleteReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """Complete an interview session and trigger evaluation."""
    try:
        session = await InterviewService.get_session(req.session_id)
        if session is None:
            return resp_500(message="Session not found")

        await InterviewService.update_session_status(req.session_id, "COMPLETED")

        report = await EvaluationService.evaluate_session(req.session_id)

        data = InterviewCompleteResp(
            evaluation_id=report.id,
            status=report.status if hasattr(report, "status") else "EVALUATED",
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Complete interview error: {err}")
        return resp_500(message=str(err))


@router.get("/interview/evaluation/{evaluation_id}", response_model=UnifiedResponseModel)
async def get_evaluation_report(
    evaluation_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get an evaluation report by ID."""
    try:
        report = await EvaluationService.get_report_by_id(evaluation_id)
        if report is None:
            return resp_500(message="Evaluation report not found")

        data = EvaluationReportResp(
            id=report.id,
            total_score=report.total_score,
            category_scores=report.category_scores or {},
            summary=report.summary or "",
            strengths=report.strengths or [],
            improvements=report.improvements or [],
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get evaluation report error: {err}")
        return resp_500(message=str(err))


@router.get("/interview/history", response_model=UnifiedResponseModel)
async def get_interview_history(
    login_user: UserPayload = Depends(get_login_user),
):
    """Get interview history for the current user."""
    try:
        sessions = await InterviewService.get_user_sessions(login_user.user_id)
        session_resps = []
        for s in sessions:
            progress = await InterviewService.calculate_progress(s.id)
            sr = _session_to_resp(s)
            sr.progress = progress
            session_resps.append(sr)

        data = InterviewHistoryResp(sessions=session_resps)
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get interview history error: {err}")
        return resp_500(message=str(err))


# ---------------------------------------------------------------------------
# Skill endpoints
# ---------------------------------------------------------------------------


@router.get("/skill/list", response_model=UnifiedResponseModel)
async def list_skills(
    login_user: UserPayload = Depends(get_login_user),
):
    """Get all available skills."""
    try:
        skills = SkillService.get_all_skills()
        data = SkillListResp(
            skills=[_skill_to_info(s) for s in skills],
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"List skills error: {err}")
        return resp_500(message=str(err))


@router.get("/skill/{skill_id}", response_model=UnifiedResponseModel)
async def get_skill_detail(
    skill_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get skill details including categories and references."""
    try:
        skill = SkillService.get_skill_by_id(skill_id)
        if skill is None:
            return resp_500(message=f"Skill not found: {skill_id}")

        # Load with references
        skill_with_refs = SkillService.get_skill_by_id(skill_id)
        if skill_with_refs is not None:
            categories = skill_with_refs.get("categories", [])
            refs = {}
            for cat in categories:
                ref = cat.get("ref")
                if ref:
                    content = SkillService.load_skill_references(skill_id, ref)
                    if content is not None:
                        refs[cat["key"]] = content
            skill["references"] = refs

        data = _skill_to_detail(skill)
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get skill detail error: {err}")
        return resp_500(message=str(err))
