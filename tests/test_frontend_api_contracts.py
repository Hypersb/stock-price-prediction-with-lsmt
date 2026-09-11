"""Verify OpenAPI stays aligned with the Next.js API client contracts."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.contracts.frontend_api import FRONTEND_API_CONTRACTS
from backend.app.core.config import clear_settings_cache
from backend.app.main import create_app


def _openapi(monkeypatch) -> dict:
    monkeypatch.setenv("APP_ENV", "development")
    clear_settings_cache()
    client = TestClient(create_app())
    response = client.get("/openapi.json")
    assert response.status_code == 200
    return response.json()


def _schema_properties(openapi: dict, schema_name: str) -> set[str]:
    schemas = openapi["components"]["schemas"]
    assert schema_name in schemas, f"missing schema {schema_name}"
    schema = schemas[schema_name]
    props: set[str] = set(schema.get("properties", {}))
    for ref_key in ("allOf", "anyOf", "oneOf"):
        for item in schema.get(ref_key, []):
            if "$ref" in item:
                nested = item["$ref"].rsplit("/", 1)[-1]
                props |= _schema_properties(openapi, nested)
            props |= set(item.get("properties", {}))
    return props


def test_frontend_consumed_paths_exist_in_openapi(monkeypatch) -> None:
    openapi = _openapi(monkeypatch)
    paths = openapi["paths"]
    for contract in FRONTEND_API_CONTRACTS:
        assert contract.path in paths, f"missing path {contract.path}"
        assert contract.method in paths[contract.path], (
            f"missing method {contract.method.upper()} on {contract.path}"
        )


def test_frontend_response_schemas_include_required_fields(monkeypatch) -> None:
    openapi = _openapi(monkeypatch)
    for contract in FRONTEND_API_CONTRACTS:
        properties = _schema_properties(openapi, contract.response_schema)
        missing = set(contract.required_properties) - properties
        assert not missing, (
            f"{contract.response_schema} missing properties for "
            f"{contract.method.upper()} {contract.path}: {sorted(missing)}"
        )


def test_frontend_query_parameters_are_declared(monkeypatch) -> None:
    openapi = _openapi(monkeypatch)
    for contract in FRONTEND_API_CONTRACTS:
        if not contract.query_parameters:
            continue
        operation = openapi["paths"][contract.path][contract.method]
        declared = {
            parameter["name"]
            for parameter in operation.get("parameters", [])
            if parameter.get("in") == "query"
        }
        missing = set(contract.query_parameters) - declared
        assert not missing, (
            f"missing query params on {contract.path}: {sorted(missing)}"
        )


def test_persistence_list_routes_are_get_not_post_only(monkeypatch) -> None:
    openapi = _openapi(monkeypatch)
    backtests = openapi["paths"]["/api/v1/backtests"]
    assert "get" in backtests
    assert "post" in backtests
    experiments = openapi["paths"]["/api/v1/experiments"]
    assert "get" in experiments
    assert "post" not in experiments
