"""Canonical schema for historical daily market data."""

from typing import Final

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
)