"""Portfolio and position dataclasses (research analytics only)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Position:
    """Single symbol position with a non-negative market value weight basis."""

    symbol: str
    quantity: float
    price: float
    return_: float | None = None

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()
        if not symbol:
            raise ValueError("symbol must be non-empty")
        object.__setattr__(self, "symbol", symbol)
        if self.quantity < 0:
            raise ValueError("quantity must be non-negative")
        if self.price < 0:
            raise ValueError("price must be non-negative")

    @property
    def market_value(self) -> float:
        return float(self.quantity * self.price)


@dataclass(frozen=True)
class Portfolio:
    """Collection of positions for simple analytics (not a brokerage account)."""

    positions: tuple[Position, ...] = field(default_factory=tuple)
    name: str = "default"

    def __post_init__(self) -> None:
        object.__setattr__(self, "positions", tuple(self.positions))

    @property
    def total_value(self) -> float:
        return float(sum(p.market_value for p in self.positions))
