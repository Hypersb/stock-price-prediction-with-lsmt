"""Canonical schema for historical daily market data.

Required OHLCV columns for research frames. CURRENT default research path uses
unadjusted closes (``ADJUSTMENT_POLICY_UNADJUSTED`` / TD-001).

Optional ``adj_close`` may be present when a provider supplies it. Presence of
``adj_close`` does **not** change the default research price basis — consumers
must opt into adjusted semantics explicitly.
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

OPTIONAL_COLUMNS: Final[tuple[str, ...]] = ("adj_close",)

SCHEMA_VERSION: Final[str] = "v1"
