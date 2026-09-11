"""Process health and dependency readiness checks."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from backend.app.core.config import Settings, get_settings
from backend.app.core.logging import get_logger
from backend.app.db.session import get_database

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


class HealthResponse(BaseModel):
    """Structured liveness payload without sensitive environment details."""

    status: str = Field(examples=["ok"])
    service: str
    version: str
    environment: str


class DependencyCheck(BaseModel):
    """Single dependency probe result without secrets."""

    status: Literal["ok", "unavailable", "unconfigured"]
    detail: str


class ReadinessResponse(BaseModel):
    """Dependency readiness payload safe for load balancers and operators."""

    status: Literal["ready", "not_ready"]
    service: str
    checks: dict[str, DependencyCheck]


def _check_database(settings: Settings) -> DependencyCheck:
    if not settings.database_url:
        return DependencyCheck(
            status="unconfigured",
            detail="database url is not configured",
        )
    try:
        database = get_database()
        with database.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        logger.warning("readiness_database_unavailable")
        return DependencyCheck(
            status="unavailable",
            detail="database connectivity check failed",
        )
    return DependencyCheck(status="ok", detail="database accepts connections")


@router.get("/health", response_model=HealthResponse)
def get_health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    """Return a lightweight process liveness signal."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessResponse},
    },
)
def get_ready(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ReadinessResponse:
    """Return dependency readiness without exposing credentials or URLs."""
    database_check = _check_database(settings)
    checks = {"database": database_check}
    ready = database_check.status == "ok"
    payload = ReadinessResponse(
        status="ready" if ready else "not_ready",
        service=settings.app_name,
        checks=checks,
    )
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return payload
