# Planned System Architecture

**Status: planned architecture.** The initial market-data ingestion and validation layer is implemented; downstream components remain planned.

## Planned Flow

```text
market data sources
        |
        v
data ingestion
        |
        v
validation and preprocessing
        |
        v
feature engineering
        |
        v
machine learning models
        |
        v
model evaluation
        |
        v
backtesting engine
        |
        v
FastAPI backend
        |
        v
Next.js frontend
```

## Layer Responsibilities

### Data Layer

Planned responsibility: acquire historical market data, preserve source metadata, validate schemas and timestamps, and produce clean datasets. The initial provider abstraction, Yahoo Finance provider, normalization, validation, persistence, and ingestion service are implemented.

### Quantitative Research Layer

Planned responsibility: calculate returns and volatility, explore market behavior, and implement quantitative feature engineering. No research features or indicators exist yet.

### Machine Learning Layer

Planned responsibility: provide baseline models and, later, LSTM forecasting workflows with chronological and walk-forward validation. No models or predictions are implemented.

### Backtesting Layer

Planned responsibility: turn model outputs into testable strategy rules and calculate performance and risk metrics with transaction costs. No backtesting engine exists.

### Backend/API Layer

Implemented responsibility: expose market data, research summaries, features, model metadata, stored-prediction lookups, and out-of-sample backtests through a versioned FastAPI boundary, with SQLAlchemy repositories and Alembic migrations targeting PostgreSQL for experiment/result persistence. Authentication is not implemented yet.

### Frontend Layer

Planned responsibility: provide a Next.js and TypeScript interface for market data, model comparisons, signals, and evaluation results. No frontend components exist.

## Design Boundaries

Data acquisition and cleaning should remain separate from research transformations. Model training should be separate from inference, and evaluation should preserve the temporal order of financial observations. The API and frontend should consume documented outputs rather than embedding research logic.
