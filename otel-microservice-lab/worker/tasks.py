from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

from celery import shared_task
from sqlalchemy import update

from app.db import get_session
from app.models import Item


@shared_task(name="worker.tasks.enrich_item")
def enrich_item(item_id: str) -> None:
    time.sleep(1.5)
    enrichment_payload = f"Enriched at {datetime.now(timezone.utc).isoformat()}"
    item_uuid = uuid.UUID(item_id)
    with get_session() as session:
        stmt = (
            update(Item)
            .where(Item.id == item_uuid)
            .values(enrichment=enrichment_payload, enriched_at=datetime.now(timezone.utc))
        )
        session.execute(stmt)
