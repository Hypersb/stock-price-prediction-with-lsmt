"""Experiment evaluation metric ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from backend.app.db.base import Base
from backend.app.db.types import created_at_column

if TYPE_CHECKING:
    from backend.app.db.models.experiment import Experiment


class ExperimentMetric(Base):
    """Normalized metric values associated with an experiment split."""

    __tablename__ = "experiment_metrics"
    __table_args__ = (
        UniqueConstraint(
            "experiment_id",
            "split",
            "metric_name",
            name="uq_experiment_metrics_experiment_split_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = created_at_column()
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    split: Mapped[str] = mapped_column(String(32), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    experiment: Mapped[Experiment] = relationship(
        "Experiment",
        back_populates="metrics",
    )
