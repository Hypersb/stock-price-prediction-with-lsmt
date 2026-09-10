"""Aggregate version-1 API routers."""

from fastapi import APIRouter

from backend.app.api.v1 import analysis, health, market_data

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(market_data.router)
api_router.include_router(analysis.router)
