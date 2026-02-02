from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import redis

from app.config import settings


@dataclass
class CacheResult:
    value: dict[str, Any] | None
    hit: bool


class CacheBackend:
    def get(self, key: str) -> CacheResult:  # pragma: no cover - interface
        raise NotImplementedError

    def set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:  # pragma: no cover
        raise NotImplementedError


class RedisCache(CacheBackend):
    def __init__(self, url: str) -> None:
        self.client = redis.Redis.from_url(url)

    def get(self, key: str) -> CacheResult:
        raw = self.client.get(key)
        if raw is None:
            return CacheResult(value=None, hit=False)
        return CacheResult(value=json.loads(raw), hit=True)

    def set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        self.client.setex(key, ttl_seconds, json.dumps(value))


class MemoryCache(CacheBackend):
    def __init__(self) -> None:
        self.data: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> CacheResult:
        value = self.data.get(key)
        if value is None:
            return CacheResult(value=None, hit=False)
        return CacheResult(value=value, hit=True)

    def set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        self.data[key] = value


_cache: CacheBackend | None = None


def get_cache() -> CacheBackend:
    global _cache
    if _cache is None:
        if settings.redis_url.startswith("memory://"):
            _cache = MemoryCache()
        else:
            _cache = RedisCache(settings.redis_url)
    return _cache
