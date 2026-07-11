import asyncio
from loguru import logger

from kirinchat.common.async_task.celery_app import celery_app


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=120,
    retry_jitter=True,
    deadletter_queue="dead_letter",
)
def evaluate_interview_task(self, session_id: str):
    """异步评估面试会话。

    失败时自动重试（最多 3 次），指数退避（30s→60s→120s）。
    超过最大重试次数后，任务被路由到 dead_letter 队列。
    """
    try:
        asyncio.run(_evaluate(session_id))
    except Exception as exc:
        logger.exception("Interview evaluation failed for %s (attempt %d/%d)",
                         session_id, self.request.retries + 1, self.max_retries + 1)
        raise


async def _evaluate(session_id: str):
    from kirinchat.api.services.evaluation import EvaluationService
    await EvaluationService.evaluate_session(session_id)
