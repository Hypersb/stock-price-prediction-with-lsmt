"""Instrument metadata helpers (non-provider-specific)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ml.data.symbols import normalize_symbol

InstrumentKind = Literal["equity", "etf", "index", "crypto", "other"]


@dataclass(frozen=True)
class InstrumentRef:
    """Normalized instrument identity for research requests."""

    symbol: str
    kind: InstrumentKind
    display_symbol: str

    @staticmethod
    def from_symbol(raw: str) -> InstrumentRef:
        symbol = normalize_symbol(raw)
        kind = classify_instrument(symbol)
        return InstrumentRef(symbol=symbol, kind=kind, display_symbol=symbol)


def classify_instrument(symbol: str) -> InstrumentKind:
    """Best-effort classification without assuming every ticker is a US equity."""
    key = normalize_symbol(symbol)
    if key.startswith("^"):
        return "index"
    if key.endswith(("-USD", "-USDT")):
        return "crypto"
    # Common US ETF heuristic — not exhaustive; unknown → equity/other.
    known_etfs = {"SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "IVV"}
    if key in known_etfs:
        return "etf"
    if not key:
        return "other"
    return "equity"
