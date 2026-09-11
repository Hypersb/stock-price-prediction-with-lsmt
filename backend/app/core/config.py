"""Environment-driven full-stack backend configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

ALLOWED_APP_ENVS = frozenset({"development", "production", "test"})


class ConfigurationError(ValueError):
    """Raised when environment configuration is invalid."""


def _parse_origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _parse_bool(raw: str, default: bool) -> bool:
    value = raw.strip().lower()
    if not value:
        return default
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"invalid boolean value: {raw!r}")


def _parse_positive_int(name: str, raw: str | None, default: int) -> int:
    text = default if raw is None or not str(raw).strip() else str(raw).strip()
    try:
        value = int(text)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} must be a positive integer")
    return value


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables.

    Secrets such as DATABASE_URL credentials and MARKET_DATA_API_KEY are never
    exposed through API responses. Safe development defaults apply only when
    APP_ENV is development or test.
    """

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
    max_market_rows: int = 5000
    max_feature_rows: int = 500
    max_page_size: int = 100
    default_page_size: int = 20
    max_request_body_bytes: int = 1_048_576
    market_data_cache_ttl_seconds: float = 60.0
    market_data_cache_max_size: int = 64
    database_url: str = ""
    market_data_api_key: str = ""
    require_database: bool = False

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def assert_database_configured(self) -> None:
        """Fail when persistence is required but DATABASE_URL is missing."""
        if self.require_database and not self.database_url:
            raise ConfigurationError(
                "DATABASE_URL is required when APP_ENV=production"
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and validate settings once from the process environment."""
    app_env = os.getenv("APP_ENV", "development").strip().lower() or "development"
    if app_env not in ALLOWED_APP_ENVS:
        raise ConfigurationError(
            f"APP_ENV must be one of {sorted(ALLOWED_APP_ENVS)}, got {app_env!r}"
        )

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "").strip()
    cors_origins_raw = os.getenv("CORS_ORIGINS", "").strip()

    if cors_origins_raw:
        origins = _parse_origins(cors_origins_raw)
    elif frontend_origin:
        origins = [frontend_origin]
    elif app_env in {"development", "test"}:
        origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    else:
        origins = []

    api_prefix = os.getenv("API_V1_PREFIX", "/api/v1").strip() or "/api/v1"
    if not api_prefix.startswith("/"):
        raise ConfigurationError("API_V1_PREFIX must start with '/'")

    database_url = os.getenv("DATABASE_URL", "").strip()
    require_database = app_env == "production"
    if require_database and not database_url:
        raise ConfigurationError(
            "DATABASE_URL is required when APP_ENV=production"
        )

    max_page_size = _parse_positive_int(
        "MAX_PAGE_SIZE", os.getenv("MAX_PAGE_SIZE"), 100
    )
    default_page_size = _parse_positive_int(
        "DEFAULT_PAGE_SIZE", os.getenv("DEFAULT_PAGE_SIZE"), 20
    )
    if default_page_size > max_page_size:
        raise ConfigurationError(
            "DEFAULT_PAGE_SIZE cannot exceed MAX_PAGE_SIZE"
        )
    max_request_body_bytes = _parse_positive_int(
        "MAX_REQUEST_BODY_BYTES", os.getenv("MAX_REQUEST_BODY_BYTES"), 1_048_576
    )
    market_data_cache_ttl_seconds = float(
        os.getenv("MARKET_DATA_CACHE_TTL_SECONDS", "60") or "60"
    )
    if market_data_cache_ttl_seconds <= 0:
        raise ConfigurationError("MARKET_DATA_CACHE_TTL_SECONDS must be positive")
    market_data_cache_max_size = _parse_positive_int(
        "MARKET_DATA_CACHE_MAX_SIZE",
        os.getenv("MARKET_DATA_CACHE_MAX_SIZE"),
        64,
    )

    return Settings(
        app_env=app_env,
        app_name=os.getenv("APP_NAME", "stock-price-prediction-research-api").strip()
        or "stock-price-prediction-research-api",
        app_version=os.getenv("APP_VERSION", "0.1.0").strip() or "0.1.0",
        api_v1_prefix=api_prefix,
        cors_origins=origins,
        cors_allow_credentials=_parse_bool(
            os.getenv("CORS_ALLOW_CREDENTIALS", "true"), True
        ),
        max_market_data_days=_parse_positive_int(
            "MAX_MARKET_DATA_DAYS", os.getenv("MAX_MARKET_DATA_DAYS"), 3650
        ),
        max_market_rows=_parse_positive_int(
            "MAX_MARKET_ROWS", os.getenv("MAX_MARKET_ROWS"), 5000
        ),
        max_feature_rows=_parse_positive_int(
            "MAX_FEATURE_ROWS", os.getenv("MAX_FEATURE_ROWS"), 500
        ),
        max_page_size=max_page_size,
        default_page_size=default_page_size,
        max_request_body_bytes=max_request_body_bytes,
        market_data_cache_ttl_seconds=market_data_cache_ttl_seconds,
        market_data_cache_max_size=market_data_cache_max_size,
        database_url=database_url,
        market_data_api_key=os.getenv("MARKET_DATA_API_KEY", "").strip(),
        require_database=require_database,
    )


def clear_settings_cache() -> None:
    """Reset cached settings (useful in tests)."""
    get_settings.cache_clear()
