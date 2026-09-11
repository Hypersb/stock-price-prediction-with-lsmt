"""Tests for HTTP security and request safeguards."""

from __future__ import annotations

from datetime import date

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.core.security import validate_ticker_symbol
from backend.app.main import create_app
from backend.app.services.market_data import MarketDataService
from ml.data.provider import MarketDataProvider


class FakeProvider(MarketDataProvider):
    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
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


def build_client(monkeypatch) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "128")
    monkeypatch.setenv("MAX_MARKET_DATA_DAYS", "30")
    clear_settings_cache()
    application = create_app()
    application.state.market_data_service_factory = lambda: MarketDataService(
        provider=FakeProvider()
    )
    return TestClient(application)


def test_security_headers_are_present(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "referrer-policy" in response.headers


def test_oversized_request_body_is_rejected(monkeypatch) -> None:
    client = build_client(monkeypatch)
    payload = {"sample_kind": "out_of_sample", "padding": "x" * 200}
    response = client.post("/api/v1/backtests", json=payload)
    assert response.status_code == 413
    body = response.json()
    assert body["error"] == "payload_too_large"
    assert "traceback" not in response.text.lower()


def test_invalid_ticker_symbol_is_rejected(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get(
        "/api/v1/market-data/../etc/passwd",
        params={"start_date": "2020-01-01", "end_date": "2020-01-10"},
    )
    assert response.status_code in {400, 404, 422}
    assert "DATABASE_URL" not in response.text


def test_market_data_range_limit_is_enforced(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get(
        "/api/v1/market-data/AAPL",
        params={"start_date": "2010-01-01", "end_date": "2020-01-01"},
    )
    assert response.status_code == 400
    assert "maximum" in response.json()["detail"].lower()


def test_unexpected_errors_do_not_leak_stack_traces(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    clear_settings_cache()
    application = create_app()

    @application.get("/api/v1/_boom")
    def _boom() -> None:
        raise RuntimeError("secret filesystem path /var/secret/key")

    client = TestClient(application, raise_server_exceptions=False)
    response = client.get("/api/v1/_boom")
    assert response.status_code == 500
    payload = response.json()
    assert payload["error"] == "internal_error"
    assert "secret" not in response.text.lower()
    assert "/var/" not in response.text


def test_validate_ticker_symbol_accepts_share_classes() -> None:
    assert validate_ticker_symbol("brk.b") == "BRK.B"
