# Otel Microservice Lab

A production-style FastAPI microservice with PostgreSQL persistence, Redis caching, a Celery worker, and a full local OpenTelemetry stack (Collector, Jaeger, Prometheus, Grafana).

## Quickstart

```bash
cd ..
make up
make demo
```

## Architecture

```
+---------------------+         +-----------------------+
|  FastAPI Service    |         |  Celery Worker        |
|  /items, /metrics   |         |  item_enrichment      |
+---------+-----------+         +----------+------------+
          |                                |
          | DB + Cache                     | DB
          v                                v
+---------------------+         +-----------------------+
|  Postgres           |         |  Redis (broker/cache) |
+---------------------+         +-----------------------+

Telemetry flow:
FastAPI + Worker -> OTEL Collector -> Jaeger (traces)
                                   -> Prometheus (metrics)
                                   -> Grafana (dashboards)
```

## Telemetry Flow

1. The app and worker emit traces, metrics, and logs via OTLP to the OpenTelemetry Collector.
2. The Collector exports traces to Jaeger and metrics to Prometheus.
3. Grafana reads Prometheus (metrics) to render pre-provisioned dashboards.

## Dashboards

Grafana dashboard includes:

- Request latency (p50/p95)
- Error rate (5xx)
- DB query time (p95)
- Cache hit rate
- Worker queue depth

## Endpoint behavior for traces

Use these endpoints to generate traces quickly:

- `POST /items` (DB insert + task enqueue)
- `GET /items/{id}` (cache miss/hit + DB lookup)
- `GET /health` (baseline service span)

## Local Development

```bash
make run
```

For linting and tests:

```bash
make lint
make test
```

## Project Layout

```
app/            # FastAPI app, db, cache, OpenTelemetry setup
worker/         # Celery worker tasks & OTEL setup
infra/          # Docker Compose, OTEL collector, Prometheus, Grafana
infra/grafana/  # Grafana dashboards + provisioning
scripts/        # Load test scripts
/tests/         # Pytest suites
```

## Troubleshooting

- **Ports already in use**: stop local services or change ports in `infra/docker-compose.yml`.
- **Missing spans in Jaeger**: ensure `otel-collector` is running and run `make demo` traffic.
- **Prometheus shows no metrics**: verify `app:8000/metrics` is reachable from Prometheus.
- **Grafana dashboard empty**: ensure Prometheus datasource is healthy and traffic is being generated.

## API Reference

### POST /items
Creates an item and enqueues enrichment.

### GET /items/{id}
Reads an item. Uses Redis cache (cache-aside pattern).

### GET /health
Health check.

### GET /metrics
Prometheus/OpenMetrics format metrics.
