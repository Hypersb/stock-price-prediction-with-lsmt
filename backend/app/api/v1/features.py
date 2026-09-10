"""Feature engineering HTTP routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from backend.app.dependencies import get_feature_service
from backend.app.schemas.features import FeatureResponse
from backend.app.services.features import FeatureService
from backend.app.services.market_data import ensure_default_end_date

router = APIRouter(prefix="/features", tags=["features"])


@router.get("/{symbol}", response_model=FeatureResponse)
def get_features(
    symbol: str,
    start_date: date = Query(..., description="Inclusive range start (YYYY-MM-DD)"),
    end_date: date | None = Query(
        None, description="Exclusive-style range end (YYYY-MM-DD)"
    ),
    limit: int | None = Query(
        None, ge=1, description="Maximum number of feature rows to return"
    ),
    service: FeatureService = Depends(get_feature_service),
) -> FeatureResponse:
    """Return engineered features for research inspection without targets."""
    return service.get_features(
        symbol,
        start_date,
        ensure_default_end_date(end_date),
        limit=limit,
    )
