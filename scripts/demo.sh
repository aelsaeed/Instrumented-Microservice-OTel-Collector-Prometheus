#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

compose_file="otel-microservice-lab/infra/docker-compose.yml"
base_url="http://localhost:8000"

if ! command -v docker >/dev/null 2>&1; then
  echo "[demo] Docker unavailable. Running dry-mode alternative."
  bash scripts/smoke_test.sh
  PYTHONPATH=otel-microservice-lab pytest otel-microservice-lab/tests/test_app.py -q
  echo "[demo] Dry mode complete."
  echo "[demo] For full observability flow (traces + dashboards), run on a machine with Docker:"
  echo "       make up && make demo"
  exit 0
fi

echo "[demo] Ensuring stack is running..."
docker compose -f "$compose_file" up -d --build

echo "[demo] Waiting for API health endpoint..."
for _ in {1..60}; do
  if curl -fsS "$base_url/health" >/dev/null; then
    break
  fi
  sleep 2
done
curl -fsS "$base_url/health" >/dev/null

echo "[demo] Sending small synthetic load to generate spans and metrics..."
for i in $(seq 1 8); do
  payload="{\"name\":\"demo-item-$i\",\"description\":\"observability-demo\"}"
  item_id="$(curl -fsS -X POST "$base_url/items" -H 'content-type: application/json' -d "$payload" | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')"
  curl -fsS "$base_url/items/$item_id" >/dev/null
  curl -fsS "$base_url/items/$item_id" >/dev/null
  sleep 0.2
done

echo
printf '[demo] Traces:      %s\n' "http://localhost:16686"
printf '[demo] Dashboards:  %s\n' "http://localhost:3000/d/otel-lab/otel-microservice-lab"
printf '[demo] Metrics UI:  %s\n' "http://localhost:9090"
echo "[demo] Endpoints generating spans:"
echo "  - POST /items"
echo "  - GET /items/{id}"
echo "  - GET /health"
echo "[demo] Done."
