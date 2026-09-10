"""Environment-driven backend configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


def _parse_origins(raw: str) -> list[str]:
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    app_env: str = "development"
    app_name: str = "stock-price-prediction-research-api"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = field(
        default_factory=lambda: ["GET", "POST", "OPTIONS"]
    )
    cors_allow_headers: list[str] = field(
        default_factory=lambda: ["Authorization", "Content-Type", "X-Request-ID"]
    )
    max_market_data_days: int = 3650
    max_feature_rows: int = 500
    database_url: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once from the process environment."""
    app_env = os.getenv("APP_ENV", "development").strip().lower() or "development"
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "").strip()
    cors_origins_raw = os.getenv("CORS_ORIGINS", "").strip()

    if cors_origins_raw:
        origins = _parse_origins(cors_origins_raw)
    elif frontend_origin:
        origins = [frontend_origin]
    elif app_env == "development":
        origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    else:
        origins = []

    return Settings(
        app_env=app_env,
        app_name=os.getenv("APP_NAME", "stock-price-prediction-research-api").strip()
        or "stock-price-prediction-research-api",
        app_version=os.getenv("APP_VERSION", "0.1.0").strip() or "0.1.0",
        api_v1_prefix=os.getenv("API_V1_PREFIX", "/api/v1").strip() or "/api/v1",
        cors_origins=origins,
        cors_allow_credentials=os.getenv(
            "CORS_ALLOW_CREDENTIALS", "true"
        ).strip().lower()
        in {"1", "true", "yes"},
        max_market_data_days=int(os.getenv("MAX_MARKET_DATA_DAYS", "3650")),
        max_feature_rows=int(os.getenv("MAX_FEATURE_ROWS", "500")),
        database_url=os.getenv("DATABASE_URL", "").strip(),
    )


def clear_settings_cache() -> None:
    """Reset cached settings (useful in tests)."""
    get_settings.cache_clear()
