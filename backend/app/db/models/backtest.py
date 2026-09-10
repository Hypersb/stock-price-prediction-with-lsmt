"""Backtest persistence ORM models."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from backend.app.db.base import Base
from backend.app.db.types import created_at_column

if TYPE_CHECKING:
    from backend.app.db.models.experiment import Experiment
    from backend.app.db.models.walk_forward import WalkForwardRun


class BacktestRun(Base):
    """Persisted historical research backtest configuration and summary."""

    __tablename__ = "backtest_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = created_at_column()
    experiment_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("experiments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    walk_forward_run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("walk_forward_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    task: Mapped[str] = mapped_column(String(32), nullable=False)
    strategy_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    signal_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    transaction_cost_bps: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    slippage_bps: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    initial_capital: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    observation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sample_kind: Mapped[str] = mapped_column(
        String(32), nullable=False, default="out_of_sample"
    )

    experiment: Mapped[Experiment | None] = relationship("Experiment")
    walk_forward_run: Mapped[WalkForwardRun | None] = relationship("WalkForwardRun")
    metrics: Mapped[list[BacktestMetric]] = relationship(
        "BacktestMetric",
        back_populates="backtest",
        cascade="all, delete-orphan",
    )
    equity_points: Mapped[list[BacktestEquityPoint]] = relationship(
        "BacktestEquityPoint",
        back_populates="backtest",
        cascade="all, delete-orphan",
        order_by="BacktestEquityPoint.date",
    )


class BacktestMetric(Base):
    """Flexible metric storage for a backtest run."""

    __tablename__ = "backtest_metrics"
    __table_args__ = (
        UniqueConstraint(
            "backtest_id",
            "metric_name",
            name="uq_backtest_metrics_backtest_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = created_at_column()
    backtest_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("backtest_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    backtest: Mapped[BacktestRun] = relationship("BacktestRun", back_populates="metrics")


class BacktestEquityPoint(Base):
    """Date-aligned equity and return observations for a backtest."""

    __tablename__ = "backtest_equity_points"
    __table_args__ = (
        UniqueConstraint(
            "backtest_id",
            "date",
            name="uq_backtest_equity_points_backtest_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    backtest_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("backtest_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    position: Mapped[float | None] = mapped_column(Float, nullable=True)
    gross_return: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_return: Mapped[float | None] = mapped_column(Float, nullable=True)
    equity: Mapped[float | None] = mapped_column(Float, nullable=True)

    backtest: Mapped[BacktestRun] = relationship(
        "BacktestRun", back_populates="equity_points"
    )
