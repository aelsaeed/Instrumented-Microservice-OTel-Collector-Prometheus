# Roadmap

## Milestone 1: Stabilize demo
- Ensure `make demo` is deterministic and completes in under one minute.
- Keep local dry-mode demo independent from Docker dependencies.
- Add smoke checks that verify app health and core wiring.

## Milestone 2: Observability + metrics
- Expand application metrics (error budgets, saturation indicators).
- Add trace exemplars and a standard dashboard review checklist.
- Add alert rule examples for latency and error-rate regressions.

## Milestone 3: Hardening + docs
- Document production deployment patterns and security controls.
- Add dependency and container vulnerability scanning in CI.
- Grow troubleshooting/runbooks and onboarding documentation.
