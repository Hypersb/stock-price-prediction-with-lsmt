# Stock Price Prediction with LSTM

## Purpose

This project is a full-stack **quantitative ML research platform**. It is **not**
a claim that an LSTM can magically predict the stock market, and it makes **no**
promise of profitable trading.

A scientifically valid conclusion includes:

> The evidence does not demonstrate that the LSTM consistently outperforms simpler models.

## Recruiter-Useful Summary

Honest capabilities of the shipped platform (not trading performance claims):

- Leakage-safe chronological time-series ML (features, targets, splits, purging)
- Baseline models compared against a PyTorch LSTM under the same rules
- Walk-forward validation with true out-of-sample prediction collection
- Transaction-cost-aware historical strategy backtesting and risk analytics
- FastAPI + PostgreSQL persistence, Next.js dashboard, Docker Compose, and CI

The final engineering pass focused on **research integrity** (direction-label
semantics, LSTM context-aware sequences, fold-aware OOS stitching, horizon=1
strategy backtests, prediction GET-from-DB, documentation aligned to the real
system)—not on inventing empirical wins.

Architecture detail: [docs/system-design.md](docs/system-design.md) ·
[docs/architecture.md](docs/architecture.md)

## Status

**All 15 core phases are complete**, including final multi-asset robustness,
regime analysis, explainability, ablation, complexity comparison, statistical
comparison, backtest sensitivity, the final research pipeline, and research
reporting. Empirical report sections remain placeholders until a legitimate
experiment is executed and rendered.

## Architecture

```mermaid
flowchart LR
    User[User] --> FE[Next.js]
    FE --> API[FastAPI]
    API --> Svc[Services]
    Svc --> Repo[Repositories]
    Repo --> DB[(PostgreSQL)]
    Svc --> Eng[Quant / ML Engine]
    Eng --> Repo
```

Conceptual research flow:

```text
Market Data → Validation → Features → Targets → Temporal ML
  → Baseline + LSTM → Walk-Forward OOS → Evaluation
  → Backtesting / Risk → PostgreSQL → FastAPI → Next.js
```

## Research Methodology

See [docs/research-methodology.md](docs/research-methodology.md) and
[docs/final-research-report.md](docs/final-research-report.md).

Highlights:

- Leakage-safe features and separated targets
- Chronological splits and walk-forward validation with purging
- Multi-asset robustness without hiding weak assets
- Causal rule-based regime labels
- Tree/linear explainability and LSTM permutation sensitivity (non-causal)
- Feature-group ablations on aligned splits
- Complexity versus performance diagnostics
- Block-bootstrap paired model comparison
- Cost/threshold sensitivity (diagnostic; no holdout threshold cherry-picking)
- Final orchestration via `ml/research/pipeline.py`

## Technology Stack

- **Python**: pandas, NumPy, scikit-learn, PyTorch, Jupyter
- **API**: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Frontend**: Next.js, TypeScript, Recharts
- **Ops**: Docker Compose, GitHub Actions CI

## Directory Structure

```text
backend/       FastAPI research API and persistence layer
alembic/       Database migrations
frontend/      Next.js quantitative research dashboard
data/          Raw and processed data locations
docs/          Project documentation
ml/            Reusable quantitative and machine-learning code
ml/research/   Final evaluation: robustness, regimes, ablation, report
notebooks/     Exploratory notebooks (01–09)
tests/         Automated tests
```

## Setup

Prefer Python 3.12 for PyTorch compatibility on macOS Intel.

```bash
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Frontend (Node 20+ recommended):

```bash
cd frontend
npm install
cp .env.example .env.local
```

Copy root env template:

```bash
cp .env.example .env
```

## Quick Start (Full Stack)

```bash
docker compose up --build
```

- Dashboard: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health: `GET /api/v1/health`
- Ready: `GET /api/v1/ready`

Manual alternative:

```bash
docker compose up -d postgres
export DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/quant_research"
alembic upgrade head
uvicorn backend.app.main:app --reload
# separate terminal
cd frontend && npm run dev
```

## Market-Data Ingestion

Provider abstraction with Yahoo Finance historical OHLCV, request validation,
normalization, and local CSV persistence (`ml/data/`).

## Feature Engineering

Lagged returns, momentum, SMA/EMA, volatility, volume, RSI, MACD, ATR with
leakage validation (`ml/features/`).

## Baseline Models

Naive, linear/logistic, random forest, gradient boosting (`ml/models/`).

## LSTM

PyTorch sequence datasets, LSTM regression/classification, training with
validation-only early stopping and checkpointing (`ml/neural/`, `ml/training/`).
Sequences may use prior within-fold features as lookback context only.

## Walk-Forward Validation

Expanding/rolling folds, purging, gaps, fold preprocessing, OOS prediction
collection, stability aggregates (`ml/validation/`).

## Backtesting

Signals, forward execution alignment (`forecast_horizon=1`), transaction
costs/slippage, equity curves, Sharpe/Sortino/drawdown/turnover, fold-aware OOS
stitching, benchmark comparison (`ml/backtesting/`).

## FastAPI / PostgreSQL / Next.js

Versioned research APIs, SQLAlchemy models, Alembic migrations, and a Next.js
dashboard for market, features, experiments, walk-forward, and backtests.
Prediction GET endpoints read persisted OOS rows and never train.

## Docker and CI

- `docker compose` for Postgres, API, and frontend
- `.github/workflows/ci.yml`: ruff, pytest, frontend lint/typecheck/test/build,
  Postgres migration checks

## Testing

```bash
# Python
ruff check backend tests ml
pytest -q

# Frontend
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
```

## Final Evaluation

```python
from ml.research.config import tiny_fixture_config
from ml.research.pipeline import run_final_research_evaluation
from ml.research.report import render_final_research_report

# Production research: load provider OHLCV for config.symbols
# result = run_final_research_evaluation(market_data, config)
# print(render_final_research_report(result).markdown)
print(render_final_research_report(None).markdown)
```

## Limitations

- Research/education only — not financial advice
- No live trading, brokerage APIs, or profitability guarantees
- Regime labels and feature sensitivities are diagnostics, not causal proof
- Cost and threshold assumptions are configurable research scenarios
- Provider data quality limits apply

## Future Extensions

Labeled **future work only** (not implemented):

- Licensed real-time market feeds
- News/NLP sentiment
- Transformer sequence models
- Portfolio optimization / multi-asset allocation
- Paper trading
- Model monitoring

## Docs

- [system design](docs/system-design.md)
- [architecture](docs/architecture.md)
- [development](docs/development.md)
- [project status](docs/project-status.md)
- [research methodology](docs/research-methodology.md)
- [final research report](docs/final-research-report.md)
- [backend](docs/backend.md) · [frontend](docs/frontend.md) · [database](docs/database.md) · [deployment](docs/deployment.md)

## Disclaimer

This project is for research and educational purposes only. It is not financial
advice, and no implementation should be interpreted as a promise of accuracy or
profitability.
