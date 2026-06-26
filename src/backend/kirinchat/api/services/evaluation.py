import json
import asyncio
import logging

from kirinchat.api.services.interview import InterviewService
from kirinchat.core.models.manager import ModelManager
from kirinchat.database.dao.interview import (
    EvaluationReportDao,
    InterviewQuestionDao,
    EvaluationQuestionDetailDao,
)
from kirinchat.database.models.interview import EvaluationReportTable, EvaluationQuestionDetailTable
from kirinchat.utils.llm_parser import parse_llm_json

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating interview sessions via LLM-based scoring."""

    DEFAULT_BATCH_SIZE = 8

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    async def evaluate_session(cls, session_id):
        """Evaluate an interview session -- main entry point."""
        questions = await InterviewService.get_session_questions(session_id)

        if not questions:
            report = await cls._save_default_report(session_id)
            await InterviewService.update_session_status(session_id, "EVALUATED")
            return report

        question_dicts = [cls._question_to_dict(q) for q in questions]
        batches = cls._batch_questions(question_dicts, cls.DEFAULT_BATCH_SIZE)

        # [P4] 并行评估所有批次
        tasks = [cls._evaluate_batch_safe(batch) for batch in batches]
        batch_results = await asyncio.gather(*tasks)
        batch_results = [r for r in batch_results if r is not None]

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

        report = EvaluationReportTable(
            session_id=session_id,
            total_score=merged["total_score"],
            category_scores=merged["category_scores"],
            summary=merged["summary"],
            strengths=merged["strengths"],
            improvements=merged["improvements"],
        )
        report = await EvaluationReportDao.create_report(report)

        # 持久化逐题评估详情（得分 + 反馈 + 参考答案）
        detail_objects = []
        for qs in merged.get("question_scores", []):
            qid = qs.get("id")
            score = qs.get("score")
            if qid and score is not None:
                detail = EvaluationQuestionDetailTable(
                    evaluation_id=report.id,
                    question_id=qid,
                    score=int(float(score)),
                    feedback=qs.get("feedback", ""),
                    reference_answer=qs.get("reference_answer", ""),
                )
                detail_objects.append(detail)
        if detail_objects:
            await EvaluationQuestionDetailDao.batch_create(detail_objects)

        await InterviewService.update_session_status(session_id, "EVALUATED")
        return report

    @classmethod
    async def get_report_by_id(cls, report_id):
        return await EvaluationReportDao.select_report_by_id(report_id)

    @classmethod
    async def get_report_by_session(cls, session_id):
        return await EvaluationReportDao.select_report_by_session(session_id)

    @classmethod
    async def get_details_by_evaluation(cls, evaluation_id: str):
        """获取评估报告的逐题详情列表。"""
        return await EvaluationQuestionDetailDao.select_by_evaluation_id(evaluation_id)

    @classmethod
    async def get_detail_by_question(cls, question_id: str):
        """获取单题的评估详情。"""
        return await EvaluationQuestionDetailDao.select_by_question_id(question_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _batch_questions(cls, questions, batch_size=DEFAULT_BATCH_SIZE):
        if not questions:
            return []
        return [
            questions[i : i + batch_size]
            for i in range(0, len(questions), batch_size)
        ]

    @classmethod
    async def _evaluate_batch_safe(cls, batch):
        """安全评估单个批次，失败返回 None。"""
        try:
            return await cls._evaluate_batch(batch)
        except Exception:
            logger.exception("Batch evaluation failed for batch of %d questions", len(batch))
            return None

    @classmethod
    async def _evaluate_batch(cls, batch):
        prompt = cls._build_evaluation_prompt(batch)
        llm = ModelManager.get_conversation_model()
        response = await llm.ainvoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        return cls._parse_evaluation_result(content, batch)

    @classmethod
    async def _summarize_evaluation(cls, merged):
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
            '    {"id": "题目ID", "score": 分数(0-10), "feedback": "简短评价(50字以内)", "reference_answer": "该题的标准参考答案(100字以内)"}\n'
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
            result = parse_llm_json(content)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse LLM evaluation result")
            return None

        category_scores = result.get("category_scores", {})
        question_scores = result.get("question_scores", [])

        scored_ids = {qs.get("id") for qs in question_scores}
        for q in batch:
            qid = q.get("id")
            if qid and qid not in scored_ids:
                question_scores.append({"id": qid, "score": 0.0, "feedback": "未评分", "reference_answer": ""})

        try:
            normalized_categories = {k: float(v) for k, v in category_scores.items()}
        except (ValueError, TypeError):
            normalized_categories = {}

        return {
            "category_scores": normalized_categories,
            "question_scores": question_scores,
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", []),
        }

    @classmethod
    def _merge_batch_results(cls, batch_results):
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

        for cat in merged_categories:
            count = category_counts[cat]
            if count > 0:
                merged_categories[cat] = round(merged_categories[cat] / count, 1)

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
        return {
            "id": q.id,
            "content": q.content,
            "answer": q.user_answer or "未作答",
            "category": getattr(q, "category", "general"),
            "type": getattr(q, "type", "MAIN"),
        }

    @classmethod
    def _build_default_report(cls):
        return {
            "total_score": 0.0,
            "summary": "暂无评估数据。",
            "category_scores": {},
            "strengths": [],
            "improvements": [],
        }

    @classmethod
    async def _save_default_report(cls, session_id):
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

    @staticmethod
    async def _update_question_score_safe(qid: str, score: float):
        try:
            await InterviewQuestionDao.update_question_score(qid, score)
        except Exception:
            logger.exception("Failed to update score for question %s", qid)
