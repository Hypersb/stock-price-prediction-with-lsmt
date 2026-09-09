"""Validation for historical OHLCV data."""

import pandas as pd

from ml.data.schema import REQUIRED_COLUMNS


class MarketDataValidationError(ValueError):
    """Raised when historical market data violates the canonical contract."""


def validate_ohlcv(data: object) -> None:
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