"""Validation for historical OHLCV data."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ml.data.schema import OPTIONAL_COLUMNS, REQUIRED_COLUMNS
from ml.errors import DataValidationError


class MarketDataValidationError(DataValidationError):
    """Raised when historical market data violates the canonical contract."""


@dataclass(frozen=True)
class MarketDataQualityReport:
    """Non-fatal quality observations for operators and research notes."""

    row_count: int
    large_gap_dates: tuple[str, ...]
    max_gap_days: int
    warnings: tuple[str, ...]


def validate_ohlcv(data: object, *, strict_ohlc: bool = True) -> None:
    """Validate an OHLCV frame without changing its values."""
    if not isinstance(data, pd.DataFrame):
        raise MarketDataValidationError("market data must be a pandas DataFrame")
    if data.empty:
        raise MarketDataValidationError("market data must not be empty")

    missing_columns = set(REQUIRED_COLUMNS) - set(data.columns)
    if missing_columns:
        columns = ", ".join(sorted(missing_columns))
        raise MarketDataValidationError(f"market data is missing required columns: {columns}")
    if data[list(REQUIRED_COLUMNS)].isna().any().any():
        raise MarketDataValidationError("market data contains missing required values")

    parsed_dates = pd.to_datetime(data["date"], errors="coerce")
    if parsed_dates.isna().any():
        raise MarketDataValidationError("market data contains invalid dates")
    if parsed_dates.duplicated().any():
        raise MarketDataValidationError("market data contains duplicate dates")
    if not parsed_dates.is_monotonic_increasing:
        raise MarketDataValidationError("market data dates must be chronological")

    for column in ("open", "high", "low", "close", "volume"):
        numeric_values = pd.to_numeric(data[column], errors="coerce")
        if numeric_values.isna().any():
            raise MarketDataValidationError(f"market data column '{column}' must be numeric")
    if (pd.to_numeric(data["volume"]) < 0).any():
        raise MarketDataValidationError("market data volume must not be negative")

    opens = pd.to_numeric(data["open"])
    highs = pd.to_numeric(data["high"])
    lows = pd.to_numeric(data["low"])
    closes = pd.to_numeric(data["close"])
    if (opens <= 0).any() or (highs <= 0).any() or (lows <= 0).any() or (closes <= 0).any():
        raise MarketDataValidationError("market data prices must be positive")

    if strict_ohlc:
        if (highs < opens).any() or (highs < closes).any() or (highs < lows).any():
            raise MarketDataValidationError("market data high must be >= open, close, and low")
        if (lows > opens).any() or (lows > closes).any():
            raise MarketDataValidationError("market data low must be <= open and close")

    if "adj_close" in data.columns:
        adj = pd.to_numeric(data["adj_close"], errors="coerce")
        if adj.isna().any():
            raise MarketDataValidationError("market data column 'adj_close' must be numeric when present")
        if (adj <= 0).any():
            raise MarketDataValidationError("market data adj_close must be positive when present")


def assess_market_data_quality(
    data: pd.DataFrame,
    *,
    large_gap_days: int = 10,
) -> MarketDataQualityReport:
    """Return soft quality diagnostics (gaps) without failing hard validation."""
    validate_ohlcv(data)
    dates = pd.to_datetime(data["date"]).sort_values()
    deltas = dates.diff().dt.days.dropna()
    large_mask = deltas > large_gap_days
    gap_dates = tuple(
        dates.iloc[i].date().isoformat()
        for i, flag in enumerate(large_mask, start=1)
        if bool(flag)
    )
    max_gap = int(deltas.max()) if len(deltas) else 0
    warnings: list[str] = []
    if gap_dates:
        warnings.append(
            f"{len(gap_dates)} calendar gap(s) exceed {large_gap_days} days "
            f"(max_gap_days={max_gap})"
        )
    unused_optional = [name for name in OPTIONAL_COLUMNS if name not in data.columns]
    if unused_optional:
        warnings.append("optional columns absent: " + ", ".join(unused_optional))
    return MarketDataQualityReport(
        row_count=len(data),
        large_gap_dates=gap_dates,
        max_gap_days=max_gap,
        warnings=tuple(warnings),
    )
