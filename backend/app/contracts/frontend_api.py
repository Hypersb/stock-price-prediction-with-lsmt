"""Frontend-consumed API contract catalog.

This module is the lightweight source of truth for routes and response
property names the Next.js dashboard expects. Contract tests compare it to
the live OpenAPI schema to detect drift without a code-generation framework.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrontendEndpointContract:
    """One dashboard-consumed HTTP endpoint."""

    method: str
    path: str
    response_schema: str
    required_properties: tuple[str, ...]
    query_parameters: tuple[str, ...] = ()


# Paths use FastAPI/OpenAPI template syntax.
FRONTEND_API_CONTRACTS: tuple[FrontendEndpointContract, ...] = (
    FrontendEndpointContract(
        method="get",
        path="/api/v1/health",
        response_schema="HealthResponse",
        required_properties=("status", "service", "version", "environment"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/ready",
        response_schema="ReadinessResponse",
        required_properties=("status", "service", "checks"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/market-data/{symbol}",
        response_schema="MarketDataResponse",
        required_properties=(
            "symbol",
            "start_date",
            "end_date",
            "total",
            "count",
            "limit",
            "offset",
            "returned",
            "data",
        ),
        query_parameters=("start_date", "end_date", "limit", "offset"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/analysis/{symbol}/summary",
        response_schema="AnalysisSummaryResponse",
        required_properties=(
            "symbol",
            "start_date",
            "end_date",
            "observation_count",
            "return_count",
            "mean_return",
            "median_return",
            "volatility",
            "cumulative_return",
            "maximum_drawdown",
        ),
        query_parameters=("start_date", "end_date"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/features/{symbol}",
        response_schema="FeatureResponse",
        required_properties=(
            "symbol",
            "start_date",
            "end_date",
            "feature_names",
            "feature_count",
            "observation_count",
            "returned_rows",
            "limit",
            "offset",
            "features",
        ),
        query_parameters=("start_date", "end_date", "limit", "offset"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/models",
        response_schema="ModelCatalogResponse",
        required_properties=("models", "count"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/experiments",
        response_schema="ExperimentListResponse",
        required_properties=("items", "total", "limit", "offset"),
        query_parameters=("limit", "offset", "symbol"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/experiments/{experiment_id}",
        response_schema="ExperimentDetail",
        required_properties=(
            "id",
            "created_at",
            "symbol",
            "task",
            "model_name",
            "target_name",
            "forecast_horizon",
            "status",
            "feature_count",
            "updated_at",
        ),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/experiments/{experiment_id}/metrics",
        response_schema="ExperimentMetricsResponse",
        required_properties=("experiment_id", "metrics"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/experiments/{experiment_id}/related",
        response_schema="ExperimentRelatedResponse",
        required_properties=("experiment_id", "walk_forward_runs", "backtests"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/walk-forward/{run_id}",
        response_schema="WalkForwardRunResponse",
        required_properties=(
            "id",
            "created_at",
            "symbol",
            "model_name",
            "task",
            "window_type",
            "forecast_horizon",
            "gap",
            "folds",
        ),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/backtests",
        response_schema="PersistedBacktestListResponse",
        required_properties=("items", "total", "limit", "offset"),
        query_parameters=("limit", "offset", "symbol", "experiment_id"),
    ),
    FrontendEndpointContract(
        method="get",
        path="/api/v1/backtests/{backtest_id}",
        response_schema="PersistedBacktestDetail",
        required_properties=(
            "id",
            "created_at",
            "symbol",
            "model_name",
            "task",
            "strategy_mode",
            "sample_kind",
            "transaction_cost_bps",
            "slippage_bps",
            "initial_capital",
            "metrics",
            "equity_curve",
        ),
    ),
)


def frontend_contract_paths() -> set[str]:
    """Return OpenAPI path keys consumed by the dashboard."""
    return {contract.path for contract in FRONTEND_API_CONTRACTS}
