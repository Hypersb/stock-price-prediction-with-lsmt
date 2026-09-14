"""Canonical research symbol normalization.

API path validation (character allow-list) lives in
``backend.app.core.security.validate_ticker_symbol`` and builds on this helper.
Filesystem-safe names for CSV storage may further sanitize characters and must
not be confused with the research symbol identity.
"""

from __future__ import annotations


def normalize_symbol(symbol: object) -> str:
    """Return a stripped, uppercased symbol identity.

    Preserves characters such as ``.``, ``-``, and ``^`` so provider-specific
    tickers (for example ``BRK-B``, ``BRK.B``, ``BTC-USD``, ``^GSPC``) are not
    rewritten — only whitespace is trimmed and case is normalized.
    """
    if not isinstance(symbol, str):
        raise TypeError("symbol must be a string")
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("symbol must be provided")
    return normalized
