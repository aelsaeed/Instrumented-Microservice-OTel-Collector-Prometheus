# Instrumented-Microservice-OTel-Collector-Prometheus

This repository contains the **otel-microservice-lab** project: a production-style FastAPI microservice with PostgreSQL persistence, Redis cache-aside, a Celery worker, and a full local OpenTelemetry stack (Collector, Jaeger, Prometheus, Grafana).

## Quickstart

```bash
cd otel-microservice-lab
make up
```

Key endpoints and dashboards:

- API: http://localhost:8000
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics
- Jaeger: http://localhost:16686
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (anonymous access enabled)

## What’s Inside

- `otel-microservice-lab/` — FastAPI app, worker, infra configs, dashboards, and tests.
- `otel-microservice-lab/infra/` — Docker Compose plus OpenTelemetry Collector, Prometheus, Grafana configs.
- `otel-microservice-lab/scripts/` — Load test script (k6).

For full documentation, see: [otel-microservice-lab/README.md](otel-microservice-lab/README.md)
