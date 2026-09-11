from datetime import date

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.main import create_app
from backend.app.services.features import FeatureService
from backend.app.services.market_data import MarketDataService
from ml.data.provider import MarketDataProvider


class FakeProvider(MarketDataProvider):
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        return self.data.copy()


def long_frame(periods: int = 80) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=periods, freq="D")
    closes = [100 + (index % 7) * 0.5 for index in range(periods)]
    return pd.DataFrame(
        {
            "Date": dates.strftime("%Y-%m-%d"),
            "Open": closes,
            "High": [value + 1 for value in closes],
            "Low": [value - 1 for value in closes],
            "Close": closes,
            "Volume": [1000 + index for index in range(periods)],
        }
    )


def build_client(provider: MarketDataProvider, monkeypatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("MAX_FEATURE_ROWS", "50")
    clear_settings_cache()
    market_service = MarketDataService(provider=provider)
    application = create_app()
    application.state.market_data_service_factory = lambda: market_service
    application.state.feature_service_factory = lambda: FeatureService(
        market_data_service=market_service
    )
    return TestClient(application)


def test_feature_endpoint_excludes_target_columns(monkeypatch) -> None:
    client = build_client(FakeProvider(long_frame()), monkeypatch)
    response = client.get(
        "/api/v1/features/AAPL",
        params={"start_date": "2020-01-01", "end_date": "2020-03-21", "limit": 10},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "AAPL"
    assert payload["feature_count"] == len(payload["feature_names"])
    assert payload["returned_rows"] == 10
    names = " ".join(payload["feature_names"]).lower()
    assert "target" not in names
    assert "future_return" not in names
    assert "direction_" not in names
    for name in payload["feature_names"]:
        assert "future" not in name.lower()
        assert "target" not in name.lower()


def test_feature_endpoint_respects_row_limit(monkeypatch) -> None:
    client = build_client(FakeProvider(long_frame()), monkeypatch)
    response = client.get(
        "/api/v1/features/MSFT",
        params={"start_date": "2020-01-01", "end_date": "2020-03-21", "limit": 5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["returned_rows"] == 5
    assert len(payload["features"]) == 5
    assert payload["limit"] == 5
    assert payload["offset"] == payload["observation_count"] - 5
    assert set(payload["features"][0]["values"]) == set(payload["feature_names"])


def test_feature_endpoint_offset_uses_chronological_slice(monkeypatch) -> None:
    client = build_client(FakeProvider(long_frame()), monkeypatch)
    response = client.get(
        "/api/v1/features/MSFT",
        params={
            "start_date": "2020-01-01",
            "end_date": "2020-03-21",
            "limit": 3,
            "offset": 0,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["offset"] == 0
    assert payload["returned_rows"] == 3
    assert payload["features"][0]["date"] < payload["features"][-1]["date"]
