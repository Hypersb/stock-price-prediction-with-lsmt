"""Feature-set identity contract (does not alter feature formulas)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureSetSpec:
    """Named feature configuration for provenance and alignment checks."""

    feature_set_id: str
    feature_names: tuple[str, ...]
    lookback_bars: int
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.feature_set_id.strip():
            raise ValueError("feature_set_id must be provided")
        if not self.feature_names:
            raise ValueError("feature_names must be non-empty")
        if self.lookback_bars < 0:
            raise ValueError("lookback_bars must be non-negative")
        if "date" in self.feature_names:
            raise ValueError("date is not a model feature column")
        forbidden = {"future_return", "direction", "target"}
        exact = forbidden.intersection(self.feature_names)
        if exact:
            raise ValueError(
                f"feature set includes forbidden target-like names: {sorted(exact)}"
            )
