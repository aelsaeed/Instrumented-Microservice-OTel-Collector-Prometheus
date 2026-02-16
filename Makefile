SHELL := /bin/bash

PROJECT_DIR := otel-microservice-lab
COMPOSE_FILE := $(PROJECT_DIR)/infra/docker-compose.yml
PYTHON ?= python3
PIP ?= pip3

.PHONY: setup lint typecheck test fmt up demo clean

setup:
	$(PIP) install -r $(PROJECT_DIR)/requirements-dev.txt
	pre-commit install

lint:
	ruff check $(PROJECT_DIR)
	bash scripts/smoke_test.sh

typecheck:
	PYTHONPATH=$(PROJECT_DIR) mypy --config-file $(PROJECT_DIR)/pyproject.toml $(PROJECT_DIR)/tests

test:
	PYTHONPATH=$(PROJECT_DIR) pytest $(PROJECT_DIR)/tests

fmt:
	ruff format $(PROJECT_DIR)

up:
	docker compose -f $(COMPOSE_FILE) up -d --build

demo:
	bash scripts/demo.sh

clean:
	find $(PROJECT_DIR) -type d -name "__pycache__" -prune -exec rm -rf {} +
	find $(PROJECT_DIR) -type f -name "*.pyc" -delete
	rm -f test.db otel-microservice-lab/test.db
