"""Minimal experiment identity contract (not an MLflow platform)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExperimentSpec:
    """Links research inputs for provenance without inventing results."""

    experiment_id: str
    dataset_id: str | None = None
    feature_set_id: str | None = None
    target_definition: str | None = None
    model_name: str | None = None
    split_strategy: str | None = None
    random_seed: int | None = None
    code_version: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.experiment_id.strip():
            raise ValueError("experiment_id must be provided")
