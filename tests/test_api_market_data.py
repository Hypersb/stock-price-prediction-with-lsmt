from datetime import date

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.main import create_app
from backend.app.services.market_data import MarketDataService
from ml.data.provider import MarketDataProvider


class FakeProvider(MarketDataProvider):
    def __init__(self, data: pd.DataFrame | None = None, empty: bool = False) -> None:
        self.empty = empty
        self.data = data
        self.calls: list[tuple[str, date, date]] = []

    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        self.calls.append((symbol, start_date, end_date))
        if self.empty:
            return pd.DataFrame()
        assert self.data is not None
        return self.data.copy()


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": ["2020-01-02", "2020-01-03"],
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1000, 1100],
        }
    )


def build_client(provider: MarketDataProvider, monkeypatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("MAX_MARKET_DATA_DAYS", "3650")
    clear_settings_cache()
    application = create_app()
    application.state.market_data_service_factory = lambda: MarketDataService(
        provider=provider
    )
    return TestClient(application)


def test_market_data_endpoint_uses_injected_provider(monkeypatch) -> None:
    provider = FakeProvider(sample_frame())
    client = build_client(provider, monkeypatch)

    response = client.get(
        "/api/v1/market-data/aapl",
        params={"start_date": "2020-01-01", "end_date": "2020-01-04"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "AAPL"
    assert payload["count"] == 2
    assert payload["data"][0]["close"] == 101.0
    assert provider.calls == [("AAPL", date(2020, 1, 1), date(2020, 1, 4))]


def test_market_data_rejects_inverted_dates(monkeypatch) -> None:
    client = build_client(FakeProvider(sample_frame()), monkeypatch)
    response = client.get(
        "/api/v1/market-data/AAPL",
        params={"start_date": "2020-02-01", "end_date": "2020-01-01"},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "bad_request"


def test_market_data_rejects_excessive_range(monkeypatch) -> None:
    monkeypatch.setenv("MAX_MARKET_DATA_DAYS", "30")
    clear_settings_cache()
    provider = FakeProvider(sample_frame())
    application = create_app()
    application.state.market_data_service_factory = lambda: MarketDataService(
        provider=provider
    )
    client = TestClient(application)

    response = client.get(
        "/api/v1/market-data/AAPL",
        params={"start_date": "2020-01-01", "end_date": "2020-03-01"},
    )
    assert response.status_code == 400
    assert "maximum" in response.json()["detail"]
    assert provider.calls == []


def test_market_data_returns_not_found_for_empty_provider(monkeypatch) -> None:
    client = build_client(FakeProvider(empty=True), monkeypatch)
    response = client.get(
        "/api/v1/market-data/ZZZZ",
        params={"start_date": "2020-01-01", "end_date": "2020-01-04"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_market_data_validation_error_for_bad_symbol_type_path(monkeypatch) -> None:
    client = build_client(FakeProvider(sample_frame()), monkeypatch)
    response = client.get(
        "/api/v1/market-data/%20",
        params={"start_date": "2020-01-01", "end_date": "2020-01-04"},
    )
    assert response.status_code == 400
