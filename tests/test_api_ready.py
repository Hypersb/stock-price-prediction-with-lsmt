"""Tests for dependency readiness endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.db.session import reset_database
from backend.app.main import create_app


def test_ready_reports_unconfigured_database(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    clear_settings_cache()
    reset_database()

    client = TestClient(create_app())
    response = client.get("/api/v1/ready")

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "not_ready"
    assert payload["checks"]["database"]["status"] == "unconfigured"
    assert "postgresql" not in response.text.lower()
    assert "password" not in response.text.lower()


def test_ready_reports_healthy_database(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "ready.db"
    url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", url)
    clear_settings_cache()
    reset_database()

    with TestClient(create_app()) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["checks"]["database"]["status"] == "ok"
    assert "DATABASE_URL" not in response.text
    reset_database()


def test_ready_reports_unavailable_database(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:////this/path/definitely/does/not/exist/ready.db",
    )
    clear_settings_cache()
    reset_database()

    with TestClient(create_app()) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "not_ready"
    assert payload["checks"]["database"]["status"] == "unavailable"
    assert "DATABASE_URL" not in response.text
    reset_database()
