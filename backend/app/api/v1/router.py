"""Aggregate version-1 API routers."""

from fastapi import APIRouter

from backend.app.api.v1 import (
    analysis,
    backtests,
    features,
    health,
    market_data,
    models,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(market_data.router)
api_router.include_router(analysis.router)
api_router.include_router(features.router)
api_router.include_router(models.router)
api_router.include_router(backtests.router)
