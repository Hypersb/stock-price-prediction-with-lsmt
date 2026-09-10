"""Experiment persistence repository."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.db.metrics import normalize_metric_value
from backend.app.db.models import Experiment, ExperimentMetric


@dataclass(frozen=True)
class ExperimentCreate:
    """Input payload for creating an experiment row."""

    symbol: str
    task: str
    model_name: str
    target_name: str
    forecast_horizon: int
    feature_count: int = 0
    lookback: int | None = None
    seed: int | None = None
    feature_names: list[str] | None = None
    model_configuration: dict[str, Any] | None = None
    training_configuration: dict[str, Any] | None = None
    status: str = "created"
    train_start: date | None = None
    train_end: date | None = None
    validation_start: date | None = None
    validation_end: date | None = None
    test_start: date | None = None
    test_end: date | None = None
    best_epoch: int | None = None
    best_validation_loss: float | None = None
    checkpoint_reference: str | None = None


@dataclass(frozen=True)
class MetricCreate:
    """Input payload for one experiment metric."""

    split: str
    metric_name: str
    metric_value: float | None


class ExperimentRepository:
    """Domain-specific persistence operations for experiments."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, payload: ExperimentCreate) -> Experiment:
        experiment = Experiment(
            symbol=payload.symbol.strip().upper(),
            task=payload.task,
            model_name=payload.model_name,
            target_name=payload.target_name,
            forecast_horizon=payload.forecast_horizon,
            feature_count=payload.feature_count,
            lookback=payload.lookback,
            seed=payload.seed,
            feature_names=payload.feature_names,
            model_configuration=payload.model_configuration,
            training_configuration=payload.training_configuration,
            status=payload.status,
            train_start=payload.train_start,
            train_end=payload.train_end,
            validation_start=payload.validation_start,
            validation_end=payload.validation_end,
            test_start=payload.test_start,
            test_end=payload.test_end,
            best_epoch=payload.best_epoch,
            best_validation_loss=normalize_metric_value(payload.best_validation_loss)
            if payload.best_validation_loss is not None
            else None,
            checkpoint_reference=payload.checkpoint_reference,
        )
        self.session.add(experiment)
        self.session.flush()
        return experiment

    def get(self, experiment_id: uuid.UUID) -> Experiment | None:
        statement: Select[tuple[Experiment]] = (
            select(Experiment)
            .where(Experiment.id == experiment_id)
            .options(selectinload(Experiment.metrics))
        )
        return self.session.scalar(statement)

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        symbol: str | None = None,
    ) -> tuple[list[Experiment], int]:
        filters = []
        if symbol:
            filters.append(Experiment.symbol == symbol.strip().upper())
        total = self.session.scalar(
            select(func.count()).select_from(Experiment).where(*filters)
        ) or 0
        statement = (
            select(Experiment)
            .where(*filters)
            .order_by(Experiment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(statement)), int(total)

    def add_metrics(
        self, experiment_id: uuid.UUID, metrics: list[MetricCreate]
    ) -> list[ExperimentMetric]:
        created: list[ExperimentMetric] = []
        for metric in metrics:
            row = ExperimentMetric(
                experiment_id=experiment_id,
                split=metric.split,
                metric_name=metric.metric_name,
                metric_value=normalize_metric_value(metric.metric_value),
            )
            self.session.add(row)
            created.append(row)
        self.session.flush()
        return created

    def list_metrics(self, experiment_id: uuid.UUID) -> list[ExperimentMetric]:
        statement = (
            select(ExperimentMetric)
            .where(ExperimentMetric.experiment_id == experiment_id)
            .order_by(ExperimentMetric.split, ExperimentMetric.metric_name)
        )
        return list(self.session.scalars(statement))
