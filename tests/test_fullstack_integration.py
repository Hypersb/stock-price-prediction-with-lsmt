"""Full-stack integration workflows without Yahoo Finance or model training."""

from __future__ import annotations

from datetime import date
from uuid import UUID

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.contracts.frontend_api import FRONTEND_API_CONTRACTS
from backend.app.core.config import clear_settings_cache
from backend.app.db.base import Base
from backend.app.db.session import configure_database, reset_database
from backend.app.main import create_app
from backend.app.repositories.backtests import (
    BacktestCreate,
    BacktestEquityCreate,
    BacktestMetricCreate,
)
from backend.app.repositories.experiments import ExperimentCreate, MetricCreate
from backend.app.repositories.walk_forward import (
    OutOfSamplePredictionCreate,
    WalkForwardFoldCreate,
    WalkForwardRunCreate,
)
from backend.app.services.market_data import MarketDataService
from backend.app.services.research_persistence import (
    ResearchPersistenceBundle,
    ResearchPersistenceService,
)
from ml.data.provider import MarketDataProvider


class DeterministicProvider(MarketDataProvider):
    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Date": [
                    "2020-01-02",
                    "2020-01-03",
                    "2020-01-06",
                    "2020-01-07",
                    "2020-01-08",
                ],
                "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
                "High": [102.0, 103.0, 104.0, 105.0, 106.0],
                "Low": [99.0, 100.0, 101.0, 102.0, 103.0],
                "Close": [101.0, 102.0, 103.0, 102.5, 104.0],
                "Volume": [1000, 1100, 1200, 1150, 1300],
            }
        )


FRONTEND_RESPONSE_KEYS = {
    contract.response_schema: set(contract.required_properties)
    for contract in FRONTEND_API_CONTRACTS
}


def _assert_frontend_shape(schema_name: str, payload: dict) -> None:
    required = FRONTEND_RESPONSE_KEYS[schema_name]
    missing = required - set(payload)
    assert not missing, f"{schema_name} missing keys: {sorted(missing)}"


def build_stack(monkeypatch, tmp_path):
    db_path = tmp_path / "fullstack.db"
    url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", url)
    clear_settings_cache()
    reset_database()
    database = configure_database(url)
    Base.metadata.create_all(database.engine)
    application = create_app()
    application.state.market_data_service_factory = lambda: MarketDataService(
        provider=DeterministicProvider()
    )
    return TestClient(application), database


def test_workflow_market_and_analysis_contract(monkeypatch, tmp_path) -> None:
    client, _database = build_stack(monkeypatch, tmp_path)
    params = {"start_date": "2020-01-01", "end_date": "2020-01-10"}

    market = client.get("/api/v1/market-data/AAPL", params=params)
    assert market.status_code == 200
    market_payload = market.json()
    _assert_frontend_shape("MarketDataResponse", market_payload)
    assert market_payload["symbol"] == "AAPL"
    assert market_payload["count"] == 5
    assert market_payload["data"][0]["date"] == "2020-01-02"
    assert all(isinstance(row["close"], (int, float)) for row in market_payload["data"])

    analysis = client.get("/api/v1/analysis/AAPL/summary", params=params)
    assert analysis.status_code == 200
    analysis_payload = analysis.json()
    _assert_frontend_shape("AnalysisSummaryResponse", analysis_payload)
    assert analysis_payload["observation_count"] == 5
    assert analysis_payload["return_count"] >= 1
    assert analysis_payload["cumulative_return"] is not None
    reset_database()


def test_workflow_experiment_metrics_api_frontend_shape(monkeypatch, tmp_path) -> None:
    client, database = build_stack(monkeypatch, tmp_path)
    with database.create_session() as session:
        result = ResearchPersistenceService(session).persist_bundle(
            ResearchPersistenceBundle(
                experiment=ExperimentCreate(
                    symbol="AAPL",
                    task="regression",
                    model_name="linear_regression",
                    target_name="future_return_1",
                    forecast_horizon=1,
                    feature_count=4,
                    status="completed",
                    best_validation_loss=float("nan"),
                ),
                metrics=(
                    MetricCreate(split="validation", metric_name="rmse", metric_value=0.11),
                    MetricCreate(split="test", metric_name="rmse", metric_value=0.13),
                    MetricCreate(split="test", metric_name="mae", metric_value=float("inf")),
                ),
            )
        )
        session.commit()
        experiment_id = result.experiment_id

    listed = client.get("/api/v1/experiments", params={"limit": 10, "offset": 0})
    assert listed.status_code == 200
    list_payload = listed.json()
    _assert_frontend_shape("ExperimentListResponse", list_payload)
    assert list_payload["total"] == 1
    assert list_payload["limit"] == 10
    assert list_payload["items"][0]["id"] == str(experiment_id)

    detail = client.get(f"/api/v1/experiments/{experiment_id}")
    assert detail.status_code == 200
    detail_payload = detail.json()
    _assert_frontend_shape("ExperimentDetail", detail_payload)
    assert detail_payload["best_validation_loss"] is None
    assert UUID(detail_payload["id"]) == experiment_id

    metrics = client.get(f"/api/v1/experiments/{experiment_id}/metrics")
    assert metrics.status_code == 200
    metrics_payload = metrics.json()
    _assert_frontend_shape("ExperimentMetricsResponse", metrics_payload)
    values = {
        (item["split"], item["metric_name"]): item["metric_value"]
        for item in metrics_payload["metrics"]
    }
    assert values[("test", "rmse")] == 0.13
    assert values[("test", "mae")] is None
    reset_database()


def test_workflow_walk_forward_and_oos_predictions(monkeypatch, tmp_path) -> None:
    client, database = build_stack(monkeypatch, tmp_path)
    with database.create_session() as session:
        result = ResearchPersistenceService(session).persist_bundle(
            ResearchPersistenceBundle(
                experiment=ExperimentCreate(
                    symbol="MSFT",
                    task="regression",
                    model_name="naive",
                    target_name="future_return_1",
                    forecast_horizon=1,
                    status="completed",
                ),
                walk_forward=WalkForwardRunCreate(
                    symbol="MSFT",
                    model_name="naive",
                    task="regression",
                    window_type="expanding",
                    initial_train_size=50,
                    validation_size=10,
                    test_size=10,
                    step_size=10,
                    forecast_horizon=1,
                    gap=1,
                ),
                folds=(
                    WalkForwardFoldCreate(
                        fold_number=1,
                        train_start=date(2020, 1, 2),
                        train_end=date(2020, 3, 1),
                        test_start=date(2020, 3, 3),
                        test_end=date(2020, 3, 17),
                        train_count=50,
                        test_count=10,
                        fold_metrics={"rmse": 0.2, "directional_accuracy": float("nan")},
                    ),
                ),
                predictions=(
                    OutOfSamplePredictionCreate(
                        fold=1,
                        model_name="naive",
                        task="regression",
                        symbol="MSFT",
                        prediction_date=date(2020, 3, 3),
                        realization_date=date(2020, 3, 4),
                        actual_target=0.01,
                        predicted_value=0.008,
                    ),
                ),
            )
        )
        session.commit()
        run_id = result.walk_forward_run_id
        assert run_id is not None

    response = client.get(f"/api/v1/walk-forward/{run_id}")
    assert response.status_code == 200
    payload = response.json()
    _assert_frontend_shape("WalkForwardRunResponse", payload)
    assert payload["symbol"] == "MSFT"
    assert payload["gap"] == 1
    assert payload["folds"][0]["train_start"] == "2020-01-02"
    assert payload["folds"][0]["test_end"] == "2020-03-17"
    assert payload["folds"][0]["fold_metrics"]["rmse"] == 0.2
    assert payload["folds"][0]["fold_metrics"]["directional_accuracy"] is None
    assert payload["experiment_id"] == str(result.experiment_id)
    reset_database()


def test_workflow_backtest_persistence_api_frontend_shape(monkeypatch, tmp_path) -> None:
    client, database = build_stack(monkeypatch, tmp_path)
    with database.create_session() as session:
        result = ResearchPersistenceService(session).persist_bundle(
            ResearchPersistenceBundle(
                experiment=ExperimentCreate(
                    symbol="AAPL",
                    task="regression",
                    model_name="linear_regression",
                    target_name="future_return_1",
                    forecast_horizon=1,
                    status="completed",
                ),
                walk_forward=WalkForwardRunCreate(
                    symbol="AAPL",
                    model_name="linear_regression",
                    task="regression",
                    window_type="rolling",
                    initial_train_size=40,
                    validation_size=0,
                    test_size=10,
                    step_size=10,
                    forecast_horizon=1,
                ),
                backtest=BacktestCreate(
                    symbol="AAPL",
                    model_name="linear_regression",
                    task="regression",
                    strategy_mode="long_only",
                    transaction_cost_bps=5.0,
                    slippage_bps=1.0,
                    initial_capital=1.0,
                    start_date=date(2020, 4, 1),
                    end_date=date(2020, 4, 30),
                    observation_count=2,
                    sample_kind="out_of_sample",
                ),
                backtest_metrics=(
                    BacktestMetricCreate(metric_name="sharpe", metric_value=0.55),
                    BacktestMetricCreate(
                        metric_name="max_drawdown", metric_value=float("-inf")
                    ),
                ),
                equity_points=(
                    BacktestEquityCreate(
                        date=date(2020, 4, 1),
                        position=1.0,
                        gross_return=0.01,
                        cost=0.0001,
                        net_return=0.0099,
                        equity=1.0099,
                    ),
                    BacktestEquityCreate(
                        date=date(2020, 4, 2),
                        position=1.0,
                        gross_return=-0.005,
                        cost=0.0,
                        net_return=-0.005,
                        equity=1.0048,
                    ),
                ),
            )
        )
        session.commit()
        backtest_id = result.backtest_id
        assert backtest_id is not None

    listed = client.get("/api/v1/backtests", params={"limit": 5, "offset": 0})
    assert listed.status_code == 200
    list_payload = listed.json()
    _assert_frontend_shape("PersistedBacktestListResponse", list_payload)
    assert list_payload["total"] == 1
    assert list_payload["items"][0]["id"] == str(backtest_id)

    detail = client.get(f"/api/v1/backtests/{backtest_id}")
    assert detail.status_code == 200
    detail_payload = detail.json()
    _assert_frontend_shape("PersistedBacktestDetail", detail_payload)
    assert detail_payload["transaction_cost_bps"] == 5.0
    assert detail_payload["slippage_bps"] == 1.0
    assert detail_payload["strategy_mode"] == "long_only"
    metric_map = {
        item["metric_name"]: item["metric_value"] for item in detail_payload["metrics"]
    }
    assert metric_map["sharpe"] == 0.55
    assert metric_map["max_drawdown"] is None
    assert detail_payload["equity_curve"][0]["date"] == "2020-04-01"
    assert detail_payload["equity_curve"][1]["equity"] == 1.0048
    assert detail_payload["experiment_id"] == str(result.experiment_id)
    assert detail_payload["walk_forward_run_id"] == str(result.walk_forward_run_id)
    reset_database()
