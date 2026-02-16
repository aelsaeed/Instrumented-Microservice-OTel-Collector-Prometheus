#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v docker >/dev/null 2>&1 && [ -f "otel-microservice-lab/infra/docker-compose.yml" ]; then
  docker compose -f otel-microservice-lab/infra/docker-compose.yml config >/dev/null
  echo "docker compose config validation passed"
else
  echo "docker or docker compose config unavailable; skipping compose validation"
fi

python3 - <<'PY'
import os
from fastapi.testclient import TestClient

os.environ["OTEL_LAB_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["OTEL_LAB_REDIS_URL"] = "memory://"
os.environ["OTEL_LAB_CELERY_BROKER_URL"] = "memory://"
os.environ["OTEL_LAB_CELERY_RESULT_BACKEND"] = "cache+memory://"

import sys
sys.path.insert(0, "otel-microservice-lab")
from app.main import app

client = TestClient(app)
resp = client.get("/health")
assert resp.status_code == 200, resp.text
assert resp.json().get("status") == "ok", resp.text
print("smoke /health passed")
PY
