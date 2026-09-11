# System Architecture

**Status: core platform implemented** (phases 1–15), including the final
engineering pass for research-integrity and documentation alignment.

The deployable shape is an intentional **modular monolith**: Next.js and
FastAPI front a shared Python quantitative engine and PostgreSQL persistence.
Research training runs offline; the dashboard reads persisted artifacts.

## High-Level Request and Research Flow

```mermaid
flowchart LR
    User[User]
    FE[Next.js]
    API[FastAPI]
    Svc[Services]
    Repo[Repositories]
    DB[(PostgreSQL)]
    Eng[Quant / ML Engine]

    User --> FE --> API --> Svc
    Svc --> Repo --> DB
    Svc --> Eng
```

```mermaid
flowchart TD
    Eng[ML / Quant Engine]
    Feat[Features]
    Models[Models]
    Val[Validation / walk-forward]
    OOS[OOS predictions]
    BT[Backtesting]
    Risk[Risk analytics]
    Repo[Repositories]
    DB[(PostgreSQL)]

    Eng --> Feat --> Models --> Val --> OOS --> BT --> Risk
    OOS --> Repo
    BT --> Repo
    Repo --> DB
```

## Research Pipeline Flow

```mermaid
flowchart TD
    A[Market Data] --> B[Validation]
    B --> C[Feature Engineering]
    C --> D[Targets]
    D --> E[Temporal ML Pipeline]
    E --> F[Baseline ML]
    E --> G[PyTorch LSTM]
    F --> H[Walk-Forward OOS Predictions]
    G --> H
    H --> I[Model Evaluation]
    I --> J[Backtesting]
    J --> K[Risk Analytics]
    K --> L[PostgreSQL]
    L --> M[FastAPI]
    M --> N[Next.js Dashboard]
    I --> O[Final Research Layer]
    O --> P[Robustness Regimes Ablation Stats Sensitivity Report]
```

```text
Market Data
    ↓
Validation
    ↓
Feature Engineering
    ↓
Targets
    ↓
Temporal ML Pipeline
    ↓
┌───────────────┬────────────────┐
│ Baseline ML   │ PyTorch LSTM   │
└───────┬───────┴───────┬────────┘
        ↓               ↓
      Walk-Forward OOS Predictions
                 ↓
          Model Evaluation
                 ↓
             Backtesting
                 ↓
           Risk Analytics
                 ↓
            PostgreSQL
                 ↓
              FastAPI
                 ↓
          Next.js Dashboard
```

## Layer Responsibilities

### Data Layer

Acquire historical market data, preserve source metadata, validate schemas and
timestamps, normalize OHLCV, and persist local research extracts (`ml/data/`).

### Quantitative Research Layer

Returns, volatility, drawdown, correlations, leakage-aware feature engineering,
supervised targets, and final evaluation utilities (`ml/analysis/`,
`ml/features/`, `ml/targets/`, `ml/research/`).

### Machine Learning Layer

Baseline models, LSTM sequence models (including context-aware lookback within
folds), train-only preprocessing, chronological splits, walk-forward validation,
and OOS prediction collection (`ml/models/`, `ml/neural/`, `ml/training/`,
`ml/validation/`).

### Backtesting Layer

Signals, execution alignment (`forecast_horizon=1`), costs/slippage, equity
curves, risk metrics, benchmarks, fold-aware OOS stitching, and cost/threshold
sensitivity (`ml/backtesting/`, `ml/research/sensitivity.py`).

### Backend/API Layer

FastAPI `/api/v1` health/ready, market data (limit/offset), analysis, features
(limit/offset), models, predictions from DB, experiments (+ related),
walk-forward, and backtests with SQLAlchemy + Alembic + PostgreSQL.

### Frontend Layer

Next.js TypeScript research dashboard for market, features, experiments
(related walk-forward/backtest links), walk-forward analytics, and backtest
risk views.

## Design Boundaries

- Data acquisition stays separate from research transforms.
- Training stays separate from inference/evaluation.
- Evaluation preserves temporal order; no future leakage.
- API/frontend consume documented outputs; research formulas live in `ml/`.
- Negative LSTM results are valid and must not be hidden.
- Combined continuous backtests reject overlapping OOS fold dates and do not
  annualize across discontinuous gaps.
- Deeper design notes: [system-design.md](system-design.md).
