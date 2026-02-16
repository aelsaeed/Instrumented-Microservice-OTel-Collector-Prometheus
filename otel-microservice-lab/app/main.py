from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pythonjsonlogger import jsonlogger
from sqlalchemy import select

from app.cache import get_cache
from app.config import settings
from app.db import Base, engine, get_session
from app.metrics import CACHE_HITS, CACHE_MISSES, DB_QUERY_LATENCY, QUEUE_DEPTH, track_request
from app.models import Item
from app.otel import configure_otel, instrument_app
from app.schemas import ItemCreate, ItemRead
from worker.client import enqueue_enrichment

logger = logging.getLogger("otel_lab")


def configure_logging() -> None:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("%(levelname)s %(message)s %(name)s %(asctime)s")
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(settings.otel_log_level)
    root.handlers = [handler]


class RequestIdMiddleware:
    def __init__(self, app: FastAPI) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):  # type: ignore[override]
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = None
        headers = dict(scope.get("headers") or [])
        if b"x-request-id" in headers:
            request_id = headers[b"x-request-id"].decode()
        if not request_id:
            request_id = str(uuid.uuid4())

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"].append((b"x-request-id", request_id.encode()))
            await send(message)

        scope["request_id"] = request_id
        await self.app(scope, receive, send_wrapper)


app = FastAPI()


@app.on_event("startup")
async def startup() -> None:
    configure_logging()
    configure_otel()
    Base.metadata.create_all(bind=engine)
    await instrument_app(app)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    with track_request(request.method, request.url.path) as record:
        response: Response = await call_next(request)
        record(response.status_code)
    logger.info(
        "request_complete",
        extra={
            "request_id": request.scope.get("request_id"),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )
    return response


app.add_middleware(RequestIdMiddleware)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/items", response_model=ItemRead)
async def create_item(payload: ItemCreate) -> ItemRead:
    def _create() -> Item:
        with get_session() as session, DB_QUERY_LATENCY.labels(operation="insert").time():
            item = Item(name=payload.name, description=payload.description)
            session.add(item)
            session.flush()
            session.refresh(item)
            return item

    item = await run_in_threadpool(_create)
    enqueue_enrichment(str(item.id))
    try:
        import redis

        client = redis.Redis.from_url(settings.celery_broker_url)
        QUEUE_DEPTH.set(client.llen("celery"))
    except Exception as exc:  # pragma: no cover
        logger.warning("queue depth update failed", extra={"error": str(exc)})
    return ItemRead(
        id=item.id,
        name=item.name,
        description=item.description,
        enrichment=item.enrichment,
        enriched_at=item.enriched_at,
    )


@app.get("/items/{item_id}", response_model=ItemRead)
async def get_item(item_id: str) -> ItemRead:
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid item id") from exc
    cache_key = f"item:{item_id}"
    cache = get_cache()
    cache_result = await run_in_threadpool(cache.get, cache_key)
    if cache_result.hit:
        CACHE_HITS.labels(cache="redis").inc()
        return ItemRead(**cache_result.value)
    CACHE_MISSES.labels(cache="redis").inc()

    def _read() -> Item | None:
        with get_session() as session:
            stmt = select(Item).where(Item.id == item_uuid)
            with DB_QUERY_LATENCY.labels(operation="select").time():
                return session.scalar(stmt)

    item = await run_in_threadpool(_read)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    payload = ItemRead(
        id=item.id,
        name=item.name,
        description=item.description,
        enrichment=item.enrichment,
        enriched_at=item.enriched_at,
    )
    await run_in_threadpool(cache.set, cache_key, payload.model_dump(), settings.cache_ttl_seconds)
    return payload


@app.get("/metrics")
async def metrics_endpoint() -> Response:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.on_event("startup")
async def set_queue_depth_job() -> None:
    try:
        import redis

        client = redis.Redis.from_url(settings.celery_broker_url)
        depth = client.llen("celery")
        QUEUE_DEPTH.set(depth)
    except Exception as exc:  # pragma: no cover
        logger.warning("queue depth check failed", extra={"error": str(exc)})
