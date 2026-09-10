"""Lightweight request observability middleware."""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.app.core.logging import get_logger

logger = get_logger("backend.api")

_SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request id and emit safe access logs."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = (time.perf_counter() - started) * 1000
            status_code = response.status_code if response is not None else 500
            logger.info(
                "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
                request_id,
                request.method,
                request.url.path,
                status_code,
                duration_ms,
            )
            if response is not None:
                response.headers["X-Request-ID"] = request_id


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Drop sensitive header values from diagnostic payloads."""
    return {
        key: ("[redacted]" if key.lower() in _SENSITIVE_HEADERS else value)
        for key, value in headers.items()
    }
