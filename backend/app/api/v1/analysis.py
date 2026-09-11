"""Quantitative analysis HTTP routes."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.core.errors import BadRequestError
from backend.app.core.security import validate_ticker_symbol
from backend.app.dependencies import get_analysis_service
from backend.app.schemas.analysis import AnalysisSummaryResponse
from backend.app.services.analysis import AnalysisService
from backend.app.services.market_data import ensure_default_end_date

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/{symbol}/summary", response_model=AnalysisSummaryResponse)
def get_analysis_summary(
    symbol: str,
    start_date: Annotated[
        date, Query(description="Inclusive range start (YYYY-MM-DD)")
    ],
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
    end_date: Annotated[
        date | None, Query(description="Exclusive-style range end (YYYY-MM-DD)")
    ] = None,
) -> AnalysisSummaryResponse:
    """Return key quantitative statistics for a symbol and date range."""
    try:
        safe_symbol = validate_ticker_symbol(symbol)
    except ValueError as exc:
        raise BadRequestError(str(exc)) from exc
    return service.summarize(
        safe_symbol, start_date, ensure_default_end_date(end_date)
    )
