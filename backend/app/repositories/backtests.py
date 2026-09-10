"""Backtest persistence repository."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.db.metrics import normalize_metric_value
from backend.app.db.models import BacktestEquityPoint, BacktestMetric, BacktestRun


@dataclass(frozen=True)
class BacktestCreate:
    symbol: str
    model_name: str
    task: str
    strategy_mode: str
    signal_threshold: float = 0.0
    transaction_cost_bps: float = 0.0
    slippage_bps: float = 0.0
    initial_capital: float = 1.0
    start_date: date | None = None
    end_date: date | None = None
    observation_count: int = 0
    experiment_id: uuid.UUID | None = None
    walk_forward_run_id: uuid.UUID | None = None
    sample_kind: str = "out_of_sample"


@dataclass(frozen=True)
class BacktestMetricCreate:
    metric_name: str
    metric_value: float | None


@dataclass(frozen=True)
class BacktestEquityCreate:
    date: date
    position: float | None = None
    gross_return: float | None = None
    cost: float | None = None
    net_return: float | None = None
    equity: float | None = None


class BacktestRepository:
    """Persist research backtests, metrics, and equity curves."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        payload: BacktestCreate,
        metrics: list[BacktestMetricCreate] | None = None,
        equity_points: list[BacktestEquityCreate] | None = None,
    ) -> BacktestRun:
        if payload.sample_kind != "out_of_sample":
            raise ValueError("only out_of_sample backtests may be persisted")
        run = BacktestRun(
            experiment_id=payload.experiment_id,
            walk_forward_run_id=payload.walk_forward_run_id,
            symbol=payload.symbol.strip().upper(),
            model_name=payload.model_name,
            task=payload.task,
            strategy_mode=payload.strategy_mode,
            signal_threshold=payload.signal_threshold,
            transaction_cost_bps=payload.transaction_cost_bps,
            slippage_bps=payload.slippage_bps,
            initial_capital=payload.initial_capital,
            start_date=payload.start_date,
            end_date=payload.end_date,
            observation_count=payload.observation_count,
            sample_kind="out_of_sample",
        )
        self.session.add(run)
        self.session.flush()
        for metric in metrics or []:
            self.session.add(
                BacktestMetric(
                    backtest_id=run.id,
                    metric_name=metric.metric_name,
                    metric_value=normalize_metric_value(metric.metric_value),
                )
            )
        for point in equity_points or []:
            self.session.add(
                BacktestEquityPoint(
                    backtest_id=run.id,
                    date=point.date,
                    position=normalize_metric_value(point.position),
                    gross_return=normalize_metric_value(point.gross_return),
                    cost=normalize_metric_value(point.cost),
                    net_return=normalize_metric_value(point.net_return),
                    equity=normalize_metric_value(point.equity),
                )
            )
        self.session.flush()
        return run

    def get(self, backtest_id: uuid.UUID) -> BacktestRun | None:
        statement = (
            select(BacktestRun)
            .where(BacktestRun.id == backtest_id)
            .options(
                selectinload(BacktestRun.metrics),
                selectinload(BacktestRun.equity_points),
            )
        )
        return self.session.scalar(statement)

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        symbol: str | None = None,
    ) -> tuple[list[BacktestRun], int]:
        filters = []
        if symbol:
            filters.append(BacktestRun.symbol == symbol.strip().upper())
        total = self.session.scalar(
            select(func.count()).select_from(BacktestRun).where(*filters)
        ) or 0
        statement: Select[tuple[BacktestRun]] = (
            select(BacktestRun)
            .where(*filters)
            .order_by(BacktestRun.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(statement)), int(total)
