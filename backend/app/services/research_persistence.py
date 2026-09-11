"""Orchestrate persistence of complete research result bundles.

Persists experiment → metrics → walk-forward → OOS predictions → backtest
through existing repositories inside one SQLAlchemy session. Callers own
commit/rollback. Returns plain IDs — never ORM objects.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from backend.app.repositories.backtests import (
    BacktestCreate,
    BacktestEquityCreate,
    BacktestMetricCreate,
    BacktestRepository,
)
from backend.app.repositories.experiments import (
    ExperimentCreate,
    ExperimentRepository,
    MetricCreate,
)
from backend.app.repositories.walk_forward import (
    OutOfSamplePredictionCreate,
    PredictionRepository,
    WalkForwardFoldCreate,
    WalkForwardRepository,
    WalkForwardRunCreate,
)


def _sanitize_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _sanitize_metric_map(values: dict[str, Any] | None) -> dict[str, float | None] | None:
    if values is None:
        return None
    return {key: _sanitize_number(raw) for key, raw in values.items()}


@dataclass(frozen=True)
class ResearchPersistenceBundle:
    """Deterministic research artifacts ready for relational persistence."""

    experiment: ExperimentCreate
    metrics: tuple[MetricCreate, ...] = ()
    walk_forward: WalkForwardRunCreate | None = None
    folds: tuple[WalkForwardFoldCreate, ...] = ()
    predictions: tuple[OutOfSamplePredictionCreate, ...] = ()
    backtest: BacktestCreate | None = None
    backtest_metrics: tuple[BacktestMetricCreate, ...] = ()
    equity_points: tuple[BacktestEquityCreate, ...] = ()


@dataclass(frozen=True)
class ResearchPersistenceResult:
    """IDs and counts for a persisted research bundle (API-safe)."""

    experiment_id: uuid.UUID
    metric_count: int
    walk_forward_run_id: uuid.UUID | None = None
    fold_count: int = 0
    prediction_count: int = 0
    backtest_id: uuid.UUID | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": str(self.experiment_id),
            "metric_count": self.metric_count,
            "walk_forward_run_id": (
                str(self.walk_forward_run_id) if self.walk_forward_run_id else None
            ),
            "fold_count": self.fold_count,
            "prediction_count": self.prediction_count,
            "backtest_id": str(self.backtest_id) if self.backtest_id else None,
        }


class ResearchPersistenceService:
    """Persist linked research results without leaking ORM entities."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.experiments = ExperimentRepository(session)
        self.walk_forward = WalkForwardRepository(session)
        self.predictions = PredictionRepository(session)
        self.backtests = BacktestRepository(session)

    def persist_bundle(
        self, bundle: ResearchPersistenceBundle
    ) -> ResearchPersistenceResult:
        """Persist the full research chain inside the caller's transaction."""
        if bundle.folds and bundle.walk_forward is None:
            raise ValueError("walk-forward folds require a walk-forward run")
        if bundle.predictions and bundle.walk_forward is None:
            raise ValueError("out-of-sample predictions require a walk-forward run")
        if (
            bundle.backtest is None
            and (bundle.backtest_metrics or bundle.equity_points)
        ):
            raise ValueError("backtest metrics/equity require a backtest payload")

        experiment = self.experiments.create(bundle.experiment)
        metrics = [
            MetricCreate(
                split=item.split,
                metric_name=item.metric_name,
                metric_value=_sanitize_number(item.metric_value),
            )
            for item in bundle.metrics
        ]
        if metrics:
            self.experiments.add_metrics(experiment.id, metrics)

        walk_forward_run_id: uuid.UUID | None = None
        fold_count = 0
        prediction_count = 0

        if bundle.walk_forward is not None:
            run_payload = WalkForwardRunCreate(
                symbol=bundle.walk_forward.symbol,
                model_name=bundle.walk_forward.model_name,
                task=bundle.walk_forward.task,
                window_type=bundle.walk_forward.window_type,
                initial_train_size=bundle.walk_forward.initial_train_size,
                validation_size=bundle.walk_forward.validation_size,
                test_size=bundle.walk_forward.test_size,
                step_size=bundle.walk_forward.step_size,
                forecast_horizon=bundle.walk_forward.forecast_horizon,
                gap=bundle.walk_forward.gap,
                experiment_id=experiment.id,
            )
            run = self.walk_forward.create_run(run_payload)
            walk_forward_run_id = run.id

            sanitized_folds = [
                WalkForwardFoldCreate(
                    fold_number=fold.fold_number,
                    train_start=fold.train_start,
                    train_end=fold.train_end,
                    test_start=fold.test_start,
                    test_end=fold.test_end,
                    train_count=fold.train_count,
                    test_count=fold.test_count,
                    validation_start=fold.validation_start,
                    validation_end=fold.validation_end,
                    validation_count=fold.validation_count,
                    best_epoch=fold.best_epoch,
                    fold_metrics=_sanitize_metric_map(fold.fold_metrics),
                )
                for fold in bundle.folds
            ]
            if sanitized_folds:
                self.walk_forward.add_folds(run.id, sanitized_folds)
                fold_count = len(sanitized_folds)

            linked_predictions = [
                OutOfSamplePredictionCreate(
                    fold=item.fold,
                    model_name=item.model_name,
                    task=item.task,
                    symbol=item.symbol,
                    prediction_date=item.prediction_date,
                    realization_date=item.realization_date,
                    actual_target=_sanitize_number(item.actual_target),
                    predicted_value=_sanitize_number(item.predicted_value),
                    predicted_probability=_sanitize_number(item.predicted_probability),
                    predicted_class=item.predicted_class,
                    walk_forward_run_id=run.id,
                    experiment_id=experiment.id,
                )
                for item in bundle.predictions
            ]
            if linked_predictions:
                self.predictions.add_many(linked_predictions)
                prediction_count = len(linked_predictions)

        backtest_id: uuid.UUID | None = None
        if bundle.backtest is not None:
            backtest_payload = BacktestCreate(
                symbol=bundle.backtest.symbol,
                model_name=bundle.backtest.model_name,
                task=bundle.backtest.task,
                strategy_mode=bundle.backtest.strategy_mode,
                signal_threshold=bundle.backtest.signal_threshold,
                transaction_cost_bps=bundle.backtest.transaction_cost_bps,
                slippage_bps=bundle.backtest.slippage_bps,
                initial_capital=bundle.backtest.initial_capital,
                start_date=bundle.backtest.start_date,
                end_date=bundle.backtest.end_date,
                observation_count=bundle.backtest.observation_count,
                experiment_id=experiment.id,
                walk_forward_run_id=walk_forward_run_id,
                sample_kind=bundle.backtest.sample_kind,
            )
            metrics_payload = [
                BacktestMetricCreate(
                    metric_name=item.metric_name,
                    metric_value=_sanitize_number(item.metric_value),
                )
                for item in bundle.backtest_metrics
            ]
            equity_payload = [
                BacktestEquityCreate(
                    date=point.date,
                    position=_sanitize_number(point.position),
                    gross_return=_sanitize_number(point.gross_return),
                    cost=_sanitize_number(point.cost),
                    net_return=_sanitize_number(point.net_return),
                    equity=_sanitize_number(point.equity),
                )
                for point in bundle.equity_points
            ]
            backtest = self.backtests.create(
                backtest_payload,
                metrics=metrics_payload,
                equity_points=equity_payload,
            )
            backtest_id = backtest.id

        # Flush so IDs are assigned; do not commit — caller owns the transaction.
        self.session.flush()
        return ResearchPersistenceResult(
            experiment_id=experiment.id,
            metric_count=len(metrics),
            walk_forward_run_id=walk_forward_run_id,
            fold_count=fold_count,
            prediction_count=prediction_count,
            backtest_id=backtest_id,
        )
