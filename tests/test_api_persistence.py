from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.db.base import Base
from backend.app.db.session import build_database, configure_database, reset_database
from backend.app.main import create_app
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
    WalkForwardFoldCreate,
    WalkForwardRepository,
    WalkForwardRunCreate,
)


def build_db_client(monkeypatch, tmp_path):
    db_path = tmp_path / "api_persistence.db"
    url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", url)
    clear_settings_cache()
    reset_database()
    database = configure_database(url)
    Base.metadata.create_all(database.engine)
    application = create_app()
    return TestClient(application), database


def test_experiment_and_metrics_api(monkeypatch, tmp_path) -> None:
    client, database = build_db_client(monkeypatch, tmp_path)
    with database.create_session() as session:
        repo = ExperimentRepository(session)
        experiment = repo.create(
            ExperimentCreate(
                symbol="AAPL",
                task="regression",
                model_name="lstm",
                target_name="future_return_1",
                forecast_horizon=1,
                feature_count=3,
                status="completed",
            )
        )
        repo.add_metrics(
            experiment.id,
            [MetricCreate(split="test", metric_name="rmse", metric_value=0.2)],
        )
        session.commit()
        experiment_id = experiment.id

    listed = client.get("/api/v1/experiments", params={"limit": 10, "offset": 0})
    assert listed.status_code == 200
    payload = listed.json()
    assert payload["total"] == 1
    assert payload["items"][0]["symbol"] == "AAPL"

    detail = client.get(f"/api/v1/experiments/{experiment_id}")
    assert detail.status_code == 200
    assert detail.json()["model_name"] == "lstm"

    metrics = client.get(f"/api/v1/experiments/{experiment_id}/metrics")
    assert metrics.status_code == 200
    assert metrics.json()["metrics"][0]["metric_name"] == "rmse"

    missing = client.get(f"/api/v1/experiments/{uuid4()}")
    assert missing.status_code == 404
    reset_database()


def test_walk_forward_and_backtest_api(monkeypatch, tmp_path) -> None:
    client, database = build_db_client(monkeypatch, tmp_path)
    with database.create_session() as session:
        experiment = ExperimentRepository(session).create(
            ExperimentCreate(
                symbol="MSFT",
                task="regression",
                model_name="linear_regression",
                target_name="future_return_1",
                forecast_horizon=1,
            )
        )
        run = WalkForwardRepository(session).create_run(
            WalkForwardRunCreate(
                experiment_id=experiment.id,
                symbol="MSFT",
                model_name="linear_regression",
                task="regression",
                window_type="rolling",
                initial_train_size=40,
                validation_size=10,
                test_size=10,
                step_size=10,
                forecast_horizon=1,
            )
        )
        WalkForwardRepository(session).add_folds(
            run.id,
            [
                WalkForwardFoldCreate(
                    fold_number=1,
                    train_start=date(2020, 1, 1),
                    train_end=date(2020, 2, 1),
                    test_start=date(2020, 3, 1),
                    test_end=date(2020, 3, 15),
                    train_count=40,
                    test_count=10,
                )
            ],
        )
        backtest = BacktestRepository(session).create(
            BacktestCreate(
                symbol="MSFT",
                model_name="linear_regression",
                task="regression",
                strategy_mode="long_only",
                observation_count=1,
                start_date=date(2020, 3, 2),
                end_date=date(2020, 3, 2),
                experiment_id=experiment.id,
                walk_forward_run_id=run.id,
            ),
            metrics=[BacktestMetricCreate(metric_name="sharpe_ratio", metric_value=0.9)],
            equity_points=[
                BacktestEquityCreate(date=date(2020, 3, 2), equity=1.02, net_return=0.02)
            ],
        )
        session.commit()
        run_id = run.id
        backtest_id = backtest.id

    wf = client.get(f"/api/v1/walk-forward/{run_id}")
    assert wf.status_code == 200
    assert wf.json()["folds"][0]["fold_number"] == 1

    listed = client.get("/api/v1/backtests")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    detail = client.get(f"/api/v1/backtests/{backtest_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["sample_kind"] == "out_of_sample"
    assert body["metrics"][0]["metric_name"] == "sharpe_ratio"
    assert body["equity_curve"][0]["equity"] == 1.02
    assert "nan" not in detail.content.decode("utf-8").lower()

    assert client.get(f"/api/v1/backtests/{uuid4()}").status_code == 404
    reset_database()
