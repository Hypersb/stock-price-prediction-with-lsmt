"""Market-data request and response schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class OhlcvObservation(BaseModel):
    """Single JSON-friendly OHLCV bar."""

    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketDataResponse(BaseModel):
    """Bounded historical market-data payload with explicit pagination metadata."""

    symbol: str
    start_date: date
    end_date: date
    total: int = Field(ge=0, description="Total observations in the requested range")
    count: int = Field(ge=0, description="Returned observation count (same as returned)")
    limit: int = Field(ge=1)
    offset: int = Field(ge=0, default=0)
    returned: int = Field(ge=0)
    data: list[OhlcvObservation]
