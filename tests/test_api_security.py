"""Tests for HTTP security and request safeguards."""

from __future__ import annotations

import asyncio
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


def test_oversized_body_without_content_length_is_rejected(monkeypatch) -> None:
    """Chunked / missing Content-Length must still enforce the byte limit."""
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "128")
    clear_settings_cache()
    application = create_app()

    payload = b'{"sample_kind":"out_of_sample","padding":"' + (b"x" * 200) + b'"}'
    chunks = [payload[i : i + 40] for i in range(0, len(payload), 40)]
    chunk_index = 0

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/backtests",
        "raw_path": b"/api/v1/backtests",
        "query_string": b"",
        "root_path": "",
        "headers": [
            (b"host", b"testserver"),
            (b"content-type", b"application/json"),
            # intentionally omit content-length
        ],
        "client": ("127.0.0.1", 50000),
        "server": ("testserver", 80),
        "state": {},
    }
    sent: list[dict] = []

    async def receive() -> dict:
        nonlocal chunk_index
        if chunk_index < len(chunks):
            body = chunks[chunk_index]
            chunk_index += 1
            return {
                "type": "http.request",
                "body": body,
                "more_body": chunk_index < len(chunks),
            }
        return {"type": "http.disconnect"}

    async def send(message: dict) -> None:
        sent.append(message)

    asyncio.run(application(scope, receive, send))
    start = next(message for message in sent if message["type"] == "http.response.start")
    assert start["status"] == 413
    body_messages = [
        message["body"]
        for message in sent
        if message["type"] == "http.response.body"
    ]
    response_text = b"".join(body_messages).decode()
    assert "payload_too_large" in response_text


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
