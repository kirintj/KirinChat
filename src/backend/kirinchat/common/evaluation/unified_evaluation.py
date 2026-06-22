"""统一评估引擎 — 供文本面试和未来语音面试共用。"""

from kirinchat.api.services.evaluation import EvaluationService


class UnifiedEvaluationService:
    """统一评估引擎代理，委托给现有 EvaluationService。"""

    @classmethod
    async def evaluate(cls, session_id: str) -> dict:
        report = await EvaluationService.evaluate_session(session_id)
        return {
            "total_score": report.total_score,
            "category_scores": report.category_scores,
            "summary": report.summary,
            "strengths": report.strengths,
            "improvements": report.improvements,
        }
