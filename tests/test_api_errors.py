from datetime import date

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from backend.app.core.errors import BadRequestError, NotFoundError
from backend.app.core.json_utils import to_iso_date, to_json_number
from backend.app.main import create_app
from backend.app.schemas.common import DateRangeQuery, MetricValue


def test_date_range_rejects_inverted_bounds() -> None:
    with pytest.raises(ValueError, match="start_date must occur before end_date"):
        DateRangeQuery(start_date=date(2020, 2, 1), end_date=date(2020, 1, 1))


def test_metric_value_sanitizes_non_finite_numbers() -> None:
    assert MetricValue(name="sharpe", value=float("nan")).value is None
    assert MetricValue(name="drawdown", value=float("-inf")).value is None
    assert MetricValue(name="return", value=0.12).value == 0.12


def test_json_helpers_normalize_dates_and_numbers() -> None:
    assert to_iso_date(date(2020, 1, 2)) == "2020-01-02"
    assert to_json_number(float("nan")) is None
    assert to_json_number(float("inf")) is None
    assert to_json_number(1.5) == 1.5


def test_mapped_errors_return_stable_payload_without_traceback() -> None:
    router = APIRouter()

    @router.get("/boom-bad")
    def boom_bad() -> None:
        raise BadRequestError("invalid ticker")

    @router.get("/boom-missing")
    def boom_missing() -> None:
        raise NotFoundError("resource was not found")

    @router.get("/boom-unexpected")
    def boom_unexpected() -> None:
        raise RuntimeError("secret stack detail")

    application = create_app()
    application.include_router(router, prefix="/api/v1")
    client = TestClient(application, raise_server_exceptions=False)

    bad = client.get("/api/v1/boom-bad")
    assert bad.status_code == 400
    assert bad.json() == {
        "error": "bad_request",
        "detail": "invalid ticker",
        "code": "bad_request",
    }

    missing = client.get("/api/v1/boom-missing")
    assert missing.status_code == 404
    assert missing.json()["code"] == "not_found"

    unexpected = client.get("/api/v1/boom-unexpected")
    assert unexpected.status_code == 500
    payload = unexpected.json()
    assert payload["code"] == "internal_error"
    assert "secret stack detail" not in payload["detail"]
    assert "traceback" not in payload["detail"].lower()


def test_validation_errors_use_error_envelope() -> None:
    from datetime import date

    from pydantic import BaseModel

    router = APIRouter()

    class Payload(BaseModel):
        start_date: date
        end_date: date

    @router.post("/validate-dates")
    def validate_dates(payload: Payload) -> dict[str, str]:
        return {"status": "ok"}

    application = create_app()
    application.include_router(router, prefix="/api/v1")
    client = TestClient(application)

    response = client.post("/api/v1/validate-dates", json={"start_date": "not-a-date"})
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] == "validation_error"
    assert payload["code"] == "validation_error"
    assert "traceback" not in payload["detail"].lower()
