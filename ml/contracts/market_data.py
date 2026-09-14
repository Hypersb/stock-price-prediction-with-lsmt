"""Market-data semantic contract.

CURRENT Yahoo path uses unadjusted OHLCV (``auto_adjust=False``). Optional
``adj_close`` may be present; default research still uses unadjusted ``close``.
Switching research to adjusted prices is a methodological change (TD-001).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from ml.data.schema import OPTIONAL_COLUMNS, REQUIRED_COLUMNS, SCHEMA_VERSION

AdjustmentPolicy = Literal["unadjusted", "adjusted"]

ADJUSTMENT_POLICY_UNADJUSTED: Final[AdjustmentPolicy] = "unadjusted"
ADJUSTMENT_POLICY_ADJUSTED: Final[AdjustmentPolicy] = "adjusted"
OHLCV_REQUIRED_COLUMNS: Final[tuple[str, ...]] = REQUIRED_COLUMNS
OHLCV_OPTIONAL_COLUMNS: Final[tuple[str, ...]] = OPTIONAL_COLUMNS
MARKET_DATA_SCHEMA_VERSION: Final[str] = SCHEMA_VERSION


@dataclass(frozen=True)
class MarketDataSemantics:
    """Explicit semantics for OHLCV frames consumed by research code."""

    required_columns: tuple[str, ...] = OHLCV_REQUIRED_COLUMNS
    optional_columns: tuple[str, ...] = OHLCV_OPTIONAL_COLUMNS
    schema_version: str = MARKET_DATA_SCHEMA_VERSION
    frequency: str = "1d"
    date_column: str = "date"
    # Half-open request ranges: start inclusive, end exclusive at the provider.
    range_convention: str = "half_open_start_inclusive"
    adjustment_policy: AdjustmentPolicy = ADJUSTMENT_POLICY_UNADJUSTED
    timezone_policy: str = "naive_exchange_calendar_date"
    # Research close column under the default unadjusted policy.
    research_price_column: str = "close"

    def assert_columns(self, columns: object) -> None:
        missing = set(self.required_columns) - set(columns)  # type: ignore[arg-type]
        if missing:
            raise ValueError(
                "market data missing required columns: "
                + ", ".join(sorted(str(column) for column in missing))
            )

    def price_column_for_policy(self) -> str:
        if self.adjustment_policy == ADJUSTMENT_POLICY_ADJUSTED:
            return "adj_close"
        return self.research_price_column
