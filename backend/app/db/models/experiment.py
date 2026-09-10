"""Experiment ORM model for machine-learning research runs."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from backend.app.db.base import Base
from backend.app.db.types import created_at_column, updated_at_column

if TYPE_CHECKING:
    from backend.app.db.models.metric import ExperimentMetric


class Experiment(Base):
    """Persisted research experiment metadata without model weight blobs."""

    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    task: Mapped[str] = mapped_column(String(32), nullable=False)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_name: Mapped[str] = mapped_column(String(64), nullable=False)
    forecast_horizon: Mapped[int] = mapped_column(Integer, nullable=False)
    lookback: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feature_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    feature_names: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    model_configuration: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    training_configuration: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    train_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    train_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    validation_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    validation_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    test_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    test_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    best_epoch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    best_validation_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    checkpoint_reference: Mapped[str | None] = mapped_column(Text, nullable=True)

    metrics: Mapped[list[ExperimentMetric]] = relationship(
        "ExperimentMetric",
        back_populates="experiment",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"Experiment(id={self.id!s}, symbol={self.symbol!r}, "
            f"model_name={self.model_name!r}, status={self.status!r})"
        )
