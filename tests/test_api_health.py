from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache, get_settings
from backend.app.main import create_app


def test_health_endpoint_returns_structured_payload(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("APP_NAME", "research-api")
    monkeypatch.setenv("APP_VERSION", "0.1.0")
    clear_settings_cache()

    client = TestClient(create_app())
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "status": "ok",
        "service": "research-api",
        "version": "0.1.0",
        "environment": "development",
    }
    assert "DATABASE_URL" not in payload
    assert "MARKET_DATA_API_KEY" not in payload


def test_cors_uses_configured_frontend_origin(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://research.example.com")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    clear_settings_cache()

    settings = get_settings()
    assert settings.cors_origins == ["https://research.example.com"]

    client = TestClient(create_app())
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "https://research.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "https://research.example.com"
    )


def test_production_without_origins_does_not_allow_all(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    clear_settings_cache()

    settings = get_settings()
    assert settings.cors_origins == []
