"""Price-basis policies for market data.

CURRENT research default remains unadjusted Yahoo OHLCV (TD-001). Adjusted
prices may be stored alongside raw closes without silently rewriting history.
"""

from __future__ import annotations

from typing import Final, Literal

PriceBasis = Literal["unadjusted", "adjusted_close"]

PRICE_BASIS_UNADJUSTED: Final[PriceBasis] = "unadjusted"
PRICE_BASIS_ADJUSTED_CLOSE: Final[PriceBasis] = "adjusted_close"

DEFAULT_RESEARCH_PRICE_BASIS: Final[PriceBasis] = PRICE_BASIS_UNADJUSTED
