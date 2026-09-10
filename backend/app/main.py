"""FastAPI application factory for the quantitative research backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import api_router
from backend.app.core.config import get_settings
from backend.app.core.errors import register_exception_handlers

APP_TITLE = "Stock Price Prediction Research API"
APP_DESCRIPTION = (
    "HTTP API boundary for the quantitative finance and machine learning "
    "research platform. Routes delegate to existing domain services."
)
APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()
    application = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=settings.app_version,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    register_exception_handlers(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
