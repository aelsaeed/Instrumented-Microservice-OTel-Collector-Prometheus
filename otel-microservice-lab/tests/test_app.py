from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def build_client() -> TestClient:
    import os

    os.environ["OTEL_LAB_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    os.environ["OTEL_LAB_REDIS_URL"] = "memory://"
    os.environ["OTEL_LAB_CELERY_BROKER_URL"] = "memory://"
    os.environ["OTEL_LAB_CELERY_RESULT_BACKEND"] = "cache+memory://"

    import app.config as config
    import app.db as db
    import app.main as main

    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(main)

    return TestClient(main.app)


def test_create_and_get_item() -> None:
    client = build_client()
    response = client.post("/items", json={"name": "widget", "description": "test"})
    assert response.status_code == 200
    item_id = response.json()["id"]

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "widget"


def test_health() -> None:
    client = build_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
