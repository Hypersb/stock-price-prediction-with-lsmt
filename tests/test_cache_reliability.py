"""Tests for in-process TTL cache and market-data caching behavior."""

from __future__ import annotations

from datetime import date

import pandas as pd

from backend.app.core.cache import TtlCache
from backend.app.core.config import clear_settings_cache
from backend.app.services.market_data import MarketDataService
from ml.data.provider import MarketDataProvider


def test_ttl_cache_evicts_oldest_when_full() -> None:
    cache: TtlCache[int] = TtlCache(max_size=2, ttl_seconds=60)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3


def test_ttl_cache_expires_entries(monkeypatch) -> None:
    cache: TtlCache[str] = TtlCache(max_size=4, ttl_seconds=10)
    times = iter([100.0, 100.0, 120.0])

    monkeypatch.setattr(
        "backend.app.core.cache.time.monotonic", lambda: next(times)
    )
    cache.set("k", "v")
    assert cache.get("k") == "v"
    assert cache.get("k") is None


def test_market_data_service_caches_identical_requests(monkeypatch) -> None:
    clear_settings_cache()
    calls = {"count": 0}

    class CountingProvider(MarketDataProvider):
        def get_historical_data(
            self, symbol: str, start_date: date, end_date: date
        ) -> pd.DataFrame:
            calls["count"] += 1
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

    service = MarketDataService(
        provider=CountingProvider(),
        cache=TtlCache(max_size=8, ttl_seconds=60),
    )
    first = service.get_ohlcv("AAPL", date(2020, 1, 1), date(2020, 1, 10))
    second = service.get_ohlcv("AAPL", date(2020, 1, 1), date(2020, 1, 10))
    assert first.count == second.count == 2
    assert calls["count"] == 1


def test_prediction_endpoint_does_not_train(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from backend.app.main import create_app

    monkeypatch.setenv("APP_ENV", "development")
    clear_settings_cache()
    client = TestClient(create_app())
    response = client.get(
        "/api/v1/models/lstm/predictions/AAPL",
        params={"task": "regression"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is False
    assert "does not train" in payload["message"]
