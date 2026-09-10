"""FastAPI application factory for the quantitative research backend."""

from fastapi import FastAPI

APP_TITLE = "Stock Price Prediction Research API"
APP_DESCRIPTION = (
    "HTTP API boundary for the quantitative finance and machine learning "
    "research platform. Routes delegate to existing domain services."
)
APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    return FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
    )


app = create_app()
