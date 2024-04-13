from celery import Celery

from bot.settings import settings


job_queue = Celery("bot", broker=settings.redis_dsn)
