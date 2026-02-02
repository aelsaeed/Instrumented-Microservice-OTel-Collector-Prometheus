.PHONY: run test lint up loadtest

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .
	mypy app worker tests

up:
	docker compose -f infra/docker-compose.yml up -d --build

loadtest:
	k6 run scripts/loadtest.js
