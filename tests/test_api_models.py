from datetime import date

from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.main import create_app
from backend.app.schemas.common import TaskType
from backend.app.schemas.models import PredictionPoint
from backend.app.services.models import ModelService, PredictionStore


def build_client(monkeypatch, service: ModelService | None = None) -> TestClient:
    monkeypatch.setenv("APP_ENV", "development")
    clear_settings_cache()
    application = create_app()
    if service is not None:
        application.state.model_service_factory = lambda: service
    return TestClient(application)


def test_list_models_reports_supported_families_as_untrained(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    payload = response.json()
    names = {model["name"] for model in payload["models"]}
    assert names == {
        "naive",
        "linear_regression",
        "logistic_regression",
        "random_forest",
        "gradient_boosting",
        "lstm",
    }
    assert all(model["trained"] is False for model in payload["models"])


def test_predictions_without_artifact_do_not_train(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get(
        "/api/v1/models/lstm/predictions/AAPL",
        params={"task": "regression"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is False
    assert payload["predictions"] == []
    assert "does not train" in payload["message"]


def test_predictions_return_stored_artifact(monkeypatch) -> None:
    store = PredictionStore()
    store.store_predictions(
        "AAPL",
        "linear_regression",
        "regression",
        [
            PredictionPoint(
                prediction_date=date(2020, 1, 2),
                forecast_horizon=1,
                predicted_return=0.01,
            )
        ],
    )
    client = build_client(monkeypatch, ModelService(store=store))
    response = client.get(
        "/api/v1/models/linear_regression/predictions/AAPL",
        params={"task": "regression"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is True
    assert payload["predictions"][0]["predicted_return"] == 0.01


def test_unknown_model_returns_not_found(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get(
        "/api/v1/models/does_not_exist/predictions/AAPL",
        params={"task": "classification"},
    )
    assert response.status_code == 404
