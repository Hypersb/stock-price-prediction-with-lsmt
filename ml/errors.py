"""Domain-layer exceptions for the quantitative research engine.

These are infrastructure-agnostic. HTTP mapping remains in ``backend.app.core.errors``.
Keep this hierarchy small — Prompt 8 owns broader error/observability architecture.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for research-domain failures."""


class DataProviderError(DomainError):
    """External market-data provider failed or returned unusable payload."""


class DataValidationError(DomainError, ValueError):
    """Domain data violated an explicit schema or temporal contract."""


class ModelError(DomainError):
    """Model fit/predict/load failed."""


class EvaluationError(DomainError):
    """Metric evaluation failed due to invalid inputs."""


class BacktestError(DomainError, ValueError):
    """Strategy backtest configuration or alignment failed."""


class ArtifactError(DomainError):
    """Artifact path/metadata contract failed."""
