# Thin wrappers around canonical developer commands.
# See docs/startup/DEVELOPER_WORKFLOW.md

.PHONY: install test lint frontend-test health migrate fetch-help

install:
	python -m pip install -r requirements.txt -r requirements-dev.txt
	cd frontend && npm ci

test:
	APP_ENV=test PYTHONPATH=. pytest -q

lint:
	ruff check backend tests ml scripts

frontend-test:
	cd frontend && npm test

health:
	PYTHONPATH=. python -m scripts.check_repo_health

migrate:
	alembic upgrade head

fetch-help:
	PYTHONPATH=. python -m scripts.fetch_market_data --help
