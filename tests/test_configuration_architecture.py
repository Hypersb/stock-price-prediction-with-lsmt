"""Configuration architecture tests for Prompt 3."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.core.config import (
    ConfigurationError,
    assert_summary_has_no_secrets,
    classify_database_target,
    clear_settings_cache,
    get_settings,
    is_local_database_url,
    redact_database_url,
    repo_root,
)


@pytest.fixture(autouse=True)
def _clear() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_repo_root_points_at_repository() -> None:
    assert (repo_root() / "backend" / "app" / "core" / "config.py").is_file()


def test_test_environment_defaults(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setenv("QUANT_LOAD_DOTENV", "false")

    settings = get_settings()
    assert settings.is_test is True
    assert settings.require_database is False
    assert settings.log_level in {"INFO", "DEBUG", "WARNING", "ERROR"}
    assert settings.market_data_provider == "yahoo"
    assert Path(settings.data_root).is_absolute()
    assert Path(settings.artifact_root).is_absolute()


def test_production_rejects_wildcard_cors(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:password@db:5432/quant_research",
    )
    monkeypatch.setenv("CORS_ORIGINS", "*")
    monkeypatch.setenv("CORS_ALLOW_CREDENTIALS", "true")

    with pytest.raises(ConfigurationError, match="CORS"):
        get_settings()


def test_production_rejects_invalid_log_level(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:password@db:5432/quant_research",
    )
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://research.example.com")
    monkeypatch.setenv("LOG_LEVEL", "VERBOSE")

    with pytest.raises(ConfigurationError, match="LOG_LEVEL"):
        get_settings()


def test_test_env_rejects_nonlocal_database(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:password@db.example.com:5432/quant_research",
    )
    monkeypatch.delenv("ALLOW_NONLOCAL_TEST_DATABASE", raising=False)

    with pytest.raises(ConfigurationError, match="non-local DATABASE_URL"):
        get_settings()


def test_test_env_allows_nonlocal_database_with_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:password@db.example.com:5432/quant_research",
    )
    monkeypatch.setenv("ALLOW_NONLOCAL_TEST_DATABASE", "true")

    settings = get_settings()
    assert classify_database_target(settings.database_url) == "remote"


def test_safe_settings_summary_redacts_secrets(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:super-secret@localhost:5432/quant_research",
    )
    monkeypatch.setenv("MARKET_DATA_API_KEY", "secret-token-value")
    monkeypatch.setenv("QUANT_LOAD_DOTENV", "false")

    settings = get_settings()
    summary = settings.safe_settings_summary()
    assert_summary_has_no_secrets(summary)
    assert summary["database_configured"] is True
    assert summary["database_target"] == "local"
    assert summary["market_data_api_key_configured"] is True
    blob = str(summary)
    assert "super-secret" not in blob
    assert "secret-token-value" not in blob


def test_redact_database_url_hides_password() -> None:
    redacted = redact_database_url(
        "postgresql+psycopg://user:super-secret@localhost:5432/db"
    )
    assert "super-secret" not in redacted
    assert "***" in redacted


def test_is_local_database_url_helpers() -> None:
    assert is_local_database_url("sqlite:///:memory:")
    assert is_local_database_url(
        "postgresql+psycopg://user:password@localhost:5432/quant_research"
    )
    assert is_local_database_url(
        "postgresql+psycopg://user:password@postgres:5432/quant_research"
    )
    assert not is_local_database_url(
        "postgresql+psycopg://user:password@db.example.com:5432/quant_research"
    )


def test_dotenv_not_loaded_in_production(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:password@db:5432/quant_research",
    )
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://research.example.com")
    # Even if a key is only in a file, production path skips dotenv.
    monkeypatch.delenv("APP_NAME", raising=False)
    settings = get_settings()
    assert settings.app_name == "stock-price-prediction-research-api"
