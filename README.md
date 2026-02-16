# Instrumented-Microservice-OTel-Collector-Prometheus

![CI](https://github.com/aelsaeed/Instrumented-Microservice-OTel-Collector-Prometheus/actions/workflows/ci.yml/badge.svg)

This repository contains the **otel-microservice-lab** project: a production-style FastAPI microservice with PostgreSQL persistence, Redis cache-aside, a Celery worker, and a local OpenTelemetry stack (Collector, Jaeger, Prometheus, Grafana).

## Quickstart

```bash
make setup
make up
make demo
```

## One-command run

- `make up` boots the full local stack (app + worker + collector + prometheus + grafana + jaeger).
- `make demo` sends a small synthetic load and prints where to inspect traces and dashboards.

```bash
make up
make demo
```

## Demo output

`make demo` exercises these span-generating endpoints:

- `POST /items`
- `GET /items/{id}`
- `GET /health`

And prints:

- Jaeger traces: http://localhost:16686
- Grafana dashboard: http://localhost:3000/d/otel-lab/otel-microservice-lab
- Prometheus: http://localhost:9090

## Telemetry flow

```text
Client traffic
   |
   v
FastAPI app + Celery worker
   |  (OTLP traces/metrics/logs)
   v
OpenTelemetry Collector
   |-----------------------> Jaeger (traces)
   |-----------------------> Prometheus (metrics)
                               |
                               v
                            Grafana
```

See the service-level architecture details in: [otel-microservice-lab/README.md#architecture](otel-microservice-lab/README.md#architecture).

## Dashboards

Grafana is pre-provisioned with an "Otel Microservice Lab" dashboard including:

- Request latency p50/p95
- Error rate (5xx)
- Cache hit rate
- Worker queue depth

Dashboard source: `otel-microservice-lab/infra/grafana/dashboards/otel_lab_dashboard.json`.

## Development

```bash
pip install -r otel-microservice-lab/requirements-dev.txt
pre-commit install
```

Common checks:

```bash
make lint
make typecheck
make test
```

## Testing / CI

GitHub Actions runs on push/pull request and validates:

- `ruff check`
- `mypy`
- `pytest`
- `docker compose config`

Workflow file: [.github/workflows/ci.yml](.github/workflows/ci.yml)

## Troubleshooting

- **`make up` fails**: ensure Docker Engine/Desktop is running and `docker compose` is installed.
- **No traces in Jaeger**: generate traffic with `make demo`, then verify `otel-collector` container is healthy.
- **Dashboard empty**: verify Prometheus target `app:8000` is `UP`, then rerun `make demo`.
- **Port conflicts**: free ports `3000`, `5432`, `6379`, `8000`, `9090`, `16686`, or edit compose mappings.

## Repository contents

- `otel-microservice-lab/` — app, worker, tests, infra config.
- `.github/` — CI workflow, issue templates, and PR template.
- `scripts/` — repository-level smoke/demo automation.
- `ROADMAP.md` — milestone planning.
- `CONTRIBUTING.md` — contribution standards and workflow.
