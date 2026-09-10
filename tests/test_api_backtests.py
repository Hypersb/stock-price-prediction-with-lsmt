from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.main import create_app


def build_client(monkeypatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    clear_settings_cache()
    return TestClient(create_app())


def oos_payload(**overrides):
    payload = {
        "sample_kind": "out_of_sample",
        "symbol": "AAPL",
        "configuration": {
            "strategy_mode": "long_only",
            "signal_threshold": 0.0,
            "transaction_cost_bps": 10.0,
            "slippage_bps": 0.0,
            "initial_capital": 1.0,
        },
        "predictions": [
            {
                "date": "2020-01-01",
                "model": "oos_model",
                "task": "regression",
                "predicted": 0.1,
            },
            {
                "date": "2020-01-02",
                "model": "oos_model",
                "task": "regression",
                "predicted": -0.1,
            },
            {
                "date": "2020-01-03",
                "model": "oos_model",
                "task": "regression",
                "predicted": 0.1,
            },
        ],
        "market_returns": [
            {"date": "2020-01-01", "realized_return": 0.5},
            {"date": "2020-01-02", "realized_return": 0.1},
            {"date": "2020-01-03", "realized_return": -0.1},
            {"date": "2020-01-04", "realized_return": 0.1},
        ],
    }
    payload.update(overrides)
    return payload


def test_backtest_endpoint_runs_deterministic_oos_flow(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.post("/api/v1/backtests", json=oos_payload())
    assert response.status_code == 200
    payload = response.json()
    assert payload["sample_kind"] == "out_of_sample"
    assert payload["observations"] == 3
    assert payload["model"] == "oos_model"
    assert "sharpe_ratio" in payload["risk_metrics"]
    assert "buy_and_hold" in payload["benchmark_metrics"]
    assert len(payload["equity_curve"]) == 3


def test_backtest_rejects_in_sample_label(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.post(
        "/api/v1/backtests",
        json=oos_payload(sample_kind="in_sample"),
    )
    assert response.status_code == 422


def test_backtest_rejects_invalid_strategy_mode(monkeypatch) -> None:
    client = build_client(monkeypatch)
    payload = oos_payload()
    payload["configuration"]["strategy_mode"] = "all_in"
    response = client.post("/api/v1/backtests", json=payload)
    assert response.status_code == 422


def test_backtest_rejects_mixed_models(monkeypatch) -> None:
    client = build_client(monkeypatch)
    payload = oos_payload()
    payload["predictions"][1]["model"] = "other_model"
    response = client.post("/api/v1/backtests", json=payload)
    assert response.status_code == 400
    assert "one model" in response.json()["detail"]
