"""HTTP security headers and request size safeguards."""

from __future__ import annotations

import re

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from backend.app.core.config import get_settings
from backend.app.schemas.common import ErrorResponse
from ml.data.symbols import normalize_symbol

_TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.\-]{0,15}$")


def validate_ticker_symbol(symbol: str) -> str:
    """Normalize and reject unsafe ticker path values.

    Normalization uses the shared research contract in ``ml.data.symbols``.
    HTTP path safety additionally requires an allow-list pattern (letters,
    digits, ``.``, ``-``). Indices such as ``^GSPC`` are valid research symbols
    but are rejected at the HTTP boundary until a dedicated quote-path design
    exists.
    """
    normalized = normalize_symbol(symbol)
    if not _TICKER_PATTERN.fullmatch(normalized):
        raise ValueError(
            "symbol must be 1-16 characters: letters, digits, '.', or '-'"
        )
    return normalized


def _payload_too_large_response(max_bytes: int) -> JSONResponse:
    payload = ErrorResponse(
        error="payload_too_large",
        detail=(
            "request body exceeds configured maximum of "
            f"{max_bytes} bytes"
        ),
        code="payload_too_large",
    )
    return JSONResponse(status_code=413, content=payload.model_dump())


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


class RequestSizeLimitMiddleware:
    """Reject oversized request bodies before handlers run.

    Implemented as pure ASGI middleware so the buffered body can be replayed
    safely. Content-Length is checked when present for an early reject, and the
    body is always streamed with a running byte count so chunked transfer or
    missing Content-Length cannot bypass ``max_request_body_bytes``.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        settings = get_settings()
        max_bytes = settings.max_request_body_bytes
        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        content_length = headers.get("content-length")
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError:
                length = -1
            if length < 0 or length > max_bytes:
                response = _payload_too_large_response(max_bytes)
                await response(scope, receive, send)
                return

        body = bytearray()
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] != "http.request":
                # Unexpected disconnect / lifecycle message — stop buffering.
                more_body = False
                continue
            chunk = message.get("body", b"")
            if chunk:
                body.extend(chunk)
            if len(body) > max_bytes:
                response = _payload_too_large_response(max_bytes)
                await response(scope, receive, send)
                return
            more_body = bool(message.get("more_body", False))

        body_bytes = bytes(body)
        body_sent = False

        async def replay_receive() -> Message:
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {
                    "type": "http.request",
                    "body": body_bytes,
                    "more_body": False,
                }
            return {"type": "http.request", "body": b"", "more_body": False}

        await self.app(scope, replay_receive, send)
