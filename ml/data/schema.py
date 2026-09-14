"""Canonical schema for historical daily market data.

Required OHLCV columns for research frames. CURRENT provider path uses
unadjusted closes (see ``ml.contracts.market_data.ADJUSTMENT_POLICY_UNADJUSTED``
and TD-001). Adjusted-close is not part of the required schema today.
"""

from typing import Final

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
)
