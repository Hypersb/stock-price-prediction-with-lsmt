"""Walk-forward and prediction persistence repositories."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.db.metrics import normalize_metric_value
from backend.app.db.models import (
    OutOfSamplePrediction,
    WalkForwardFold,
    WalkForwardRun,
)


@dataclass(frozen=True)
class WalkForwardRunCreate:
    symbol: str
    model_name: str
    task: str
    window_type: str
    initial_train_size: int
    validation_size: int
    test_size: int
    step_size: int
    forecast_horizon: int
    gap: int = 0
    experiment_id: uuid.UUID | None = None


@dataclass(frozen=True)
class WalkForwardFoldCreate:
    fold_number: int
    train_start: date
    train_end: date
    test_start: date
    test_end: date
    train_count: int
    test_count: int
    validation_start: date | None = None
    validation_end: date | None = None
    validation_count: int = 0
    best_epoch: int | None = None
    fold_metrics: dict[str, Any] | None = None


@dataclass(frozen=True)
class OutOfSamplePredictionCreate:
    fold: int
    model_name: str
    task: str
    symbol: str
    prediction_date: date
    realization_date: date | None = None
    actual_target: float | None = None
    predicted_value: float | None = None
    predicted_probability: float | None = None
    predicted_class: int | None = None
    walk_forward_run_id: uuid.UUID | None = None
    experiment_id: uuid.UUID | None = None


class WalkForwardRepository:
    """Persist walk-forward runs and folds."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_run(self, payload: WalkForwardRunCreate) -> WalkForwardRun:
        run = WalkForwardRun(
            experiment_id=payload.experiment_id,
            symbol=payload.symbol.strip().upper(),
            model_name=payload.model_name,
            task=payload.task,
            window_type=payload.window_type,
            initial_train_size=payload.initial_train_size,
            validation_size=payload.validation_size,
            test_size=payload.test_size,
            step_size=payload.step_size,
            gap=payload.gap,
            forecast_horizon=payload.forecast_horizon,
        )
        self.session.add(run)
        self.session.flush()
        return run

    def add_folds(
        self, run_id: uuid.UUID, folds: list[WalkForwardFoldCreate]
    ) -> list[WalkForwardFold]:
        created: list[WalkForwardFold] = []
        for fold in folds:
            metrics = None
            if fold.fold_metrics is not None:
                metrics = {
                    key: normalize_metric_value(value)
                    for key, value in fold.fold_metrics.items()
                }
            row = WalkForwardFold(
                run_id=run_id,
                fold_number=fold.fold_number,
                train_start=fold.train_start,
                train_end=fold.train_end,
                validation_start=fold.validation_start,
                validation_end=fold.validation_end,
                test_start=fold.test_start,
                test_end=fold.test_end,
                train_count=fold.train_count,
                validation_count=fold.validation_count,
                test_count=fold.test_count,
                best_epoch=fold.best_epoch,
                fold_metrics=metrics,
            )
            self.session.add(row)
            created.append(row)
        self.session.flush()
        return created

    def get_run(self, run_id: uuid.UUID) -> WalkForwardRun | None:
        statement = (
            select(WalkForwardRun)
            .where(WalkForwardRun.id == run_id)
            .options(selectinload(WalkForwardRun.folds))
        )
        return self.session.scalar(statement)


class PredictionRepository:
    """Persist out-of-sample prediction observations only."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add_many(
        self, predictions: list[OutOfSamplePredictionCreate]
    ) -> list[OutOfSamplePrediction]:
        created: list[OutOfSamplePrediction] = []
        for item in predictions:
            row = OutOfSamplePrediction(
                walk_forward_run_id=item.walk_forward_run_id,
                experiment_id=item.experiment_id,
                fold=item.fold,
                model_name=item.model_name,
                task=item.task,
                symbol=item.symbol.strip().upper(),
                prediction_date=item.prediction_date,
                realization_date=item.realization_date,
                actual_target=normalize_metric_value(item.actual_target),
                predicted_value=normalize_metric_value(item.predicted_value),
                predicted_probability=normalize_metric_value(item.predicted_probability),
                predicted_class=item.predicted_class,
                sample_kind="out_of_sample",
            )
            self.session.add(row)
            created.append(row)
        self.session.flush()
        return created

    def list_for_run(self, run_id: uuid.UUID) -> list[OutOfSamplePrediction]:
        statement = (
            select(OutOfSamplePrediction)
            .where(OutOfSamplePrediction.walk_forward_run_id == run_id)
            .order_by(OutOfSamplePrediction.prediction_date)
        )
        return list(self.session.scalars(statement))

    def list_filtered(
        self,
        *,
        symbol: str,
        model_name: str,
        task: str,
        experiment_id: uuid.UUID | None = None,
        walk_forward_run_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> list[OutOfSamplePrediction]:
        """List persisted OOS predictions with explicit research filters."""
        statement = select(OutOfSamplePrediction).where(
            OutOfSamplePrediction.symbol == symbol.strip().upper(),
            OutOfSamplePrediction.model_name == model_name.lower(),
            OutOfSamplePrediction.task == task.lower(),
            OutOfSamplePrediction.sample_kind == "out_of_sample",
        )
        if experiment_id is not None:
            statement = statement.where(OutOfSamplePrediction.experiment_id == experiment_id)
        if walk_forward_run_id is not None:
            statement = statement.where(
                OutOfSamplePrediction.walk_forward_run_id == walk_forward_run_id
            )
        if start_date is not None:
            statement = statement.where(OutOfSamplePrediction.prediction_date >= start_date)
        if end_date is not None:
            statement = statement.where(OutOfSamplePrediction.prediction_date <= end_date)
        statement = (
            statement.order_by(OutOfSamplePrediction.prediction_date)
            .offset(max(0, offset))
            .limit(max(1, limit))
        )
        return list(self.session.scalars(statement))
