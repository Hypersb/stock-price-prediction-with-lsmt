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
    """Bounded historical market-data payload."""

    symbol: str
    start_date: date
    end_date: date
    count: int = Field(ge=0)
    data: list[OhlcvObservation]
