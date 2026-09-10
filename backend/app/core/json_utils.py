"""JSON-safe numeric and date conversion helpers."""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd


def to_json_number(value: Any) -> float | int | None:
    """Convert numeric-like values into JSON-safe scalars."""
    if value is None:
        return None
    if isinstance(value, (bool, np.bool_)):
        return int(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return number
    if isinstance(value, (np.number,)):
        return to_json_number(value.item())
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    raise TypeError(f"unsupported numeric value: {type(value)!r}")


def to_iso_date(value: Any) -> str:
    """Convert date-like values to ISO-8601 calendar dates."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    timestamp = pd.Timestamp(value)
    if pd.isna(timestamp):
        raise ValueError("invalid date value")
    return timestamp.date().isoformat()


def sanitize_mapping(data: dict[str, Any]) -> dict[str, Any]:
    """Replace non-finite floats in a flat mapping with null."""
    sanitized: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, (float, np.floating, int, np.integer, np.bool_)):
            sanitized[key] = to_json_number(value)
        else:
            sanitized[key] = value
    return sanitized
