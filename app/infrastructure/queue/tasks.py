from app.infrastructure.queue.celery_app import celery_app


@celery_app.task
def health_check_task() -> dict[str, str]:
    """
    Simple infrastructure test task.

    This will later be replaced/expanded with tasks that
    execute document processing and proposal generation.
    """

    return {
        "status": "ok",
        "message": "Celery worker is running.",
    }
