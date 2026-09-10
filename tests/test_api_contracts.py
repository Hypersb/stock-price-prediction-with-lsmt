import json
import math
from datetime import date

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.main import create_app
from backend.app.services.market_data import MarketDataService
from ml.data.provider import MarketDataProvider


class FakeProvider(MarketDataProvider):
    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Date": ["2020-01-02", "2020-01-03", "2020-01-06"],
                "Open": [100.0, 101.0, 102.0],
                "High": [102.0, 103.0, 104.0],
                "Low": [99.0, 100.0, 101.0],
                "Close": [101.0, 102.0, 103.0],
                "Volume": [1000, 1100, 1200],
            }
        )


def build_client(monkeypatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    clear_settings_cache()
    application = create_app()
    application.state.market_data_service_factory = lambda: MarketDataService(
        provider=FakeProvider()
    )
    return TestClient(application)


def _assert_json_safe(value) -> None:
    if isinstance(value, float):
        assert math.isfinite(value)
    elif isinstance(value, dict):
        for nested in value.values():
            _assert_json_safe(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_json_safe(nested)


def test_openapi_schema_generation_succeeds(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/market-data/{symbol}" in paths
    assert "/api/v1/analysis/{symbol}/summary" in paths
    assert "/api/v1/features/{symbol}" in paths
    assert "/api/v1/models" in paths
    assert "/api/v1/backtests" in paths
    json.dumps(schema)


def test_request_id_header_is_returned(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get("/api/v1/health", headers={"X-Request-ID": "contract-1"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "contract-1"


def test_malformed_dates_return_validation_error(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get(
        "/api/v1/market-data/AAPL",
        params={"start_date": "not-a-date", "end_date": "2020-01-04"},
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] == "validation_error"


def test_missing_resource_contract(monkeypatch) -> None:
    class EmptyProvider(MarketDataProvider):
        def get_historical_data(self, symbol, start_date, end_date):
            return pd.DataFrame()

    monkeypatch.setenv("APP_ENV", "development")
    clear_settings_cache()
    application = create_app()
    application.state.market_data_service_factory = lambda: MarketDataService(
        provider=EmptyProvider()
    )
    client = TestClient(application)
    response = client.get(
        "/api/v1/market-data/ZZZZ",
        params={"start_date": "2020-01-01", "end_date": "2020-01-04"},
    )
    assert response.status_code == 404


def test_json_responses_contain_no_nan_or_infinity(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get(
        "/api/v1/analysis/AAPL/summary",
        params={"start_date": "2020-01-01", "end_date": "2020-01-07"},
    )
    assert response.status_code == 200
    payload = response.json()
    raw = response.content.decode("utf-8").lower()
    assert "nan" not in raw
    assert "infinity" not in raw
    _assert_json_safe(payload)


def test_invalid_backtest_configuration_contract(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.post(
        "/api/v1/backtests",
        json={
            "sample_kind": "out_of_sample",
            "symbol": "AAPL",
            "configuration": {
                "strategy_mode": "long_only",
                "transaction_cost_bps": -1,
            },
            "predictions": [
                {
                    "date": "2020-01-01",
                    "model": "m",
                    "task": "regression",
                    "predicted": 0.1,
                }
            ],
            "market_returns": [
                {"date": "2020-01-01", "realized_return": 0.1},
                {"date": "2020-01-02", "realized_return": 0.1},
            ],
        },
    )
    assert response.status_code == 422
