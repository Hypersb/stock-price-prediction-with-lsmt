"""Backtest request and response schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

from backend.app.schemas.common import StrategyMode, TaskType


class BacktestPredictionInput(BaseModel):
    """One explicitly out-of-sample prediction observation."""

    date: date
    model: str = Field(min_length=1, max_length=64)
    task: TaskType
    predicted: float | None = None
    probability: float | None = None
    fold: int | None = Field(
        default=None,
        ge=0,
        description="optional walk-forward fold id; required for honest multi-fold stitching",
    )

    @model_validator(mode="after")
    def validate_task_fields(self) -> BacktestPredictionInput:
        if self.task == TaskType.REGRESSION and self.predicted is None:
            raise ValueError("regression predictions require predicted")
        if self.task == TaskType.CLASSIFICATION and self.probability is None:
            raise ValueError("classification predictions require probability")
        if self.probability is not None and not 0 <= self.probability <= 1:
            raise ValueError("probability must be within [0, 1]")
        return self


class MarketReturnInput(BaseModel):
    """Realized market return observation used for execution alignment."""

    date: date
    realized_return: float


class BacktestConfigInput(BaseModel):
    """Client-provided backtest configuration without filesystem controls."""

    strategy_mode: StrategyMode = StrategyMode.LONG_ONLY
    signal_threshold: float = Field(default=0.0, ge=0)
    transaction_cost_bps: float = Field(default=0.0, ge=0)
    slippage_bps: float = Field(default=0.0, ge=0)
    initial_capital: float = Field(default=1.0, gt=0)
    annualization_factor: float = Field(default=252.0, gt=0)


class BacktestRequest(BaseModel):
    """Synchronous research backtest using explicit OOS inputs."""

    sample_kind: str = Field(
        description="must be out_of_sample; in-sample inputs are rejected"
    )
    symbol: str = Field(min_length=1, max_length=32)
    configuration: BacktestConfigInput = Field(default_factory=BacktestConfigInput)
    predictions: list[BacktestPredictionInput] = Field(min_length=1)
    market_returns: list[MarketReturnInput] = Field(min_length=2)

    @field_validator("sample_kind")
    @classmethod
    def require_out_of_sample(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized != "out_of_sample":
            raise ValueError("sample_kind must be 'out_of_sample'")
        return normalized

    @field_validator("symbol")
    @classmethod
    def normalize_symbol_field(cls, value: str) -> str:
        from ml.data.symbols import normalize_symbol

        return normalize_symbol(value)


class EquityPoint(BaseModel):
    """Single equity-curve observation."""

    date: date
    equity: float | None = None
    net_strategy_return: float | None = None


class BacktestResponse(BaseModel):
    """Serializable backtest result for research clients."""

    symbol: str
    model: str
    task: str
    sample_kind: str
    configuration: BacktestConfigInput
    start_date: date | None = None
    end_date: date | None = None
    observations: int
    performance_metrics: dict[str, float | None]
    risk_metrics: dict[str, float | None]
    trading_analytics: dict[str, float | int | None]
    benchmark_metrics: dict[str, dict[str, float | None]]
    equity_curve: list[EquityPoint]
