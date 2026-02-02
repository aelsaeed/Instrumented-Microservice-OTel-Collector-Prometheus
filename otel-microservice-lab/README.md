# Otel Microservice Lab

A production-style FastAPI microservice with PostgreSQL persistence, Redis caching, a Celery worker, and a full local OpenTelemetry stack (Collector, Jaeger, Prometheus, Grafana).

## Quickstart

```bash
cd otel-microservice-lab
make up
```

Open the service:

- API: http://localhost:8000
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics
- Jaeger: http://localhost:16686
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (anonymous access enabled)

Run a load test (requires k6 installed):

```bash
make loadtest
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
3. Grafana reads Prometheus (metrics) and Jaeger (traces) to render dashboards.

## Dashboards

Grafana dashboards are pre-provisioned:

- Service latency (p95)
- Error rate (5xx)
- DB query time
- Cache hit rate
- Worker queue depth

Example screenshot paths (store your captures here):

```
./docs/screenshots/grafana-latency.png
./docs/screenshots/grafana-cache-hit-rate.png
./docs/screenshots/jaeger-trace.png
```

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
- **Missing spans in Jaeger**: ensure `otel-collector` is running and the app has `OTEL_LAB_OTEL_EXPORTER_OTLP_ENDPOINT` set.
- **Prometheus shows no metrics**: verify `app:8000/metrics` is reachable and the Prometheus config targets `app:8000`.
- **Grafana dashboard empty**: ensure Prometheus datasource is healthy and the load test is generating traffic.

## API Reference

### POST /items
Creates an item and enqueues enrichment.

### GET /items/{id}
Reads an item. Uses Redis cache (cache-aside pattern).

### GET /health
Health check.

### GET /metrics
Prometheus/OpenMetrics format metrics.
