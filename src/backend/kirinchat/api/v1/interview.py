from datetime import datetime
from typing import Optional

from loguru import logger
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import FileResponse
import json

from kirinchat.common.utils.temp_file import make_temp_path, cleanup_temp_file

from kirinchat.api.services.interview import InterviewService
from kirinchat.api.services.skill import SkillService
from kirinchat.api.services.evaluation import EvaluationService
from kirinchat.api.services.learning import LearningService
from kirinchat.core.agents.interview_agent import InterviewAgent
from kirinchat.database.dao.interview import InterviewSessionDao, InterviewQuestionDao
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
    QuestionDetailResp,
    QuestionDetailItem,
)
from kirinchat.api.responses.builder import resp_200, resp_403, resp_404, resp_500, UnifiedResponseModel
from kirinchat.api.responses.streaming import WatchedStreamingResponse
from kirinchat.api.services.user import UserPayload, get_login_user

router = APIRouter(tags=["Interview"])


# ---------------------------------------------------------------------------
# Agent 缓存：避免每次请求重复实例化和加载技能文件
# ---------------------------------------------------------------------------

_agent_cache: dict[str, InterviewAgent] = {}


async def _get_agent(skill_id: str) -> InterviewAgent:
    """获取或创建 InterviewAgent 实例，按 skill_id 缓存复用。"""
    if skill_id not in _agent_cache:
        agent = InterviewAgent(agent_config={})
        await agent.init_interview_agent(skill_id=skill_id)
        _agent_cache[skill_id] = agent
    return _agent_cache[skill_id]


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
        user_answer=q.user_answer,
    )


def _session_to_resp(session, skill_name: str = "", total_score: Optional[float] = None) -> InterviewSessionResp:
    """Convert an InterviewSessionTable to an InterviewSessionResp."""
    return InterviewSessionResp(
        id=session.id,
        skill_id=session.skill_id,
        status=session.status,
        difficulty=session.difficulty,
        progress={},
        skill_name=skill_name,
        total_score=total_score,
        create_time=session.create_time,
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
            label=c.get("label", ""),
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


async def _build_evaluation_resp(report) -> EvaluationReportResp:
    """构建包含逐题详情的评估报告响应。"""
    details = await EvaluationService.get_details_by_evaluation(report.id)
    questions = await InterviewService.get_session_questions(report.session_id)
    q_map = {q.id: q for q in questions}
    question_items = []
    for d in details:
        q = q_map.get(d.question_id)
        question_items.append(QuestionDetailItem(
            question_id=d.question_id,
            content=q.content if q else "",
            user_answer=q.user_answer if q else None,
            type=q.type if q else "MAIN",
            category=q.category if q else "",
            score=d.score,
            feedback=d.feedback,
            reference_answer=d.reference_answer,
        ))
    return EvaluationReportResp(
        id=report.id,
        total_score=report.total_score,
        category_scores=report.category_scores or {},
        summary=report.summary or "",
        strengths=report.strengths or [],
        improvements=report.improvements or [],
        question_details=question_items,
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

        try:
            agent = await _get_agent(skill_id=req.skill_id)
            first_question = await agent.generate_first_question(
                session_id=session.id,
                user_id=login_user.user_id,
                difficulty=req.difficulty,
            )
        except Exception:
            await InterviewService.delete_session(session.id)
            raise

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
            return resp_404(message="Session not found")

        # Save the answer
        await InterviewService.submit_answer(req.question_id, req.answer)

        # Get the original question content for follow-up evaluation
        questions = await InterviewService.get_session_questions(req.session_id)
        original_question = ""
        for q in questions:
            if q.id == req.question_id:
                original_question = q.content
                break

        agent = await _get_agent(skill_id=session.skill_id)

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
                user_id=login_user.user_id,
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


@router.post("/interview/answer/stream")
async def submit_answer_stream(
    req: InterviewAnswerReq,
    login_user: UserPayload = Depends(get_login_user),
):
    """提交答案，流式返回追问题和下一题（SSE）。"""
    try:
        session = await InterviewService.get_session(req.session_id)
        if session is None:
            return resp_404(message="Session not found")

        # 保存用户答案
        await InterviewService.submit_answer(req.question_id, req.answer)

        # 获取原始题目内容
        questions = await InterviewService.get_session_questions(req.session_id)
        original_question = ""
        for q in questions:
            if q.id == req.question_id:
                original_question = q.content
                break

        # 复用缓存 agent
        agent = await _get_agent(skill_id=session.skill_id)

        async def stream():
            follow_up_content = ""
            next_question_content = ""
            is_completed = False

            try:
                # 阶段一：流式生成追问题
                async for event in agent.stream_follow_up(
                    session_id=req.session_id,
                    original_question=original_question,
                    user_answer=req.answer,
                ):
                    follow_up_content = event["data"]["accumulated"]
                    yield f"data: {json.dumps(event)}\n\n"

                # 如果有追问题，发送 done 事件并结束（不生成下一题）
                normalized = follow_up_content.strip().upper().replace(" ", "").replace("_", "").replace("-", "")
                has_follow_up = follow_up_content.strip() and normalized != "NOFOLLOWUP"
                if has_follow_up:
                    done_data = {
                        "type": "done",
                        "data": {
                            "follow_up": {"content": follow_up_content.strip()},
                            "next_question": None,
                            "is_completed": False,
                        },
                    }
                    yield f"data: {json.dumps(done_data)}\n\n"
                    return

                # 阶段二：流式生成下一题
                async for event in agent.stream_next_question(
                    session_id=req.session_id,
                    user_id=login_user.user_id,
                    difficulty=session.difficulty,
                ):
                    data = event["data"]
                    if data.get("is_completed"):
                        is_completed = True
                        break
                    next_question_content = data["accumulated"]
                    yield f"data: {json.dumps(event)}\n\n"

                # 查询刚保存的下一题 ID（stream_next_question 已保存到 DB）
                next_question_id = ""
                if next_question_content.strip() and not is_completed:
                    session_questions = await InterviewService.get_session_questions(req.session_id)
                    if session_questions:
                        last_q = session_questions[-1]
                        if last_q.content.strip() == next_question_content.strip():
                            next_question_id = last_q.id

                # 发送完成事件
                done_data = {
                    "type": "done",
                    "data": {
                        "follow_up": None,
                        "next_question": {"id": next_question_id, "content": next_question_content.strip()} if next_question_content.strip() else None,
                        "is_completed": is_completed,
                    },
                }
                yield f"data: {json.dumps(done_data)}\n\n"

            except Exception as stream_err:
                logger.error(f"SSE stream error for session {req.session_id}: {stream_err}")
                error_data = {
                    "type": "error",
                    "data": {"message": "生成过程中出现错误，请重试"},
                }
                yield f"data: {json.dumps(error_data)}\n\n"

        return WatchedStreamingResponse(
            content=stream(),
            media_type="text/event-stream",
        )
    except ValueError as err:
        logger.warning(f"Submit answer stream validation error: {err}")
        return resp_500(message=str(err))
    except Exception as err:
        logger.error(f"Submit answer stream error: {err}")
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
            return resp_404(message="Session not found")

        questions = await InterviewService.get_session_questions(session_id)
        progress = await InterviewService.calculate_progress(session_id)

        skill = SkillService.get_skill_by_id(session.skill_id)
        skill_name = skill.get("name", "") if skill else ""
        session_resp = _session_to_resp(session, skill_name=skill_name)
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
    """Complete an interview session and trigger async evaluation."""
    try:
        session = await InterviewService.get_session(req.session_id)
        if session is None:
            return resp_404(message="Session not found")

        await InterviewService.update_session_status(req.session_id, "COMPLETED")

        # 异步评估：通过 Celery 后台执行，避免 LLM 调用超时
        from kirinchat.common.async_task.evaluation_tasks import evaluate_interview_task
        evaluate_interview_task.delay(req.session_id)

        data = InterviewCompleteResp(
            evaluation_id="",
            status="PENDING",
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
    """Get an evaluation report by ID (includes per-question details)."""
    try:
        report = await EvaluationService.get_report_by_id(evaluation_id)
        if report is None:
            return resp_404(message="Evaluation report not found")

        data = await _build_evaluation_resp(report)
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get evaluation report error: {err}")
        return resp_500(message=str(err))


@router.get("/interview/evaluation/by-session/{session_id}", response_model=UnifiedResponseModel)
async def get_evaluation_by_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get an evaluation report by session ID (includes per-question details)."""
    try:
        report = await EvaluationService.get_report_by_session(session_id)
        if report is None:
            return resp_404(message="Evaluation report not found for this session")

        data = await _build_evaluation_resp(report)
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get evaluation by session error: {err}")
        return resp_500(message=str(err))


@router.get("/interview/question-detail/{question_id}", response_model=UnifiedResponseModel)
async def get_question_detail(
    question_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """获取单题的评估详情（得分、反馈、参考答案）。"""
    try:
        detail = await EvaluationService.get_detail_by_question(question_id)
        if detail is None:
            return resp_404(message="Question detail not found")

        # 通过 evaluation_id 获取 report，再通过 session_id 获取题目
        report = await EvaluationService.get_report_by_id(detail.evaluation_id)
        q = None
        session = None
        if report:
            session = await InterviewService.get_session(report.session_id)
            if session:
                questions = await InterviewService.get_session_questions(session.id)
                for candidate in questions:
                    if candidate.id == question_id:
                        q = candidate
                        break

        # 获取技能名称
        skill_name = ""
        if session:
            skill = SkillService.get_skill_by_id(session.skill_id)
            skill_name = skill.get("name", "") if skill else ""

        data = QuestionDetailResp(
            question_id=detail.question_id,
            session_id=q.session_id if q else "",
            content=q.content if q else "",
            user_answer=q.user_answer if q else None,
            type=q.type if q else "MAIN",
            category=q.category if q else "",
            score=detail.score,
            feedback=detail.feedback,
            reference_answer=detail.reference_answer,
            skill_name=skill_name,
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get question detail error: {err}")
        return resp_500(message=str(err))


@router.get("/interview/history", response_model=UnifiedResponseModel)
async def get_interview_history(
    status: Optional[str] = None,
    skill_id: Optional[str] = None,
    difficulty: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = "create_time",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    login_user: UserPayload = Depends(get_login_user),
):
    """获取面试历史列表，支持筛选、排序、分页。"""
    try:
        # 参数校验
        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        # keyword 搜索：先在文件系统中匹配 skill_name，得到 skill_ids 列表后在 DB 层筛选
        matched_skill_ids = None
        if keyword:
            all_skills = SkillService.get_all_skills()
            keyword_lower = keyword.lower()
            matched_skill_ids = [
                s.get("id", "") for s in all_skills
                if keyword_lower in s.get("name", "").lower()
            ]
            # 无匹配 skill 时直接返回空结果
            if not matched_skill_ids:
                return resp_200(data=InterviewHistoryResp(
                    sessions=[], total=0, page=page, page_size=page_size
                ).model_dump())

        # DB 层处理筛选 + 排序 + 分页，一次完成
        sessions_with_details, total = await InterviewSessionDao.select_sessions_with_details(
            user_id=login_user.user_id,
            status=status,
            skill_id=skill_id,
            skill_ids=matched_skill_ids,
            difficulty=difficulty,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # 批量计算所有 session 的进度
        session_ids = [s.id for s, _ in sessions_with_details]
        progress_map = await InterviewQuestionDao.batch_calculate_progress(session_ids)

        # 批量加载所有需要的 skill_name（每个 skill_id 只加载一次）
        unique_skill_ids = list(set(s.skill_id for s, _ in sessions_with_details))
        skill_name_cache = {}
        for sid in unique_skill_ids:
            skill = SkillService.get_skill_by_id(sid)
            skill_name_cache[sid] = skill.get("name", "") if skill else ""

        # 组装结果
        enriched = []
        for session_obj, total_score in sessions_with_details:
            skill_name = skill_name_cache.get(session_obj.skill_id, "")
            progress = progress_map.get(session_obj.id, {"current": 0, "total": 0})
            enriched.append({
                "session": session_obj,
                "skill_name": skill_name,
                "total_score": total_score,
                "progress": progress,
            })

        # 构建响应
        session_resps = [
            _session_to_resp(
                item["session"],
                skill_name=item["skill_name"],
                total_score=item["total_score"],
            )
            for item in enriched
        ]
        # 给每个 session_resp 填充 progress
        for resp_obj, item in zip(session_resps, enriched):
            resp_obj.progress = item["progress"]

        data = InterviewHistoryResp(
            sessions=session_resps,
            total=total,
            page=page,
            page_size=page_size,
        )
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get interview history error: {err}")
        return resp_500(message=str(err))


@router.delete("/interview/session/{session_id}", response_model=UnifiedResponseModel)
async def delete_interview_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Delete an interview session and all related data."""
    try:
        session = await InterviewService.get_session(session_id)
        if session is None:
            return resp_404(message="Session not found")

        if session.user_id != login_user.user_id:
            return resp_403(message="Unauthorized")

        await InterviewService.delete_session(session_id)
        return resp_200(data=None)
    except Exception as err:
        logger.error(f"Delete interview session error: {err}")
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
            return resp_404(message=f"Skill not found: {skill_id}")

        data = _skill_to_detail(skill)
        return resp_200(data=data.model_dump())
    except Exception as err:
        logger.error(f"Get skill detail error: {err}")
        return resp_500(message=str(err))


# ---------------------------------------------------------------------------
# Learning path endpoints
# ---------------------------------------------------------------------------


@router.get("/interview/learning-path/{skill_id}", response_model=UnifiedResponseModel)
async def get_learning_path(
    skill_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    """Get personalized learning path based on interview history."""
    try:
        path = await LearningService.get_learning_path(
            user_id=login_user.user_id,
            skill_id=skill_id,
        )
        if path is None:
            return resp_404(message=f"Skill not found: {skill_id}")
        return resp_200(data=path)
    except Exception as err:
        logger.error(f"Get learning path error: {err}")
        return resp_500(message=str(err))


@router.get("/interview/evaluation/{evaluation_id}/pdf")
async def download_evaluation_pdf(
    evaluation_id: str,
    background_tasks: BackgroundTasks,
    login_user: UserPayload = Depends(get_login_user),
):
    """下载面试评估报告 PDF（含逐题详情）。"""
    try:
        report = await EvaluationService.get_report_by_id(evaluation_id)
        if not report:
            return resp_404(message="评估报告不存在")

        from kirinchat.api.services.skill import SkillService
        from kirinchat.common.export.pdf_service import PdfService

        session = await InterviewService.get_session(report.session_id)
        skill = SkillService.get_skill_by_id(session.skill_id) if session else None
        skill_name = skill.get("name", "未知") if skill else "未知"

        # 获取逐题详情
        details = await EvaluationService.get_details_by_evaluation(evaluation_id)
        questions = await InterviewService.get_session_questions(report.session_id) if session else []
        q_map = {q.id: q for q in questions}

        question_details = []
        for d in details:
            q = q_map.get(d.question_id)
            question_details.append({
                "content": q.content if q else "",
                "user_answer": q.user_answer if q else "",
                "score": d.score,
                "feedback": d.feedback,
                "reference_answer": d.reference_answer,
            })

        report_data = {
            "total_score": report.total_score,
            "category_scores": report.category_scores,
            "summary": report.summary,
            "strengths": report.strengths,
            "improvements": report.improvements,
            "question_details": question_details,
        }

        # 使用 UUID 生成唯一临时文件路径，避免并发冲突
        output_path = make_temp_path(suffix=".pdf")
        PdfService.generate_evaluation_report(report_data, skill_name, output_path)

        # 注册后台任务：响应发送完成后清理临时文件
        background_tasks.add_task(cleanup_temp_file, output_path)
        return FileResponse(output_path, filename=f"evaluation_{evaluation_id}.pdf", media_type="application/pdf")
    except Exception as e:
        logger.exception("Download evaluation PDF failed")
        return resp_500(message=str(e))
