# Planned System Architecture

**Status: planned documentation only.** The components described here are not implemented yet.

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

Planned responsibility: acquire historical market data, preserve source metadata, validate schemas and timestamps, and produce clean datasets. Raw and processed data locations exist, but ingestion and validation are not implemented.

### Quantitative Research Layer

Planned responsibility: calculate returns and volatility, explore market behavior, and implement quantitative feature engineering. No research features or indicators exist yet.

### Machine Learning Layer

Planned responsibility: provide baseline models and, later, LSTM forecasting workflows with chronological and walk-forward validation. No models or predictions are implemented.

### Backtesting Layer

Planned responsibility: turn model outputs into testable strategy rules and calculate performance and risk metrics with transaction costs. No backtesting engine exists.

### Backend/API Layer

Planned responsibility: expose data, research, model, and backtest workflows through FastAPI and coordinate persistence through PostgreSQL. No API, database, or authentication components exist.

### Frontend Layer

Planned responsibility: provide a Next.js and TypeScript interface for market data, model comparisons, signals, and evaluation results. No frontend components exist.

## Design Boundaries

Data acquisition and cleaning should remain separate from research transformations. Model training should be separate from inference, and evaluation should preserve the temporal order of financial observations. The API and frontend should consume documented outputs rather than embedding research logic.
