"""Helpers for normalizing research metric values before persistence."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def normalize_metric_value(value: Any) -> float | None:
    """Convert numeric-like values to float, mapping non-finite values to NULL."""
    if value is None:
        return None
    if isinstance(value, (np.floating, np.integer)):
        value = value.item()
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("metric value must be numeric") from exc
    if math.isnan(number) or math.isinf(number):
        return None
    return number
