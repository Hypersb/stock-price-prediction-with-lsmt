"""Pydantic schemas for persisted research resources."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ExperimentSummary(BaseModel):
    id: UUID
    created_at: datetime
    symbol: str
    task: str
    model_name: str
    target_name: str
    forecast_horizon: int
    status: str
    feature_count: int
    best_epoch: int | None = None
    best_validation_loss: float | None = None
    checkpoint_reference: str | None = None


class ExperimentDetail(ExperimentSummary):
    lookback: int | None = None
    seed: int | None = None
    feature_names: list[Any] | None = None
    model_configuration: dict[str, Any] | None = None
    training_configuration: dict[str, Any] | None = None
    train_start: date | None = None
    train_end: date | None = None
    validation_start: date | None = None
    validation_end: date | None = None
    test_start: date | None = None
    test_end: date | None = None
    updated_at: datetime


class ExperimentListResponse(BaseModel):
    items: list[ExperimentSummary]
    total: int
    limit: int
    offset: int


class ExperimentMetricResponse(BaseModel):
    id: UUID
    split: str
    metric_name: str
    metric_value: float | None = None


class ExperimentMetricsResponse(BaseModel):
    experiment_id: UUID
    metrics: list[ExperimentMetricResponse]


class WalkForwardFoldResponse(BaseModel):
    fold_number: int
    train_start: date
    train_end: date
    validation_start: date | None = None
    validation_end: date | None = None
    test_start: date
    test_end: date
    train_count: int
    validation_count: int
    test_count: int
    best_epoch: int | None = None
    fold_metrics: dict[str, Any] | None = None


class WalkForwardRunResponse(BaseModel):
    id: UUID
    created_at: datetime
    experiment_id: UUID | None = None
    symbol: str
    model_name: str
    task: str
    window_type: str
    initial_train_size: int
    validation_size: int
    test_size: int
    step_size: int
    gap: int
    forecast_horizon: int
    folds: list[WalkForwardFoldResponse]


class PersistedBacktestSummary(BaseModel):
    id: UUID
    created_at: datetime
    symbol: str
    model_name: str
    task: str
    strategy_mode: str
    sample_kind: str
    observation_count: int
    start_date: date | None = None
    end_date: date | None = None


class ExperimentRelatedResponse(BaseModel):
    """Persisted research artifacts linked to one experiment."""

    experiment_id: UUID
    walk_forward_runs: list[WalkForwardRunResponse]
    backtests: list[PersistedBacktestSummary]


class PersistedBacktestListResponse(BaseModel):
    items: list[PersistedBacktestSummary]
    total: int
    limit: int
    offset: int


class PersistedBacktestMetric(BaseModel):
    metric_name: str
    metric_value: float | None = None


class PersistedEquityPoint(BaseModel):
    date: date
    position: float | None = None
    gross_return: float | None = None
    cost: float | None = None
    net_return: float | None = None
    equity: float | None = None


class PersistedBacktestDetail(PersistedBacktestSummary):
    experiment_id: UUID | None = None
    walk_forward_run_id: UUID | None = None
    signal_threshold: float
    transaction_cost_bps: float
    slippage_bps: float
    initial_capital: float
    metrics: list[PersistedBacktestMetric]
    equity_curve: list[PersistedEquityPoint] = Field(default_factory=list)
