"""Optional API-key authentication for local single-user deployments.

When ``Settings.auth_api_key`` is empty, auth is disabled (single-user mode):
``require_api_key`` is a no-op. When set, callers must supply the key via the
``X-API-Key`` header (or ``Authorization: Bearer <key>``).

Routes are not globally protected yet — opt in per-endpoint with this dependency.
"""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from backend.app.core.config import Settings, get_settings


def is_auth_enabled(settings: Settings | None = None) -> bool:
    """Return True when an API key is configured."""
    cfg = settings or get_settings()
    return bool(cfg.auth_api_key and cfg.auth_api_key.strip())


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
) -> None:
    """Enforce API key when configured; no-op in single-user mode."""
    settings = get_settings()
    expected = (settings.auth_api_key or "").strip()
    if not expected:
        # Auth disabled — local single-user mode.
        return

    provided = (x_api_key or "").strip()
    if not provided and authorization:
        auth = authorization.strip()
        if auth.lower().startswith("bearer "):
            provided = auth[7:].strip()

    if not provided or provided != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
