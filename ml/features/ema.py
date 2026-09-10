"""Exponential moving-average trend features."""

from collections.abc import Iterable

import pandas as pd


def exponential_moving_average_features(
    close: pd.Series,
    spans: Iterable[int],
) -> pd.DataFrame:
    """Calculate trailing EMAs with pandas ``adjust=False`` convention."""
    if not isinstance(close, pd.Series):
        raise TypeError("close must be a pandas Series")
    if close.isna().any() or (close <= 0).any():
        raise ValueError("close values must be positive and non-missing")
    normalized_spans = _validate_spans(spans)
    result: dict[str, pd.Series] = {}
    for span in normalized_spans:
        ema = close.ewm(span=span, adjust=False, min_periods=span).mean()
        result[f"ema_{span}"] = ema
        result[f"close_to_ema_{span}"] = close / ema - 1
    return pd.DataFrame(result, index=close.index)


def _validate_spans(spans: Iterable[int]) -> tuple[int, ...]:
    normalized = tuple(spans)
    if any(isinstance(span, bool) or not isinstance(span, int) or span <= 0 for span in normalized):
        raise ValueError("spans must contain positive integers")
    if len(set(normalized)) != len(normalized):
        raise ValueError("spans must not contain duplicates")
    return normalized