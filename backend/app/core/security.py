"""HTTP security headers and request size safeguards."""

from __future__ import annotations

import re

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.app.core.config import get_settings
from backend.app.schemas.common import ErrorResponse

_TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.\-]{0,15}$")


def validate_ticker_symbol(symbol: str) -> str:
    """Normalize and reject unsafe ticker path values."""
    if not isinstance(symbol, str):
        raise TypeError("symbol must be a string")
    normalized = symbol.strip().upper()
    if not _TICKER_PATTERN.fullmatch(normalized):
        raise ValueError(
            "symbol must be 1-16 characters: letters, digits, '.', or '-'"
        )
    return normalized


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach restrained security headers to every response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        response.headers.setdefault("X-XSS-Protection", "0")
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject oversized request bodies before handlers run."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        settings = get_settings()
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError:
                length = -1
            if length < 0 or length > settings.max_request_body_bytes:
                payload = ErrorResponse(
                    error="payload_too_large",
                    detail=(
                        "request body exceeds configured maximum of "
                        f"{settings.max_request_body_bytes} bytes"
                    ),
                    code="payload_too_large",
                )
                return JSONResponse(status_code=413, content=payload.model_dump())
        return await call_next(request)
