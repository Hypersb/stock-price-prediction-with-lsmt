from datetime import date

from fastapi.testclient import TestClient

from backend.app.core.config import clear_settings_cache
from backend.app.main import create_app
from backend.app.services.models import ModelService


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


def test_predictions_service_maps_persisted_rows(monkeypatch) -> None:
    class _Row:
        prediction_date = date(2020, 1, 2)
        predicted_value = 0.01
        predicted_probability = None
        predicted_class = None

    class _Repo:
        def list_filtered(self, **kwargs):
            assert kwargs["symbol"] == "AAPL"
            assert kwargs["model_name"] == "linear_regression"
            return [_Row()]

    service = ModelService(session=object())
    monkeypatch.setattr(
        "backend.app.services.models.PredictionRepository",
        lambda session: _Repo(),
    )
    response = service.get_predictions("AAPL", "linear_regression", task=__import__(
        "backend.app.schemas.common", fromlist=["TaskType"]
    ).TaskType.REGRESSION)
    assert response.available is True
    assert response.predictions[0].predicted_return == 0.01


def test_unknown_model_returns_not_found(monkeypatch) -> None:
    client = build_client(monkeypatch)
    response = client.get(
        "/api/v1/models/does_not_exist/predictions/AAPL",
        params={"task": "classification"},
    )
    assert response.status_code == 404
