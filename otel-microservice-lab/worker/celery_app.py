from __future__ import annotations

from celery import Celery

from app.config import settings
from worker.otel import configure_otel

celery_app = Celery(
    "otel_lab",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.task_acks_late = True
celery_app.conf.task_default_queue = "celery"

configure_otel()
