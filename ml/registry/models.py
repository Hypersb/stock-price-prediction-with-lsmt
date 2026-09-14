"""Typed model registry records.

Statuses describe registry lifecycle only. ``champion`` must never be claimed
without a verifiable on-disk artifact (enforced by the store).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

ModelStatus = Literal["candidate", "champion", "archived"]


@dataclass(frozen=True)
class ModelRecord:
    """Immutable catalog entry for a registered research model version."""

    model_id: str
    version: str
    algorithm: str
    status: ModelStatus
    experiment_id: str | None = None
    artifact_uri: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    feature_set_id: str | None = None
    dataset_id: str | None = None
    checksum: str | None = None

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id must be non-empty")
        if not self.version.strip():
            raise ValueError("version must be non-empty")
        if not self.algorithm.strip():
            raise ValueError("algorithm must be non-empty")
        if self.status not in {"candidate", "champion", "archived"}:
            raise ValueError(f"invalid status: {self.status!r}")
        # Normalize metrics to float values only (reject fabricated nested blobs).
        clean: dict[str, float] = {}
        for key, value in self.metrics.items():
            clean[str(key)] = float(value)
        object.__setattr__(self, "metrics", clean)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "version": self.version,
            "algorithm": self.algorithm,
            "status": self.status,
            "experiment_id": self.experiment_id,
            "artifact_uri": self.artifact_uri,
            "metrics": dict(self.metrics),
            "created_at": self.created_at.isoformat(),
            "feature_set_id": self.feature_set_id,
            "dataset_id": self.dataset_id,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ModelRecord:
        created_raw = payload.get("created_at")
        if isinstance(created_raw, datetime):
            created_at = created_raw
        elif isinstance(created_raw, str) and created_raw.strip():
            created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        else:
            created_at = datetime.now(timezone.utc)
        return cls(
            model_id=str(payload["model_id"]),
            version=str(payload["version"]),
            algorithm=str(payload["algorithm"]),
            status=payload["status"],  # type: ignore[arg-type]
            experiment_id=_optional_str(payload.get("experiment_id")),
            artifact_uri=_optional_str(payload.get("artifact_uri")),
            metrics=dict(payload.get("metrics") or {}),
            created_at=created_at,
            feature_set_id=_optional_str(payload.get("feature_set_id")),
            dataset_id=_optional_str(payload.get("dataset_id")),
            checksum=_optional_str(payload.get("checksum")),
        )


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
