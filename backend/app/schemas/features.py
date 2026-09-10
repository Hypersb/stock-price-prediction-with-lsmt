"""Feature engineering response schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class FeatureObservation(BaseModel):
    """One date-aligned feature row with JSON-safe values."""

    date: date
    values: dict[str, float | None]


class FeatureResponse(BaseModel):
    """Bounded feature-matrix inspection payload."""

    symbol: str
    start_date: date
    end_date: date
    feature_names: list[str]
    feature_count: int = Field(ge=0)
    observation_count: int = Field(ge=0)
    returned_rows: int = Field(ge=0)
    features: list[FeatureObservation]
