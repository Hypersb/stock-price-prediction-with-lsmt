"""Normalization of provider responses into the internal OHLCV format."""

import pandas as pd

from ml.data.schema import REQUIRED_COLUMNS


def normalize_ohlcv(data: pd.DataFrame) -> pd.DataFrame:
    """Return deterministic, chronologically ordered OHLCV columns."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("market data must be a pandas DataFrame")

    frame = data.copy()
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    if "date" not in frame.columns:
        if isinstance(frame.index, pd.DatetimeIndex):
            frame.insert(0, "date", frame.index)
        else:
            raise ValueError("market data must contain a date column or DatetimeIndex")

    missing_columns = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing_columns:
        columns = ", ".join(sorted(missing_columns))
        raise ValueError(f"market data is missing required columns: {columns}")

    frame = frame.loc[:, REQUIRED_COLUMNS]
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for column in ("open", "high", "low", "close", "volume"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    return frame.sort_values("date", kind="stable").reset_index(drop=True)