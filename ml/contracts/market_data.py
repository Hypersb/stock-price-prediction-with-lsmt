"""Market-data semantic contract.

CURRENT Yahoo path uses unadjusted OHLCV (``auto_adjust=False``). Switching to
adjusted prices is a methodological change tracked as TD-001 — not done here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from ml.data.schema import REQUIRED_COLUMNS

AdjustmentPolicy = Literal["unadjusted", "adjusted"]

ADJUSTMENT_POLICY_UNADJUSTED: Final[AdjustmentPolicy] = "unadjusted"
OHLCV_REQUIRED_COLUMNS: Final[tuple[str, ...]] = REQUIRED_COLUMNS


@dataclass(frozen=True)
class MarketDataSemantics:
    """Explicit semantics for OHLCV frames consumed by research code."""

    required_columns: tuple[str, ...] = OHLCV_REQUIRED_COLUMNS
    frequency: str = "1d"
    date_column: str = "date"
    # Half-open request ranges: start inclusive, end exclusive at the provider.
    range_convention: str = "half_open_start_inclusive"
    adjustment_policy: AdjustmentPolicy = ADJUSTMENT_POLICY_UNADJUSTED
    timezone_policy: str = "naive_exchange_calendar_date"

    def assert_columns(self, columns: object) -> None:
        missing = set(self.required_columns) - set(columns)  # type: ignore[arg-type]
        if missing:
            raise ValueError(
                "market data missing required columns: "
                + ", ".join(sorted(str(column) for column in missing))
            )
