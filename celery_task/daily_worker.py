"""Defines celery task for workers and daily schedule for beats"""
from celery import Celery
from celery.schedules import crontab
from requests import HTTPError
from sqlalchemy.exc import SQLAlchemyError

from data.add_today import add_today_weather

celery = Celery("celery_task.daily_worker")
celery.conf.beat_schedule = {
    "update_db_daily": {
        "task": "celery_task.daily_worker.daily_update",
        "schedule": crontab(),
    },
}
celery.conf.timezone = "UTC"


@celery.task(bind=True)
def daily_update(self) -> None:
    """Task for celery worker.
    Runs daily "add_today_weather" function which adds new weather data into
    database for all cities.

    """
    try:
        add_today_weather()
    except (HTTPError, SQLAlchemyError) as exc:
        raise self.retry(exc=exc, countdown=(60 * 30))
