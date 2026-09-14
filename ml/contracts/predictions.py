"""Canonical prediction record for provenance-ready OOS outputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class PredictionRecord:
    """One out-of-sample prediction row.

    Optional fields remain optional until a legitimate run populates them.
    Do not invent metric or experiment identifiers.
    """

    symbol: str | None
    model_name: str
    prediction_date: date
    target_date: date | None
    horizon: int | None
    predicted: float
    actual: float | None = None
    fold: int | None = None
    task: str | None = None
    probability: float | None = None
    experiment_id: str | None = None
    model_version: str | None = None
    extras: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.model_name.strip():
            raise ValueError("model_name must be provided")
        if self.horizon is not None and self.horizon <= 0:
            raise ValueError("horizon must be positive when provided")
