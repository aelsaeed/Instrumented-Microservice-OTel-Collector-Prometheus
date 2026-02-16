from __future__ import annotations

import importlib
import os

from fastapi.testclient import TestClient

os.environ["OTEL_LAB_DATABASE_URL"] = "sqlite+pysqlite:///./test.db"
os.environ["OTEL_LAB_REDIS_URL"] = "memory://"
os.environ["OTEL_LAB_CELERY_BROKER_URL"] = "memory://"
os.environ["OTEL_LAB_CELERY_RESULT_BACKEND"] = "cache+memory://"

import app.config as config
import app.db as db
import app.main as main
from app.db import Base, engine

importlib.reload(config)
importlib.reload(db)
importlib.reload(main)


def test_create_and_get_item() -> None:
    Base.metadata.create_all(bind=engine)
    with TestClient(main.app) as client:
        response = client.post("/items", json={"name": "widget", "description": "test"})
        assert response.status_code == 200
        item_id = response.json()["id"]

        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "widget"


def test_health() -> None:
    Base.metadata.create_all(bind=engine)
    with TestClient(main.app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
