from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "fastapi_celery",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=['app.tasks']  # This ensures all tasks are discovered
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Add periodic tasks
celery_app.conf.beat_schedule = {
    "run-every-2-minutes": {
        "task": "app.tasks.periodic.test_periodic_task",
        "schedule": crontab(minute='*/2'),  # Every 2 minutes
    },
}