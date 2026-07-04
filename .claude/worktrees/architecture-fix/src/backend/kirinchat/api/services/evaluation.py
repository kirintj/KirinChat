import json
import logging

from kirinchat.api.services.interview import InterviewService
from kirinchat.core.models.manager import ModelManager
from kirinchat.database.dao.interview import (
    EvaluationReportDao,
    InterviewQuestionDao,
)
from kirinchat.database.models.interview import EvaluationReportTable

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating interview sessions via LLM-based scoring."""

    DEFAULT_BATCH_SIZE = 8

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    async def evaluate_session(cls, session_id):
        """Evaluate an interview session -- main entry point.

        Flow:
        1. Fetch all questions for the session.
        2. Split into batches.
        3. Evaluate each batch via LLM (skip on failure).
        4. Merge batch results.
        5. Generate a summary via LLM (fallback to default on failure).
        6. Save the report.
        7. Update individual question scores.
        8. Update session status to EVALUATED.
        """
        questions = await InterviewService.get_session_questions(session_id)

        if not questions:
            report = await cls._save_default_report(session_id)
            await InterviewService.update_session_status(session_id, "EVALUATED")
            return report

        # Convert question objects to dicts for easier manipulation
        question_dicts = [cls._question_to_dict(q) for q in questions]
        batches = cls._batch_questions(question_dicts, cls.DEFAULT_BATCH_SIZE)

        batch_results = []
        for batch in batches:
            try:
                result = await cls._evaluate_batch(batch)
                if result is not None:
                    batch_results.append(result)
            except Exception:
                logger.exception("Batch evaluation failed for batch of %d questions", len(batch))

        if not batch_results:
            report = await cls._save_default_report(session_id)
            await InterviewService.update_session_status(session_id, "EVALUATED")
            return report

        merged = cls._merge_batch_results(batch_results)

        # Second-pass summary
        try:
            summary = await cls._summarize_evaluation(merged)
            if summary:
                merged["summary"] = summary
        except Exception:
            logger.exception("Summary generation failed, using default summary")
            if not merged.get("summary"):
                merged["summary"] = "评估完成，但自动生成总结时出现错误。"

        # Ensure required fields
        merged.setdefault("summary", "评估完成。")
        merged.setdefault("strengths", [])
        merged.setdefault("improvements", [])
        merged.setdefault("total_score", 0.0)
        merged.setdefault("category_scores", {})

        # Save report
        report = EvaluationReportTable(
            session_id=session_id,
            total_score=merged["total_score"],
            category_scores=merged["category_scores"],
            summary=merged["summary"],
            strengths=merged["strengths"],
            improvements=merged["improvements"],
        )
        report = await EvaluationReportDao.create_report(report)

        # Update question scores
        for qs in merged.get("question_scores", []):
            qid = qs.get("id")
            score = qs.get("score")
            if qid and score is not None:
                try:
                    await InterviewQuestionDao.update_question_score(qid, float(score))
                except Exception:
                    logger.exception("Failed to update score for question %s", qid)

        # Update session status
        await InterviewService.update_session_status(session_id, "EVALUATED")
        return report

    @classmethod
    async def get_report_by_id(cls, report_id):
        """Get an evaluation report by its ID."""
        return await EvaluationReportDao.select_report_by_id(report_id)

    @classmethod
    async def get_report_by_session(cls, session_id):
        """Get an evaluation report by session ID."""
        return await EvaluationReportDao.select_report_by_session(session_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _batch_questions(cls, questions, batch_size=DEFAULT_BATCH_SIZE):
        """Split questions into batches of ``batch_size``."""
        if not questions:
            return []
        return [
            questions[i : i + batch_size]
            for i in range(0, len(questions), batch_size)
        ]

    @classmethod
    async def _evaluate_batch(cls, batch):
        """Evaluate a single batch of questions via LLM."""
        prompt = cls._build_evaluation_prompt(batch)
        llm = ModelManager.get_conversation_model()
        response = await llm.ainvoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        return cls._parse_evaluation_result(content, batch)

    @classmethod
    async def _summarize_evaluation(cls, merged):
        """Generate a human-readable summary of the merged evaluation."""
        summary_prompt = (
            "你是一位专业的面试评估专家。请根据以下评估结果，撰写一段简洁的中文评估总结（3-5句话）。\n\n"
            f"总分: {merged.get('total_score', 0)}\n"
            f"分类得分: {json.dumps(merged.get('category_scores', {}), ensure_ascii=False)}\n"
            f"优势: {', '.join(merged.get('strengths', []))}\n"
            f"改进: {', '.join(merged.get('improvements', []))}\n\n"
            "请直接输出总结文本，不要使用 Markdown 格式。"
        )
        llm = ModelManager.get_conversation_model()
        response = await llm.ainvoke(summary_prompt)
        content = response.content if hasattr(response, "content") else str(response)
        return content.strip() if content else None

    @classmethod
    def _build_evaluation_prompt(cls, batch):
        """Build the LLM prompt for evaluating a batch of questions."""
        questions_text = ""
        for q in batch:
            questions_text += (
                f"题目ID: {q.get('id', 'unknown')}\n"
                f"分类: {q.get('category', 'general')}\n"
                f"问题: {q.get('content', '')}\n"
                f"回答: {q.get('answer', '未作答')}\n\n"
            )

        return (
            "你是一位专业的面试评估专家。请对以下面试题目和回答进行评估。\n\n"
            "请严格以如下 JSON 格式输出（不要输出其他内容）：\n"
            "```json\n"
            "{\n"
            '  "category_scores": {"分类名": 分数(0-10)},\n'
            '  "question_scores": [\n'
            '    {"id": "题目ID", "score": 分数(0-10), "feedback": "简短评价"}\n'
            "  ],\n"
            '  "strengths": ["优势1", "优势2"],\n'
            '  "improvements": ["改进1", "改进2"]\n'
            "}\n"
            "```\n\n"
            f"待评估题目（共 {len(batch)} 道）:\n\n"
            f"{questions_text}"
        )

    @classmethod
    def _parse_evaluation_result(cls, content, batch):
        """Parse the LLM evaluation response into a structured dict."""
        try:
            # Try to extract JSON from the response
            text = content.strip()
            # Handle markdown code blocks
            if "```" in text:
                # Extract content between ``` markers
                parts = text.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    if part.startswith("{"):
                        text = part
                        break

            result = json.loads(text)

            # Validate and normalize
            category_scores = result.get("category_scores", {})
            question_scores = result.get("question_scores", [])

            # Ensure all questions from the batch have a score entry
            scored_ids = {qs.get("id") for qs in question_scores}
            for q in batch:
                qid = q.get("id")
                if qid and qid not in scored_ids:
                    question_scores.append({"id": qid, "score": 0.0, "feedback": "未评分"})

            return {
                "category_scores": {k: float(v) for k, v in category_scores.items()},
                "question_scores": question_scores,
                "strengths": result.get("strengths", []),
                "improvements": result.get("improvements", []),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            logger.warning("Failed to parse LLM evaluation result")
            return None

    @classmethod
    def _merge_batch_results(cls, batch_results):
        """Merge results from multiple batches into a single evaluation."""
        if not batch_results:
            return {
                "total_score": 0.0,
                "category_scores": {},
                "question_scores": [],
                "strengths": [],
                "improvements": [],
            }

        merged_categories = {}
        all_question_scores = []
        all_strengths = []
        all_improvements = []

        # Collect category scores -- average across batches
        category_counts = {}
        for result in batch_results:
            for cat, score in result.get("category_scores", {}).items():
                if cat not in merged_categories:
                    merged_categories[cat] = 0.0
                    category_counts[cat] = 0
                merged_categories[cat] += float(score)
                category_counts[cat] += 1

            all_question_scores.extend(result.get("question_scores", []))
            all_strengths.extend(result.get("strengths", []))
            all_improvements.extend(result.get("improvements", []))

        # Average category scores
        for cat in merged_categories:
            count = category_counts[cat]
            if count > 0:
                merged_categories[cat] = round(merged_categories[cat] / count, 1)

        # Compute total score as average of all question scores
        scores = [
            float(qs.get("score", 0))
            for qs in all_question_scores
            if qs.get("score") is not None
        ]
        total_score = round(sum(scores) / len(scores), 1) if scores else 0.0

        return {
            "total_score": total_score,
            "category_scores": merged_categories,
            "question_scores": all_question_scores,
            "strengths": all_strengths,
            "improvements": all_improvements,
        }

    @classmethod
    def _question_to_dict(cls, q):
        """Convert a question ORM object to a plain dict."""
        return {
            "id": q.id,
            "content": q.content,
            "answer": q.user_answer or "未作答",
            "category": getattr(q, "category", "general"),
            "type": getattr(q, "type", "MAIN"),
        }

    @classmethod
    def _build_default_report(cls):
        """Build a default (empty) evaluation report dict."""
        return {
            "total_score": 0.0,
            "summary": "暂无评估数据。",
            "category_scores": {},
            "strengths": [],
            "improvements": [],
        }

    @classmethod
    async def _save_default_report(cls, session_id):
        """Save a default evaluation report to the database."""
        default = cls._build_default_report()
        report = EvaluationReportTable(
            session_id=session_id,
            total_score=default["total_score"],
            category_scores=default["category_scores"],
            summary=default["summary"],
            strengths=default["strengths"],
            improvements=default["improvements"],
        )
        return await EvaluationReportDao.create_report(report)
