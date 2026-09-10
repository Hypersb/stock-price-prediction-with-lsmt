"""Shared Pydantic schemas for the research API."""

from __future__ import annotations

import math
from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class TaskType(str, Enum):
    """Supported supervised learning task types."""

    REGRESSION = "regression"
    CLASSIFICATION = "classification"


class StrategyMode(str, Enum):
    """Supported research strategy modes."""

    LONG_ONLY = "long_only"
    LONG_SHORT = "long_short"


class ErrorResponse(BaseModel):
    """Stable error payload returned by API exception handlers."""

    error: str
    detail: str
    code: str | None = None


class DateRangeQuery(BaseModel):
    """Validated inclusive-style calendar range for research queries."""

    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_order(self) -> DateRangeQuery:
        if self.start_date >= self.end_date:
            raise ValueError("start_date must occur before end_date")
        return self


class ModelIdentifier(BaseModel):
    """Logical model family identifier for research metadata."""

    name: str = Field(min_length=1, max_length=64)
    family: str = Field(min_length=1, max_length=64)
    task: TaskType | None = None
    trained: bool = False


class MetricValue(BaseModel):
    """Named quantitative metric with a JSON-safe numeric value."""

    name: str
    value: float | None = None

    @field_validator("value", mode="before")
    @classmethod
    def sanitize_numeric(cls, value: Any) -> float | None:
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("metric value must be numeric") from exc
        if math.isnan(number) or math.isinf(number):
            return None
        return number


class PaginationMeta(BaseModel):
    """Optional pagination metadata for bounded list responses."""

    limit: int = Field(ge=1)
    offset: int = Field(ge=0, default=0)
    total: int = Field(ge=0)
    returned: int = Field(ge=0)
