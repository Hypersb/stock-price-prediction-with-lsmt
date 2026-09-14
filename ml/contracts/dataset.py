"""Minimal research dataset identity contract (provenance-ready)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DatasetSpec:
    """Logical identity for a research OHLCV/feature-ready dataset.

    This is a contract object for reproducibility — not a database table.
    Optional fields remain unset until a run legitimately populates them.
    """

    dataset_id: str
    symbol: str
    provider: str
    start_date: date
    end_date: date
    frequency: str = "1d"
    classification: str = "raw"  # raw | derived
    adjustment_policy: str = "unadjusted"
    feature_set_id: str | None = None
    target_definition: str | None = None
    source_metadata: str | None = None

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must be provided")
        if not self.symbol.strip():
            raise ValueError("symbol must be provided")
        if self.start_date >= self.end_date:
            raise ValueError("start_date must occur before end_date")
        if self.classification not in {"raw", "derived"}:
            raise ValueError("classification must be 'raw' or 'derived'")
