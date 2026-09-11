# Stock Price Prediction with LSTM

## Status

Historical market-data ingestion, quantitative analysis, feature engineering, supervised datasets, baseline models, LSTM training, walk-forward validation, backtesting, a FastAPI research backend, PostgreSQL persistence, a Next.js research dashboard, Docker Compose orchestration, readiness checks, security safeguards, and CI are implemented.

## Project

This project is intended to become a full-stack quantitative finance and machine learning research platform. It will eventually support historical market-data workflows, quantitative feature engineering, time-series model evaluation, strategy research, risk analysis, and user-facing results.

## Goals

- Acquire, validate, and clean historical financial market data.
- Explore data and engineer quantitative features without data leakage.
- Compare baseline and LSTM time-series models using chronological validation.
- Generate research signals and evaluate strategies with realistic assumptions.
- Expose research workflows through a backend API and frontend application.

## Planned Architecture

Market data flows through ingestion, validation and preprocessing, feature engineering, model training and evaluation, backtesting, API, persistence, and the Next.js research dashboard.

## Planned Technology Stack

- Python for data, quantitative research, and machine learning workflows.
- pandas and NumPy for data manipulation and numerical work.
- scikit-learn and PyTorch for baseline and LSTM modeling.
- FastAPI for the research API boundary; SQLAlchemy, Alembic, and PostgreSQL for persistence.
- Next.js and TypeScript for the research dashboard.
- Jupyter for exploration and research notebooks.

## Directory Structure

```text
backend/       FastAPI research API and persistence layer
alembic/       Database migrations
frontend/      Next.js quantitative research dashboard
data/          Raw and processed data locations
docs/          Project documentation
ml/            Reusable quantitative and machine-learning code
notebooks/     Exploratory notebooks
tests/         Automated tests
```

## Local Python Environment

On Windows PowerShell, create the environment if `.venv` does not already exist:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Quick Start (Full Stack)

```powershell
copy .env.example .env
docker compose up --build
```

- Dashboard: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health: `GET /api/v1/health`
- Ready: `GET /api/v1/ready`

Manual alternative:

```powershell
docker compose up -d postgres
$env:DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/quant_research"
alembic upgrade head
uvicorn backend.app.main:app --reload
# separate terminal
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Docs: [docs/development.md](docs/development.md) · [docs/deployment.md](docs/deployment.md) · [docs/frontend.md](docs/frontend.md) · [docs/backend.md](docs/backend.md) · [docs/database.md](docs/database.md)

## Frontend Dashboard

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

- App: `http://localhost:3000`
- Frontend notes: [docs/frontend.md](docs/frontend.md)
- Requires FastAPI at `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`)

## Backend API

Start the research API from the repository root:

```powershell
uvicorn backend.app.main:app --reload
```

- Health: `GET /api/v1/health`
- Ready: `GET /api/v1/ready`
- OpenAPI docs: `http://127.0.0.1:8000/docs`
- Backend notes: [docs/backend.md](docs/backend.md)
- Database notes: [docs/database.md](docs/database.md)
- Deployment notes: [docs/deployment.md](docs/deployment.md)

Optional local PostgreSQL:

```powershell
docker compose up -d postgres
$env:DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/quant_research"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

The local environment and generated data are excluded from Git. Do not create or commit real credentials; use `.env.example` as the safe template for local configuration.

## Development Philosophy

The project will be built incrementally in small, testable steps. Reusable production logic should be separated from exploratory notebooks, financial time series must preserve chronological order, and model and trading performance must be evaluated out of sample with realistic assumptions. Generated datasets, model artifacts, and secrets should remain local.

## Disclaimer

This project is for research and educational purposes only. It is not financial advice, and no future implementation should be interpreted as a promise of accuracy or profitability.
