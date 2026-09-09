"""Validation and normalization for historical-data requests."""

from dataclasses import dataclass
from datetime import date, datetime

import pandas as pd

from ml.data.provider import DateLike


@dataclass(frozen=True)
class MarketDataRequest:
    """A validated request for one symbol and date range."""

    symbol: str
    start_date: date
    end_date: date

    @classmethod
    def create(
        cls,
        symbol: object,
        start_date: DateLike,
        end_date: DateLike,
    ) -> "MarketDataRequest":
        if not isinstance(symbol, str):
            raise TypeError("symbol must be a string")
        normalized_symbol = symbol.strip().upper()
        if not normalized_symbol:
            raise ValueError("symbol must be provided")

        normalized_start = _parse_date(start_date, "start_date")
        normalized_end = _parse_date(end_date, "end_date")
        if normalized_start >= normalized_end:
            raise ValueError("start_date must occur before end_date")

        return cls(normalized_symbol, normalized_start, normalized_end)


def _parse_date(value: DateLike, field_name: str) -> date:
    if not isinstance(value, (date, datetime, str)):
        raise TypeError(f"{field_name} must be a date, datetime, or ISO date string")
    try:
        timestamp = pd.Timestamp(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid date") from None
    if pd.isna(timestamp):
        raise ValueError(f"{field_name} must be a valid date")
    return timestamp.date()