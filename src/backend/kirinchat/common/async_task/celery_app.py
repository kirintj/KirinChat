from celery import Celery
from kirinchat.settings import app_settings

celery_app = Celery(
    "kirinchat",
    broker=app_settings.celery_broker_url,
    backend=app_settings.celery_result_backend,
    include=[
        "kirinchat.common.async_task.resume_tasks",
        "kirinchat.common.async_task.evaluation_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_soft_time_limit=300,
    task_time_limit=600,
    worker_max_tasks_per_child=100,
    task_default_retry_delay=60,
)
