"""Tests for optional API-key auth dependency."""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.app.core.auth import is_auth_enabled, require_api_key
from backend.app.core.config import clear_settings_cache


@pytest.fixture(autouse=True)
def _clear_settings() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


def _protected_app() -> FastAPI:
    application = FastAPI()

    @application.get("/protected")
    async def protected(_: None = Depends(require_api_key)):
        return {"ok": True}

    return application


def test_auth_disabled_when_key_unset(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("QUANT_LOAD_DOTENV", "false")
    monkeypatch.delenv("AUTH_API_KEY", raising=False)
    clear_settings_cache()
    assert is_auth_enabled() is False

    client = TestClient(_protected_app())
    response = client.get("/protected")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_auth_requires_matching_key(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("QUANT_LOAD_DOTENV", "false")
    monkeypatch.setenv("AUTH_API_KEY", "test-secret-key")
    clear_settings_cache()
    assert is_auth_enabled() is True

    client = TestClient(_protected_app())
    denied = client.get("/protected")
    assert denied.status_code == 401

    allowed = client.get("/protected", headers={"X-API-Key": "test-secret-key"})
    assert allowed.status_code == 200
    assert allowed.json() == {"ok": True}
