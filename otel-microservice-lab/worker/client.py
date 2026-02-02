from __future__ import annotations

from celery import Celery

from app.config import settings

celery_client = Celery(
    "otel_lab_client",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


def enqueue_enrichment(item_id: str) -> None:
    celery_client.send_task("worker.tasks.enrich_item", args=[item_id])
