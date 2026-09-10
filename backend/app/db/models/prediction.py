"""Out-of-sample prediction persistence models."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from backend.app.db.base import Base
from backend.app.db.types import created_at_column

if TYPE_CHECKING:
    from backend.app.db.models.experiment import Experiment
    from backend.app.db.models.walk_forward import WalkForwardRun


class OutOfSamplePrediction(Base):
    """One chronologically out-of-sample prediction observation."""

    __tablename__ = "out_of_sample_predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = created_at_column()
    walk_forward_run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("walk_forward_runs.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    experiment_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("experiments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    fold: Mapped[int] = mapped_column(Integer, nullable=False)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    task: Mapped[str] = mapped_column(String(32), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    prediction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    realization_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_target: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_class: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sample_kind: Mapped[str] = mapped_column(
        String(32), nullable=False, default="out_of_sample"
    )

    walk_forward_run: Mapped[WalkForwardRun | None] = relationship("WalkForwardRun")
    experiment: Mapped[Experiment | None] = relationship("Experiment")
