from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager

from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "path"],
)
CACHE_HITS = Counter("cache_hits_total", "Cache hits", ["cache"])
CACHE_MISSES = Counter("cache_misses_total", "Cache misses", ["cache"])
QUEUE_DEPTH = Gauge("worker_queue_depth", "Celery queue depth")
DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],
)


@contextmanager
def track_request(method: str, path: str) -> Iterator[callable]:
    start = time.perf_counter()
    status_code: str = "500"

    def _record(status: int) -> None:
        nonlocal status_code
        status_code = str(status)

    try:
        yield _record
    finally:
        duration = time.perf_counter() - start
        REQUEST_COUNT.labels(method=method, path=path, status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
