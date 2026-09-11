"""Configurable research universes for multi-asset evaluation.

The default symbols are an example diversified set only. Callers may supply
any liquid symbols; production research should load provider data separately.
"""

from dataclasses import dataclass

# Example research universe spanning tech, financials, energy, and a broad ETF.
DEFAULT_RESEARCH_UNIVERSE: tuple[str, ...] = ("AAPL", "MSFT", "JPM", "XOM", "SPY")


@dataclass(frozen=True)
class ResearchUniverse:
    """Explicit multi-asset evaluation universe configuration."""

    symbols: tuple[str, ...] = DEFAULT_RESEARCH_UNIVERSE

    def __post_init__(self) -> None:
        if not self.symbols:
            raise ValueError("symbols must not be empty")
        cleaned = tuple(symbol.strip().upper() for symbol in self.symbols)
        if any(not symbol for symbol in cleaned):
            raise ValueError("symbols must be non-empty strings")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("symbols must be unique")
        object.__setattr__(self, "symbols", cleaned)
