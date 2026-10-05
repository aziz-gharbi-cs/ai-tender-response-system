from celery import Celery

from app.core.config import settings

broker_url = (
    f"redis://{settings.redis_host}:{settings.redis_port}/0"
)

result_backend = (
    f"redis://{settings.redis_host}:{settings.redis_port}/1"
)


celery_app = Celery(
    "ai_tender_response_system",
    broker=broker_url,
    backend=result_backend,
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


celery_app.autodiscover_tasks(
    packages=["app.infrastructure.queue"],
)
