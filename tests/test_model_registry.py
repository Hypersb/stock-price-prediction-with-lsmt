"""Tests for filesystem model registry (no fabricated champion/trained)."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.services.models import ModelService
from ml.registry import ModelRecord, ModelRegistryStore


def test_register_and_list(tmp_path: Path) -> None:
    store = ModelRegistryStore(tmp_path / "models.json")
    record = ModelRecord(
        model_id="m1",
        version="1",
        algorithm="lstm",
        status="candidate",
        artifact_uri=None,
        metrics={"mae": 0.1},
    )
    store.register(record)
    assert store.get("m1", "1") is not None
    assert len(store.list_models()) == 1


def test_champion_requires_existing_artifact(tmp_path: Path) -> None:
    store = ModelRegistryStore(tmp_path / "models.json")
    missing = tmp_path / "missing.bin"
    with pytest.raises(ValueError, match="artifact_uri"):
        store.register(
            ModelRecord(
                model_id="m1",
                version="1",
                algorithm="lstm",
                status="champion",
                artifact_uri=str(missing),
            )
        )

    artifact = tmp_path / "weights.bin"
    artifact.write_bytes(b"ok")
    store.register(
        ModelRecord(
            model_id="m1",
            version="1",
            algorithm="lstm",
            status="candidate",
            artifact_uri=str(artifact),
        )
    )
    champ = store.set_status("m1", "1", "champion")
    assert champ.status == "champion"


def test_model_service_trained_only_with_artifact(tmp_path: Path) -> None:
    empty = ModelService(registry=ModelRegistryStore(tmp_path / "empty.json"))
    assert all(m.trained is False for m in empty.list_models().models)

    artifact = tmp_path / "lstm.bin"
    artifact.write_bytes(b"weights")
    store = ModelRegistryStore(tmp_path / "models.json")
    store.register(
        ModelRecord(
            model_id="lstm-run",
            version="1",
            algorithm="lstm",
            status="candidate",
            artifact_uri=str(artifact),
        )
    )
    service = ModelService(registry=store)
    by_name = {m.name: m.trained for m in service.list_models().models}
    assert by_name["lstm"] is True
    assert by_name["naive"] is False
