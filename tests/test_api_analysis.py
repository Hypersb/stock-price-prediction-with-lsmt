from datetime import date

import math

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.main import create_app
from backend.app.services.analysis import AnalysisService
from backend.app.services.market_data import MarketDataService
from ml.data.provider import MarketDataProvider


class FakeProvider(MarketDataProvider):
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        return self.data.copy()


def trending_frame() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=6, freq="D")
    closes = [100.0, 101.0, 102.0, 101.0, 103.0, 104.0]
    return pd.DataFrame(
        {
            "Date": dates.strftime("%Y-%m-%d"),
            "Open": closes,
            "High": [value + 1 for value in closes],
            "Low": [value - 1 for value in closes],
            "Close": closes,
            "Volume": [1000] * len(closes),
        }
    )


def build_client(provider: MarketDataProvider, monkeypatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    clear_settings_cache()
    market_service = MarketDataService(provider=provider)
    application = create_app()
    application.state.market_data_service_factory = lambda: market_service
    application.state.analysis_service_factory = lambda: AnalysisService(
        market_data_service=market_service
    )
    return TestClient(application)


def test_analysis_summary_returns_serializable_metrics(monkeypatch) -> None:
    client = build_client(FakeProvider(trending_frame()), monkeypatch)
    response = client.get(
        "/api/v1/analysis/AAPL/summary",
        params={"start_date": "2020-01-01", "end_date": "2020-01-07"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "AAPL"
    assert payload["observation_count"] == 6
    assert payload["return_count"] == 5
    assert payload["mean_return"] is not None
    assert payload["volatility"] is not None
    assert payload["cumulative_return"] is not None
    assert payload["maximum_drawdown"] is not None
    for key in (
        "mean_return",
        "median_return",
        "volatility",
        "cumulative_return",
        "maximum_drawdown",
    ):
        value = payload[key]
        assert value is None or (isinstance(value, float) and math.isfinite(value))


def test_analysis_summary_rejects_inverted_dates(monkeypatch) -> None:
    client = build_client(FakeProvider(trending_frame()), monkeypatch)
    response = client.get(
        "/api/v1/analysis/AAPL/summary",
        params={"start_date": "2020-02-01", "end_date": "2020-01-01"},
    )
    assert response.status_code == 400
