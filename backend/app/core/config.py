"""Canonical backend configuration for the research API.

Ownership: ``backend.app.core.config`` is the single settings surface for
infrastructure/runtime configuration. Research/experiment parameters (lookback,
horizon, LSTM hyperparameters, walk-forward windows, costs) live in ``ml.*``
config modules and must not be promoted to process environment variables.

Precedence (highest wins):
1. Process environment variables already set
2. Optional repo-root ``.env`` keys (development/test only; never production)
3. Safe environment-specific defaults

Secrets are never included in ``safe_settings_summary()`` or health payloads.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_APP_ENVS = frozenset({"development", "production", "test"})
ALLOWED_LOG_LEVELS = frozenset(
    {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SECRET_ENV_NAMES = frozenset(
    {
        "DATABASE_URL",
        "MARKET_DATA_API_KEY",
        "POSTGRES_PASSWORD",
        "SECRET_KEY",
        "API_KEY",
        "AUTH_API_KEY",
    }
)


class ConfigurationError(ValueError):
    """Raised when environment configuration is invalid."""


def repo_root() -> Path:
    """Return the repository root (stable relative to this module)."""
    return _REPO_ROOT


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


def _parse_positive_float(name: str, raw: str | None, default: float) -> float:
    text = default if raw is None or not str(raw).strip() else str(raw).strip()
    try:
        value = float(text)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{name} must be a number") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} must be positive")
    return value


def _load_dotenv_file(path: Path) -> None:
    """Load KEY=VALUE pairs into os.environ only when the key is unset.

    Minimal parser: ignores comments/blank lines. Does not support export
    prefix expansion or multiline values. Production must never call this.
    """
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ[key] = value


def maybe_load_dotenv() -> None:
    """Optionally load repo-root ``.env`` for local development.

    - production: never
    - test: only when ``QUANT_LOAD_DOTENV=true`` (default off for hermetic tests)
    - development: default on; set ``QUANT_LOAD_DOTENV=false`` to disable
    """
    app_env = os.getenv("APP_ENV", "development").strip().lower() or "development"
    if app_env == "production":
        return
    if app_env == "test":
        if not _parse_bool(os.getenv("QUANT_LOAD_DOTENV", ""), False):
            return
    elif not _parse_bool(os.getenv("QUANT_LOAD_DOTENV", "true"), True):
        return
    _load_dotenv_file(repo_root() / ".env")


def is_local_database_url(database_url: str) -> bool:
    """Return True for sqlite or local/compose database hosts."""
    raw = database_url.strip()
    if not raw:
        return True
    if raw.startswith("sqlite:"):
        return True
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    return host in {"localhost", "127.0.0.1", "::1", "postgres"}


def redact_database_url(database_url: str) -> str:
    """Return a URL safe for diagnostics (password replaced)."""
    raw = database_url.strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    if not parsed.password:
        return f"{parsed.scheme}://{parsed.hostname or 'unknown'}"
    user = parsed.username or ""
    host = parsed.hostname or "unknown"
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{user}:***@{host}{port}"


def classify_database_target(database_url: str) -> str:
    """Classify DB target without exposing credentials."""
    raw = database_url.strip()
    if not raw:
        return "unconfigured"
    if raw.startswith("sqlite:"):
        return "sqlite"
    if is_local_database_url(raw):
        return "local"
    return "remote"


@dataclass(frozen=True)
class Settings:
    """Typed runtime settings for the FastAPI research API.

    Field groups (logical, single object for simple ownership):
    - application: app_env, app_name, app_version, api_v1_prefix, log_level
    - network/CORS: cors_*
    - database: database_url, require_database
    - market data / cache: max_* , market_data_*
    - paths: data_root, artifact_root
    - secrets: database_url credentials, market_data_api_key
    """

    app_env: str = "development"
    app_name: str = "stock-price-prediction-research-api"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    cors_origins: list[str] = field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = field(
        default_factory=lambda: ["GET", "POST", "OPTIONS"]
    )
    cors_allow_headers: list[str] = field(
        default_factory=lambda: [
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-API-Key",
        ]
    )
    max_market_data_days: int = 3650
    max_market_rows: int = 5000
    max_feature_rows: int = 500
    max_page_size: int = 100
    default_page_size: int = 20
    max_request_body_bytes: int = 1_048_576
    market_data_cache_ttl_seconds: float = 60.0
    market_data_cache_max_size: int = 64
    market_data_provider: str = "yahoo"
    database_url: str = ""
    market_data_api_key: str = ""
    auth_api_key: str = ""
    require_database: bool = False
    data_root: str = ""
    artifact_root: str = ""

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_test(self) -> bool:
        return self.app_env == "test"

    def assert_database_configured(self) -> None:
        """Fail when persistence is required but DATABASE_URL is missing."""
        if self.require_database and not self.database_url:
            raise ConfigurationError(
                "DATABASE_URL is required when APP_ENV=production"
            )

    def assert_startup_ready(self) -> None:
        """Validate critical configuration at process startup."""
        self.assert_database_configured()
        if self.is_production and self.cors_allow_credentials and not self.cors_origins:
            # Empty origins with credentials is allowed (no browser clients),
            # but wildcard is never allowed.
            pass
        for origin in self.cors_origins:
            if origin == "*":
                raise ConfigurationError(
                    "CORS origin '*' is not allowed; configure explicit origins"
                )
        if self.cors_allow_credentials and "*" in self.cors_origins:
            raise ConfigurationError(
                "CORS credentials cannot be enabled with wildcard origins"
            )

    def safe_settings_summary(self) -> dict[str, object]:
        """Non-secret operator diagnostics for local/CLI use."""
        return {
            "app_env": self.app_env,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "api_v1_prefix": self.api_v1_prefix,
            "log_level": self.log_level,
            "cors_origins": list(self.cors_origins),
            "cors_allow_credentials": self.cors_allow_credentials,
            "database_configured": bool(self.database_url),
            "database_target": classify_database_target(self.database_url),
            "require_database": self.require_database,
            "market_data_provider": self.market_data_provider,
            "market_data_api_key_configured": bool(self.market_data_api_key),
            "auth_api_key_configured": bool(self.auth_api_key),
            "market_data_cache_ttl_seconds": self.market_data_cache_ttl_seconds,
            "market_data_cache_max_size": self.market_data_cache_max_size,
            "max_market_data_days": self.max_market_data_days,
            "max_page_size": self.max_page_size,
            "default_page_size": self.default_page_size,
            "data_root": self.data_root,
            "artifact_root": self.artifact_root,
        }


def _default_log_level(app_env: str) -> str:
    if app_env == "development":
        return "DEBUG"
    return "INFO"


def _validate_cors(app_env: str, origins: list[str], allow_credentials: bool) -> None:
    if "*" in origins:
        raise ConfigurationError(
            "CORS origin '*' is not allowed; configure explicit origins"
        )
    if allow_credentials and "*" in origins:
        raise ConfigurationError(
            "CORS credentials cannot be enabled with wildcard origins"
        )
    if app_env == "production" and allow_credentials and not origins:
        # Explicit empty list is permitted (non-browser clients). Documented.
        return
    for origin in origins:
        if not re.match(r"^https?://", origin):
            raise ConfigurationError(
                "CORS origins must be absolute http(s) origins"
            )


def _assert_test_database_safety(app_env: str, database_url: str) -> None:
    if app_env != "test" or not database_url:
        return
    if is_local_database_url(database_url):
        return
    allow = _parse_bool(os.getenv("ALLOW_NONLOCAL_TEST_DATABASE", ""), False)
    if allow:
        return
    raise ConfigurationError(
        "APP_ENV=test refuses non-local DATABASE_URL; "
        "set ALLOW_NONLOCAL_TEST_DATABASE=true only for intentional integration runs"
    )


def _resolve_path(raw: str | None, default: Path) -> str:
    text = (raw or "").strip()
    if not text:
        return str(default)
    path = Path(text)
    if not path.is_absolute():
        path = repo_root() / path
    return str(path.resolve())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and validate settings once from the process environment."""
    maybe_load_dotenv()

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

    allow_credentials = _parse_bool(
        os.getenv("CORS_ALLOW_CREDENTIALS", "true"), True
    )
    _validate_cors(app_env, origins, allow_credentials)

    api_prefix = os.getenv("API_V1_PREFIX", "/api/v1").strip() or "/api/v1"
    if not api_prefix.startswith("/"):
        raise ConfigurationError("API_V1_PREFIX must start with '/'")

    database_url = os.getenv("DATABASE_URL", "").strip()
    require_database = app_env == "production"
    if require_database and not database_url:
        raise ConfigurationError(
            "DATABASE_URL is required when APP_ENV=production"
        )
    _assert_test_database_safety(app_env, database_url)

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

    log_level_raw = (
        os.getenv("LOG_LEVEL", _default_log_level(app_env)).strip().upper()
        or _default_log_level(app_env)
    )
    if log_level_raw not in ALLOWED_LOG_LEVELS:
        raise ConfigurationError(
            f"LOG_LEVEL must be one of {sorted(ALLOWED_LOG_LEVELS)}"
        )

    provider = os.getenv("MARKET_DATA_PROVIDER", "yahoo").strip().lower() or "yahoo"
    if provider != "yahoo":
        raise ConfigurationError(
            "MARKET_DATA_PROVIDER only supports 'yahoo' in this phase"
        )

    data_root = _resolve_path(
        os.getenv("QUANT_DATA_ROOT"), repo_root() / "data"
    )
    artifact_root = _resolve_path(
        os.getenv("QUANT_ARTIFACT_ROOT"), repo_root() / "artifacts"
    )

    settings = Settings(
        app_env=app_env,
        app_name=os.getenv("APP_NAME", "stock-price-prediction-research-api").strip()
        or "stock-price-prediction-research-api",
        app_version=os.getenv("APP_VERSION", "0.1.0").strip() or "0.1.0",
        api_v1_prefix=api_prefix,
        log_level=log_level_raw,
        cors_origins=origins,
        cors_allow_credentials=allow_credentials,
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
        max_request_body_bytes=_parse_positive_int(
            "MAX_REQUEST_BODY_BYTES",
            os.getenv("MAX_REQUEST_BODY_BYTES"),
            1_048_576,
        ),
        market_data_cache_ttl_seconds=_parse_positive_float(
            "MARKET_DATA_CACHE_TTL_SECONDS",
            os.getenv("MARKET_DATA_CACHE_TTL_SECONDS"),
            60.0,
        ),
        market_data_cache_max_size=_parse_positive_int(
            "MARKET_DATA_CACHE_MAX_SIZE",
            os.getenv("MARKET_DATA_CACHE_MAX_SIZE"),
            64,
        ),
        market_data_provider=provider,
        database_url=database_url,
        market_data_api_key=os.getenv("MARKET_DATA_API_KEY", "").strip(),
        auth_api_key=os.getenv("AUTH_API_KEY", "").strip(),
        require_database=require_database,
        data_root=data_root,
        artifact_root=artifact_root,
    )
    settings.assert_startup_ready()
    return settings


def clear_settings_cache() -> None:
    """Reset cached settings (useful in tests)."""
    get_settings.cache_clear()


def assert_summary_has_no_secrets(summary: dict[str, object]) -> None:
    """Raise ConfigurationError if a diagnostics payload looks secret-bearing."""
    if "database_url" in summary:
        raise ConfigurationError("safe summary must not include database_url")
    if "market_data_api_key" in summary:
        raise ConfigurationError("safe summary must not include api key field")
    if "auth_api_key" in summary:
        raise ConfigurationError("safe summary must not include auth api key field")
    for name in _SECRET_ENV_NAMES:
        if name.lower() in {str(key).lower() for key in summary}:
            raise ConfigurationError(f"safe summary must not include {name}")
    blob = " ".join(f"{key}={value}" for key, value in summary.items()).lower()
    for marker in (
        "password=",
        "api_key=",
        "auth_api_key=",
        "secret_key=",
        "postgresql+",
        "postgres://",
    ):
        if marker in blob:
            raise ConfigurationError("safe summary appears to contain secrets")
