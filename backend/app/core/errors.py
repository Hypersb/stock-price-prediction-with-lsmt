"""Application-level API exceptions and FastAPI handlers."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for mapped HTTP API errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "app_error"

    def __init__(self, detail: str, *, code: str | None = None) -> None:
        self.detail = detail
        self.code = code or self.code
        super().__init__(detail)


class BadRequestError(AppError):
    """Client supplied an invalid but syntactically accepted request."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"


class NotFoundError(AppError):
    """Requested research resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(AppError):
    """Request conflicts with current research state."""

    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


def register_exception_handlers(application: FastAPI) -> None:
    """Attach consistent JSON error handlers to the application."""

    @application.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        payload = ErrorResponse(error=exc.code, detail=exc.detail, code=exc.code)
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        payload = ErrorResponse(
            error="validation_error",
            detail="request validation failed",
            code="validation_error",
        )
        # Preserve FastAPI/Pydantic details in a stable envelope field via detail text.
        # Avoid dumping raw exception objects that may contain sensitive internals.
        messages = []
        for error in exc.errors():
            location = ".".join(str(part) for part in error.get("loc", ()))
            messages.append(f"{location}: {error.get('msg', 'invalid')}")
        if messages:
            payload = ErrorResponse(
                error="validation_error",
                detail="; ".join(messages),
                code="validation_error",
            )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=payload.model_dump(),
        )

    @application.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled api error path=%s method=%s",
            request.url.path,
            request.method,
        )
        payload = ErrorResponse(
            error="internal_error",
            detail="an unexpected error occurred",
            code="internal_error",
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=payload.model_dump(),
        )
