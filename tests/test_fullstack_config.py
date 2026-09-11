"""Tests for unified full-stack configuration."""

from __future__ import annotations

import pytest

from backend.app.core.config import (
    ConfigurationError,
    clear_settings_cache,
    get_settings,
)


@pytest.fixture(autouse=True)
def _clear_settings() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_development_defaults_are_safe(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = get_settings()

    assert settings.app_env == "development"
    assert settings.require_database is False
    assert settings.database_url == ""
    assert "http://localhost:3000" in settings.cors_origins
    assert settings.max_page_size == 100
    assert settings.default_page_size == 20
    assert settings.market_data_api_key == ""


def test_production_requires_database_url(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://research.example.com")

    with pytest.raises(ConfigurationError, match="DATABASE_URL"):
        get_settings()


def test_production_loads_with_database_and_origin(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:password@db:5432/quant_research",
    )
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://research.example.com")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    settings = get_settings()

    assert settings.is_production is True
    assert settings.require_database is True
    assert settings.cors_origins == ["https://research.example.com"]
    assert settings.database_url.startswith("postgresql+")


def test_invalid_app_env_rejected(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "staging")

    with pytest.raises(ConfigurationError, match="APP_ENV"):
        get_settings()


def test_invalid_limits_rejected(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("MAX_MARKET_DATA_DAYS", "0")

    with pytest.raises(ConfigurationError, match="MAX_MARKET_DATA_DAYS"):
        get_settings()


def test_default_page_size_cannot_exceed_max(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("MAX_PAGE_SIZE", "10")
    monkeypatch.setenv("DEFAULT_PAGE_SIZE", "50")

    with pytest.raises(ConfigurationError, match="DEFAULT_PAGE_SIZE"):
        get_settings()


def test_cors_origins_list_overrides_frontend_origin(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:3000")
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://a.example.com, https://b.example.com",
    )

    settings = get_settings()
    assert settings.cors_origins == [
        "https://a.example.com",
        "https://b.example.com",
    ]
