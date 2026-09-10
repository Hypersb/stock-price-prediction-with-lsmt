"""Quantitative analysis response schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class AnalysisSummaryResponse(BaseModel):
    """Serializable research summary for one symbol."""

    symbol: str
    start_date: date
    end_date: date
    observation_count: int = Field(ge=0)
    return_count: int = Field(ge=0)
    mean_return: float | None = None
    median_return: float | None = None
    volatility: float | None = None
    cumulative_return: float | None = None
    maximum_drawdown: float | None = None
