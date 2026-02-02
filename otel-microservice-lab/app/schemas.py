from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None


class ItemRead(BaseModel):
    id: UUID
    name: str
    description: str | None
    enrichment: str | None
    enriched_at: datetime | None
