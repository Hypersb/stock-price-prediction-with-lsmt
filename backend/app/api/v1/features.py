"""Feature engineering HTTP routes."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.core.errors import BadRequestError
from backend.app.core.security import validate_ticker_symbol
from backend.app.dependencies import get_feature_service
from backend.app.schemas.features import FeatureResponse
from backend.app.services.features import FeatureService
from backend.app.services.market_data import ensure_default_end_date

router = APIRouter(prefix="/features", tags=["features"])


@router.get("/{symbol}", response_model=FeatureResponse)
def get_features(
    symbol: str,
    start_date: Annotated[
        date, Query(description="Inclusive range start (YYYY-MM-DD)")
    ],
    service: Annotated[FeatureService, Depends(get_feature_service)],
    end_date: Annotated[
        date | None, Query(description="Exclusive-style range end (YYYY-MM-DD)")
    ] = None,
    limit: Annotated[
        int | None, Query(ge=1, description="Maximum number of feature rows to return")
    ] = None,
) -> FeatureResponse:
    """Return engineered features for research inspection without targets."""
    try:
        safe_symbol = validate_ticker_symbol(symbol)
    except ValueError as exc:
        raise BadRequestError(str(exc)) from exc
    return service.get_features(
        safe_symbol,
        start_date,
        ensure_default_end_date(end_date),
        limit=limit,
    )
