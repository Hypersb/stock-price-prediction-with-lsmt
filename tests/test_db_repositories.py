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
    WalkForwardRepository,
    WalkForwardRunCreate,
)


@pytest.fixture()
def session():
    database = build_database("sqlite:///:memory:")
    Base.metadata.create_all(database.engine)
    with database.create_session() as active:
        yield active
    database.engine.dispose()


def test_experiment_repository_create_list_and_metrics(session) -> None:
    repo = ExperimentRepository(session)
    experiment = repo.create(
        ExperimentCreate(
            symbol="aapl",
            task="regression",
            model_name="lstm",
            target_name="future_return_1",
            forecast_horizon=1,
            feature_count=4,
            best_validation_loss=float("nan"),
            status="completed",
        )
    )
    repo.add_metrics(
        experiment.id,
        [
            MetricCreate(split="test", metric_name="rmse", metric_value=0.11),
            MetricCreate(split="test", metric_name="mae", metric_value=float("inf")),
        ],
    )
    session.commit()

    loaded = repo.get(experiment.id)
    listed, total = repo.list(limit=10, offset=0, symbol="AAPL")
    metrics = repo.list_metrics(experiment.id)

    assert loaded is not None
    assert loaded.best_validation_loss is None
    assert total == 1
    assert listed[0].id == experiment.id
    assert {item.metric_name: item.metric_value for item in metrics} == {
        "rmse": 0.11,
        "mae": None,
    }


def test_repository_transaction_rollback(session) -> None:
    repo = ExperimentRepository(session)
    experiment = repo.create(
        ExperimentCreate(
            symbol="MSFT",
            task="classification",
            model_name="logistic_regression",
            target_name="direction_1",
            forecast_horizon=1,
        )
    )
    session.flush()
    experiment_id = experiment.id
    session.rollback()
    assert repo.get(experiment_id) is None


def test_walk_forward_and_prediction_repositories(session) -> None:
    experiments = ExperimentRepository(session)
    experiment = experiments.create(
        ExperimentCreate(
            symbol="AAPL",
            task="regression",
            model_name="linear_regression",
            target_name="future_return_1",
            forecast_horizon=1,
        )
    )
    wf = WalkForwardRepository(session)
    run = wf.create_run(
        WalkForwardRunCreate(
            experiment_id=experiment.id,
            symbol="AAPL",
            model_name="linear_regression",
            task="regression",
            window_type="expanding",
            initial_train_size=100,
            validation_size=20,
            test_size=20,
            step_size=20,
            forecast_horizon=1,
        )
    )
    wf.add_folds(
        run.id,
        [
            WalkForwardFoldCreate(
                fold_number=1,
                train_start=date(2020, 1, 1),
                train_end=date(2020, 4, 1),
                test_start=date(2020, 5, 1),
                test_end=date(2020, 6, 1),
                train_count=100,
                test_count=20,
                fold_metrics={"rmse": 0.04},
            )
        ],
    )
    predictions = PredictionRepository(session)
    predictions.add_many(
        [
            OutOfSamplePredictionCreate(
                walk_forward_run_id=run.id,
                experiment_id=experiment.id,
                fold=1,
                model_name="linear_regression",
                task="regression",
                symbol="AAPL",
                prediction_date=date(2020, 5, 2),
                predicted_value=0.01,
            )
        ]
    )
    session.commit()
    loaded = wf.get_run(run.id)
    stored = predictions.list_for_run(run.id)
    assert loaded is not None
    assert len(loaded.folds) == 1
    assert stored[0].sample_kind == "out_of_sample"


def test_backtest_repository_create_and_retrieve(session) -> None:
    repo = BacktestRepository(session)
    run = repo.create(
        BacktestCreate(
            symbol="AAPL",
            model_name="oos_model",
            task="regression",
            strategy_mode="long_only",
            observation_count=2,
            start_date=date(2020, 1, 2),
            end_date=date(2020, 1, 3),
        ),
        metrics=[BacktestMetricCreate(metric_name="sharpe_ratio", metric_value=0.5)],
        equity_points=[
            BacktestEquityCreate(date=date(2020, 1, 2), equity=1.01, net_return=0.01)
        ],
    )
    session.commit()
    loaded = repo.get(run.id)
    listed, total = repo.list(limit=5)
    assert loaded is not None
    assert total == 1
    assert loaded.metrics[0].metric_name == "sharpe_ratio"
    assert loaded.equity_points[0].equity == 1.01
    assert listed[0].id == run.id
