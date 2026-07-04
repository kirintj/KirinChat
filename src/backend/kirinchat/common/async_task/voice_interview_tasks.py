import asyncio

from loguru import logger
from kirinchat.common.async_task.celery_app import celery_app


@celery_app.task(bind=True, max_retries=1)
def voice_interview_evaluation_task(self, session_id: str):
    """Evaluate a completed voice interview session via LLM scoring."""
    try:
        asyncio.run(_evaluate(session_id))
    except Exception as exc:
        logger.exception("Voice interview evaluation failed for %s", session_id)
        raise


async def _evaluate(session_id: str):
    from kirinchat.api.services.voice_interview import VoiceInterviewService
    from kirinchat.database.dao.voice_interview import VoiceInterviewSessionDao

    session = await VoiceInterviewService.get_session(session_id)
    if not session:
        logger.warning("Session %s not found, skipping evaluation", session_id)
        return

    # Ensure evaluation record exists and mark PROCESSING
    eval_record = await VoiceInterviewService.get_evaluation(session_id)
    if not eval_record:
        eval_record = await VoiceInterviewService.create_evaluation_placeholder(session_id)
    # Mark session as PROCESSING
    await VoiceInterviewSessionDao.update_session(session_id, evaluate_status="PROCESSING")

    try:
        # Build QA records from messages
        messages = await VoiceInterviewService.get_messages(session_id)
        qa_pairs = _build_qa_pairs(messages)

        if not qa_pairs:
            logger.warning("No QA pairs found for session %s, saving empty evaluation", session_id)
            await VoiceInterviewService.update_evaluation(
                eval_record.id,
                overall_score=0.0,
                overall_feedback="暂无评估数据。",
            )
            await VoiceInterviewSessionDao.update_session(session_id, evaluate_status="COMPLETED")
            return

        # Call LLM to evaluate
        result = await _evaluate_with_llm(qa_pairs)

        # Save results
        await VoiceInterviewService.update_evaluation(
            eval_record.id,
            overall_score=result.get("overall_score", 0.0),
            overall_feedback=result.get("overall_feedback", ""),
            category_scores=result.get("category_scores", {}),
            question_evaluations=result.get("question_evaluations", []),
            strengths=result.get("strengths", []),
            improvements=result.get("improvements", []),
            reference_answers=result.get("reference_answers", []),
        )

        await VoiceInterviewSessionDao.update_session(session_id, evaluate_status="COMPLETED")
        logger.info("Voice interview evaluation completed for session %s", session_id)

    except Exception:
        logger.exception("Evaluation processing failed for session %s", session_id)
        await VoiceInterviewSessionDao.update_session(session_id, evaluate_status="FAILED")
        raise


def _build_qa_pairs(messages) -> list[dict]:
    """Extract question/answer pairs from voice interview messages.

    Messages alternate: AI asks a question (ai_text set), then user answers
    (user_text set). A single message can contain both (e.g. the AI text from
    a previous turn and user text in the same logical exchange).
    """
    qa_pairs: list[dict] = []
    ai_q: str | None = None
    for msg in messages:
        if msg.ai_text:
            ai_q = msg.ai_text
        if msg.user_text and ai_q:
            qa_pairs.append({"question": ai_q, "answer": msg.user_text})
            ai_q = None
    return qa_pairs


async def _evaluate_with_llm(qa_pairs: list[dict]) -> dict:
    """Send QA pairs to the LLM and return structured evaluation results."""
    from kirinchat.core.models.manager import ModelManager
    from kirinchat.utils.llm_parser import parse_llm_json

    prompt = _build_evaluation_prompt(qa_pairs)
    llm = ModelManager.get_conversation_model()
    response = await llm.ainvoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    result = parse_llm_json(content)

    # Normalize and ensure all expected fields exist
    question_evaluations = result.get("question_evaluations", [])
    for i, qe in enumerate(question_evaluations):
        qe.setdefault("question", qa_pairs[i]["question"] if i < len(qa_pairs) else "")
        qe.setdefault("answer", qa_pairs[i]["answer"] if i < len(qa_pairs) else "")
        qe.setdefault("score", 0)
        qe.setdefault("feedback", "")

    overall_score = result.get("overall_score", 0)
    try:
        overall_score = float(overall_score)
    except (ValueError, TypeError):
        overall_score = 0.0

    category_scores = result.get("category_scores", {})
    try:
        category_scores = {k: float(v) for k, v in category_scores.items()}
    except (ValueError, TypeError):
        category_scores = {}

    return {
        "overall_score": overall_score,
        "overall_feedback": result.get("overall_feedback", ""),
        "category_scores": category_scores,
        "question_evaluations": question_evaluations,
        "strengths": result.get("strengths", []),
        "improvements": result.get("improvements", []),
        "reference_answers": result.get("reference_answers", []),
    }


def _build_evaluation_prompt(qa_pairs: list[dict]) -> str:
    """Build the LLM prompt for evaluating voice interview QA pairs."""
    questions_text = ""
    for i, pair in enumerate(qa_pairs, 1):
        questions_text += (
            f"--- 第 {i} 题 ---\n"
            f"问题: {pair['question']}\n"
            f"回答: {pair['answer']}\n\n"
        )

    return (
        "你是一位专业的面试评估专家。请对以下语音面试的问答对进行全面评估。\n\n"
        "请严格以如下 JSON 格式输出（不要输出其他内容）：\n"
        "```json\n"
        "{\n"
        '  "overall_score": 总分(0-100),\n'
        '  "overall_feedback": "总体评价（2-3句话）",\n'
        '  "category_scores": {"技术能力": 分数(0-10), "沟通表达": 分数(0-10), "逻辑思维": 分数(0-10)},\n'
        '  "question_evaluations": [\n'
        '    {"score": 分数(0-10), "feedback": "对本题的评价"}\n'
        "  ],\n"
        '  "strengths": ["优势1", "优势2"],\n'
        '  "improvements": ["改进建议1", "改进建议2"],\n'
        '  "reference_answers": [\n'
        '    {"question": "问题文本", "reference_answer": "参考答案"}\n'
        "  ]\n"
        "}\n"
        "```\n\n"
        f"待评估问答（共 {len(qa_pairs)} 道）:\n\n"
        f"{questions_text}"
    )
