# Developer Workflow

Canonical commands for this repository. Prefer these over ad-hoc path hacks.

**Node:** ≥ 20 (CI uses 22). See `frontend/package.json` `engines` and `frontend/.nvmrc`.  
**Python:** 3.12 recommended (PyTorch on macOS Intel).

---

## Install

```bash
# Python
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt

# Frontend
cd frontend
npm ci   # or npm install
cp .env.example .env.local
cd ..

cp .env.example .env
```

Or: `make install` (venv assumed activated for pip).

---

## Backend dev

```bash
docker compose up -d postgres
export DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/quant_research"
export PYTHONPATH=.
alembic upgrade head
uvicorn backend.app.main:app --reload
```

API docs: `http://localhost:8000/docs`

---

## Frontend dev

```bash
cd frontend
npm run dev
```

Dashboard: `http://localhost:3000`

---

## Tests & lint

```bash
export PYTHONPATH=. APP_ENV=test
ruff check backend tests ml scripts
pytest -q

cd frontend && npm test && npm run lint && npm run typecheck
```

Repo structural health:

```bash
PYTHONPATH=. python -m scripts.check_repo_health
```

Or: `make test`, `make lint`, `make health`.

---

## Research pipeline

```python
from ml.research.config import tiny_fixture_config  # tests / smoke
from ml.research.pipeline import run_final_research_evaluation
from ml.research.report import render_final_research_report

# Production research: supply real OHLCV dict keyed by symbol
# result = run_final_research_evaluation(market_data, config)
print(render_final_research_report(None).markdown)  # placeholder-safe
```

Fetch sample history:

```bash
PYTHONPATH=. python -m scripts.fetch_market_data AAPL 2020-01-01 2024-01-01 --save
```

---

## Database migration

```bash
export DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/quant_research"
alembic upgrade head
```

---

## Docker development

```bash
docker compose up --build
```

- UI: `http://localhost:3000`  
- API: `http://localhost:8000`  
- Postgres: local port `5432` with **dev placeholder** credentials only  

Docker API image installs from `requirements-docker.txt` (pinned compatible ranges, **no** torch/jupyter). Strategy: same lower-bound pins as `requirements.txt` for shared packages so Compose builds are predictable without freezing the entire host venv.

---

## Make targets

| Target | Action |
|--------|--------|
| `make install` | pip + frontend npm ci |
| `make test` | pytest |
| `make lint` | ruff |
| `make frontend-test` | vitest |
| `make health` | repo health check |
| `make migrate` | alembic upgrade head |
