"""Target-definition contract (documents existing methodology)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TargetKind = Literal["future_return", "direction"]


@dataclass(frozen=True)
class TargetSpec:
    """Explicit target semantics for leakage-safe supervised learning."""

    kind: TargetKind
    horizon: int
    column_name: str
    # Direction: 1 iff future_return > 0; flats map to 0; missing stays NA.
    direction_positive_rule: str = "future_return > 0"

    def __post_init__(self) -> None:
        if self.horizon <= 0:
            raise ValueError("horizon must be a positive integer")
        if self.kind == "future_return" and not self.column_name.startswith("future_return_"):
            raise ValueError("future_return targets must use future_return_{h} column names")
        if self.kind == "direction" and "direction" not in self.column_name:
            raise ValueError("direction targets must include 'direction' in the column name")

    @classmethod
    def future_return(cls, horizon: int) -> TargetSpec:
        return cls(kind="future_return", horizon=horizon, column_name=f"future_return_{horizon}")

    @classmethod
    def direction(cls, horizon: int) -> TargetSpec:
        return cls(
            kind="direction",
            horizon=horizon,
            column_name=f"direction_{horizon}",
        )
