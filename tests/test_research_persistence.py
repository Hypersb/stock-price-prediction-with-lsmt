"""Integration tests for research result persistence orchestration."""

from __future__ import annotations

from datetime import date

import pytest

from backend.app.db.base import Base
from backend.app.db.session import build_database
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
    WalkForwardRunCreate,
)
from backend.app.services.research_persistence import (
    ResearchPersistenceBundle,
    ResearchPersistenceService,
)


@pytest.fixture()
def session():
    database = build_database("sqlite:///:memory:")
    Base.metadata.create_all(database.engine)
    with database.create_session() as active:
        yield active
    database.engine.dispose()


def _bundle(*, include_backtest: bool = True) -> ResearchPersistenceBundle:
    experiment = ExperimentCreate(
        symbol="aapl",
        task="regression",
        model_name="linear_regression",
        target_name="future_return_1",
        forecast_horizon=1,
        feature_count=3,
        status="completed",
        checkpoint_reference="file://checkpoints/demo.pt",
        best_validation_loss=float("nan"),
    )
    walk_forward = WalkForwardRunCreate(
        symbol="AAPL",
        model_name="linear_regression",
        task="regression",
        window_type="expanding",
        initial_train_size=100,
        validation_size=20,
        test_size=20,
        step_size=20,
        forecast_horizon=1,
        gap=1,
    )
    folds = (
        WalkForwardFoldCreate(
            fold_number=1,
            train_start=date(2020, 1, 2),
            train_end=date(2020, 6, 1),
            test_start=date(2020, 6, 2),
            test_end=date(2020, 6, 30),
            train_count=100,
            test_count=20,
            fold_metrics={"rmse": 0.12, "mae": float("inf")},
        ),
    )
    predictions = (
        OutOfSamplePredictionCreate(
            fold=1,
            model_name="linear_regression",
            task="regression",
            symbol="AAPL",
            prediction_date=date(2020, 6, 2),
            realization_date=date(2020, 6, 3),
            actual_target=0.01,
            predicted_value=float("nan"),
        ),
    )
    backtest = None
    backtest_metrics: tuple[BacktestMetricCreate, ...] = ()
    equity: tuple[BacktestEquityCreate, ...] = ()
    if include_backtest:
        backtest = BacktestCreate(
            symbol="AAPL",
            model_name="linear_regression",
            task="regression",
            strategy_mode="long_only",
            transaction_cost_bps=5.0,
            slippage_bps=1.0,
            initial_capital=1.0,
            start_date=date(2020, 6, 2),
            end_date=date(2020, 6, 30),
            observation_count=1,
            sample_kind="out_of_sample",
        )
        backtest_metrics = (
            BacktestMetricCreate(metric_name="sharpe", metric_value=0.4),
            BacktestMetricCreate(metric_name="max_drawdown", metric_value=float("-inf")),
        )
        equity = (
            BacktestEquityCreate(
                date=date(2020, 6, 2),
                position=1.0,
                gross_return=0.01,
                cost=0.0001,
                net_return=0.0099,
                equity=1.0099,
            ),
        )
    return ResearchPersistenceBundle(
        experiment=experiment,
        metrics=(
            MetricCreate(split="validation", metric_name="rmse", metric_value=0.15),
            MetricCreate(split="test", metric_name="rmse", metric_value=0.18),
        ),
        walk_forward=walk_forward,
        folds=folds,
        predictions=predictions,
        backtest=backtest,
        backtest_metrics=backtest_metrics,
        equity_points=equity,
    )


def test_persist_research_bundle_links_all_artifacts(session) -> None:
    service = ResearchPersistenceService(session)
    result = service.persist_bundle(_bundle())
    session.commit()

    assert result.metric_count == 2
    assert result.fold_count == 1
    assert result.prediction_count == 1
    assert result.walk_forward_run_id is not None
    assert result.backtest_id is not None
    assert "experiment_id" in result.as_dict()

    experiment = ExperimentRepository(session).get(result.experiment_id)
    assert experiment is not None
    assert experiment.best_validation_loss is None
    assert experiment.checkpoint_reference == "file://checkpoints/demo.pt"

    metrics = ExperimentRepository(session).list_metrics(result.experiment_id)
    assert len(metrics) == 2

    run = service.walk_forward.get_run(result.walk_forward_run_id)
    assert run is not None
    assert run.experiment_id == result.experiment_id
    assert run.folds[0].fold_metrics == {"rmse": 0.12, "mae": None}

    predictions = PredictionRepository(session).list_for_run(result.walk_forward_run_id)
    assert len(predictions) == 1
    assert predictions[0].predicted_value is None
    assert predictions[0].experiment_id == result.experiment_id

    backtest = BacktestRepository(session).get(result.backtest_id)
    assert backtest is not None
    assert backtest.experiment_id == result.experiment_id
    assert backtest.walk_forward_run_id == result.walk_forward_run_id
    metric_map = {item.metric_name: item.metric_value for item in backtest.metrics}
    assert metric_map["sharpe"] == 0.4
    assert metric_map["max_drawdown"] is None
    assert len(backtest.equity_points) == 1


def test_persist_research_bundle_rolls_back_atomically(session) -> None:
    service = ResearchPersistenceService(session)
    result = service.persist_bundle(_bundle())
    experiment_id = result.experiment_id
    session.rollback()

    assert ExperimentRepository(session).get(experiment_id) is None
    listed, total = BacktestRepository(session).list(limit=10, offset=0)
    assert total == 0
    assert listed == []


def test_persist_bundle_rejects_folds_without_run(session) -> None:
    service = ResearchPersistenceService(session)
    bundle = ResearchPersistenceBundle(
        experiment=ExperimentCreate(
            symbol="MSFT",
            task="regression",
            model_name="naive",
            target_name="future_return_1",
            forecast_horizon=1,
        ),
        folds=(
            WalkForwardFoldCreate(
                fold_number=1,
                train_start=date(2020, 1, 2),
                train_end=date(2020, 2, 1),
                test_start=date(2020, 2, 2),
                test_end=date(2020, 2, 10),
                train_count=10,
                test_count=5,
            ),
        ),
    )
    with pytest.raises(ValueError, match="walk-forward"):
        service.persist_bundle(bundle)
