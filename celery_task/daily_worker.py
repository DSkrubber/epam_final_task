"""Defines celery task for workers and daily schedule for beats"""
from celery import Celery
from celery.schedules import crontab

from data.add_today import add_today_weather

celery = Celery("celery_task.daily_worker")
celery.conf.beat_schedule = {
    "update_db_daily": {
        "task": "celery_task.daily_worker.daily_update",
        "schedule": crontab(),
    },
}
celery.conf.timezone = "UTC"


@celery.task
def daily_update() -> None:
    """Task for celery worker.
    Runs daily "add_today_weather" function which adds new weather data into
    database for all cities.

    """
    add_today_weather()
