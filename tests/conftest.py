"""Pytest configuration isolation for infrastructure settings.

Ensures ordinary unit tests:
- run under APP_ENV=test by default
- do not inherit ambient MARKET_DATA_API_KEY secrets
- do not inherit non-local DATABASE_URL values from a developer shell
"""

from __future__ import annotations

import os

import pytest

from backend.app.core.config import clear_settings_cache, is_local_database_url


@pytest.fixture(autouse=True)
def _isolate_infrastructure_configuration(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("QUANT_LOAD_DOTENV", "false")

    monkeypatch.delenv("MARKET_DATA_API_KEY", raising=False)

    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url and not is_local_database_url(database_url):
        monkeypatch.delenv("DATABASE_URL", raising=False)

    clear_settings_cache()
    yield
    clear_settings_cache()
