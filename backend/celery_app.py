"""
Celery Application — broker + backend both use Redis.
Configures Beat schedule for daily practice generation and user reminders.
"""
import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "aptiverse",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["celery_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Keep results for 1 hour
    result_expires=3600,
    # Beat schedule
    beat_schedule={
        # Pre-warm practice set cache for all active users at 07:00 UTC
        "generate-daily-practice": {
            "task": "celery_tasks.generate_practice_sets_for_all_users",
            "schedule": crontab(hour=7, minute=0),
        },
        # Send reminder emails at 08:00 UTC to users who haven't practiced today
        "send-practice-reminders": {
            "task": "celery_tasks.send_practice_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        # Nudge users who haven't been active for 48 hours — runs every 6 hours
        "nudge-inactive-users": {
            "task": "celery_tasks.nudge_inactive_users",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
)
