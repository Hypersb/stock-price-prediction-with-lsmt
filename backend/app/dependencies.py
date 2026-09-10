"""Shared FastAPI dependencies for the research API."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Request

from backend.app.services.analysis import AnalysisService
from backend.app.services.features import FeatureService
from backend.app.services.market_data import MarketDataService, default_market_data_service


def get_market_data_service(request: Request) -> MarketDataService:
    """Resolve a market-data service, allowing test overrides via app.state."""
    override: Callable[[], MarketDataService] | None = getattr(
        request.app.state, "market_data_service_factory", None
    )
    if override is not None:
        return override()
    return default_market_data_service()


def get_analysis_service(request: Request) -> AnalysisService:
    """Resolve analysis service with optional test overrides."""
    override: Callable[[], AnalysisService] | None = getattr(
        request.app.state, "analysis_service_factory", None
    )
    if override is not None:
        return override()
    return AnalysisService(market_data_service=get_market_data_service(request))


def get_feature_service(request: Request) -> FeatureService:
    """Resolve feature service with optional test overrides."""
    override: Callable[[], FeatureService] | None = getattr(
        request.app.state, "feature_service_factory", None
    )
    if override is not None:
        return override()
    return FeatureService(market_data_service=get_market_data_service(request))
