"""JSON filesystem store for model registry metadata.

Never promotes a model to ``champion`` unless ``artifact_uri`` points at an
existing file. Empty registries do not invent trained/champion claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from ml.registry.models import ModelRecord, ModelStatus


class ModelRegistryStore:
    """Read/write ``artifacts/registry/models.json`` (or a custom path)."""

    def __init__(self, path: Path | str | None = None) -> None:
        if path is None:
            # Default: <repo>/artifacts/registry/models.json
            repo_root = Path(__file__).resolve().parents[2]
            path = repo_root / "artifacts" / "registry" / "models.json"
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list_models(self) -> list[ModelRecord]:
        return list(self._load().values())

    def get(self, model_id: str, version: str | None = None) -> ModelRecord | None:
        records = self._load()
        if version is not None:
            return records.get(self._key(model_id, version))
        matches = [r for r in records.values() if r.model_id == model_id]
        if not matches:
            return None
        matches.sort(key=lambda r: r.created_at, reverse=True)
        return matches[0]

    def register(self, record: ModelRecord) -> ModelRecord:
        if record.status == "champion":
            self._assert_champion_artifact(record.artifact_uri)
        records = self._load()
        records[self._key(record.model_id, record.version)] = record
        self._save(records)
        return record

    def set_status(
        self,
        model_id: str,
        version: str,
        status: ModelStatus,
    ) -> ModelRecord:
        records = self._load()
        key = self._key(model_id, version)
        existing = records.get(key)
        if existing is None:
            raise KeyError(f"model not found: {model_id}@{version}")
        if status == "champion":
            self._assert_champion_artifact(existing.artifact_uri)
        updated = ModelRecord(
            model_id=existing.model_id,
            version=existing.version,
            algorithm=existing.algorithm,
            status=status,
            experiment_id=existing.experiment_id,
            artifact_uri=existing.artifact_uri,
            metrics=dict(existing.metrics),
            created_at=existing.created_at,
            feature_set_id=existing.feature_set_id,
            dataset_id=existing.dataset_id,
            checksum=existing.checksum,
        )
        records[key] = updated
        self._save(records)
        return updated

    def artifact_exists(self, artifact_uri: str | None) -> bool:
        if not artifact_uri or not str(artifact_uri).strip():
            return False
        return Path(artifact_uri).expanduser().is_file()

    def algorithms_with_artifacts(self) -> set[str]:
        """Return algorithm names that have at least one existing artifact file."""
        found: set[str] = set()
        for record in self.list_models():
            if self.artifact_exists(record.artifact_uri):
                found.add(record.algorithm.lower())
        return found

    @staticmethod
    def _key(model_id: str, version: str) -> str:
        return f"{model_id}@{version}"

    @staticmethod
    def _assert_champion_artifact(artifact_uri: str | None) -> None:
        if not artifact_uri or not str(artifact_uri).strip():
            raise ValueError(
                "champion status requires artifact_uri pointing to an existing file"
            )
        path = Path(artifact_uri).expanduser()
        if not path.is_file():
            raise ValueError(
                "champion status requires artifact_uri pointing to an existing file"
            )

    def _load(self) -> dict[str, ModelRecord]:
        if not self.path.is_file():
            return {}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if raw is None:
            return {}
        if not isinstance(raw, list):
            raise TypeError("models.json must be a JSON list of records")
        records: dict[str, ModelRecord] = {}
        for item in raw:
            if not isinstance(item, dict):
                raise TypeError("each registry entry must be an object")
            record = ModelRecord.from_dict(item)
            records[self._key(record.model_id, record.version)] = record
        return records

    def _save(self, records: dict[str, ModelRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [record.to_dict() for record in records.values()]
        self.path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
