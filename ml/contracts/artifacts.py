"""Artifact reference contract for local/filesystem research outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ArtifactKind = Literal[
    "model",
    "predictions",
    "evaluation",
    "backtest",
    "report",
    "figure",
    "checkpoint",
    "other",
]


@dataclass(frozen=True)
class ArtifactRef:
    """Pointer to a research artifact without requiring object storage."""

    artifact_id: str
    kind: ArtifactKind
    path: str
    experiment_id: str | None = None
    content_type: str | None = None

    def __post_init__(self) -> None:
        if not self.artifact_id.strip():
            raise ValueError("artifact_id must be provided")
        if not self.path.strip():
            raise ValueError("path must be provided")
        if self.path.startswith("/Users/") or ":\\" in self.path[:3]:
            # Allow absolute paths, but reject obvious personal-home hardcoding
            # only when it looks like a notebook accident — keep permissive.
            pass
