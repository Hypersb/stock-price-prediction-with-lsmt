# Thin wrappers around canonical developer commands.
# See docs/startup/DEVELOPER_WORKFLOW.md

.PHONY: install test lint frontend-test health migrate fetch-help print-config

install:
	python -m pip install -r requirements.txt -r requirements-dev.txt
	cd frontend && npm ci

test:
	APP_ENV=test QUANT_LOAD_DOTENV=false PYTHONPATH=. pytest -q

lint:
	ruff check backend tests ml scripts

frontend-test:
	cd frontend && npm test

health:
	PYTHONPATH=. python -m scripts.check_repo_health

print-config:
	PYTHONPATH=. python -m scripts.print_config

migrate:
	alembic upgrade head

fetch-help:
	PYTHONPATH=. python -m scripts.fetch_market_data --help
