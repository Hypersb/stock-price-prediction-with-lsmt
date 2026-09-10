"""Market-data HTTP routes."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.dependencies import get_market_data_service
from backend.app.schemas.market_data import MarketDataResponse
from backend.app.services.market_data import MarketDataService, ensure_default_end_date

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/{symbol}", response_model=MarketDataResponse)
def get_market_data(
    symbol: str,
    start_date: Annotated[
        date, Query(description="Inclusive range start (YYYY-MM-DD)")
    ],
    service: Annotated[MarketDataService, Depends(get_market_data_service)],
    end_date: Annotated[
        date | None, Query(description="Exclusive-style range end (YYYY-MM-DD)")
    ] = None,
) -> MarketDataResponse:
    """Return validated OHLCV observations for a symbol and date range."""
    return service.get_ohlcv(symbol, start_date, ensure_default_end_date(end_date))
