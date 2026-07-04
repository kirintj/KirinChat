import asyncio
from loguru import logger

from kirinchat.common.async_task.celery_app import celery_app


@celery_app.task(bind=True, max_retries=1)
def evaluate_interview_task(self, session_id: str):
    """异步评估面试会话。"""
    try:
        asyncio.run(_evaluate(session_id))
    except Exception as exc:
        logger.exception("Interview evaluation failed for %s", session_id)
        raise


async def _evaluate(session_id: str):
    from kirinchat.api.services.evaluation import EvaluationService
    await EvaluationService.evaluate_session(session_id)
