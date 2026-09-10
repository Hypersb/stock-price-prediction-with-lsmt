"""Walk-forward evaluation ORM models."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from backend.app.db.base import Base
from backend.app.db.types import created_at_column

if TYPE_CHECKING:
    from backend.app.db.models.experiment import Experiment


class WalkForwardRun(Base):
    """Metadata for one walk-forward evaluation campaign."""

    __tablename__ = "walk_forward_runs"

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
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    task: Mapped[str] = mapped_column(String(32), nullable=False)
    window_type: Mapped[str] = mapped_column(String(32), nullable=False)
    initial_train_size: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_size: Mapped[int] = mapped_column(Integer, nullable=False)
    test_size: Mapped[int] = mapped_column(Integer, nullable=False)
    step_size: Mapped[int] = mapped_column(Integer, nullable=False)
    gap: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    forecast_horizon: Mapped[int] = mapped_column(Integer, nullable=False)

    experiment: Mapped[Experiment | None] = relationship("Experiment")
    folds: Mapped[list[WalkForwardFold]] = relationship(
        "WalkForwardFold",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="WalkForwardFold.fold_number",
    )


class WalkForwardFold(Base):
    """One fold within a walk-forward run."""

    __tablename__ = "walk_forward_folds"
    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "fold_number",
            name="uq_walk_forward_folds_run_fold_number",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = created_at_column()
    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("walk_forward_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fold_number: Mapped[int] = mapped_column(Integer, nullable=False)
    train_start: Mapped[date] = mapped_column(Date, nullable=False)
    train_end: Mapped[date] = mapped_column(Date, nullable=False)
    validation_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    validation_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    test_start: Mapped[date] = mapped_column(Date, nullable=False)
    test_end: Mapped[date] = mapped_column(Date, nullable=False)
    train_count: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    test_count: Mapped[int] = mapped_column(Integer, nullable=False)
    best_epoch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fold_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    run: Mapped[WalkForwardRun] = relationship("WalkForwardRun", back_populates="folds")
