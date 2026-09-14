"""Normalization of provider responses into the internal OHLCV format."""

import pandas as pd

from ml.data.schema import OPTIONAL_COLUMNS, REQUIRED_COLUMNS


def normalize_ohlcv(data: pd.DataFrame) -> pd.DataFrame:
    """Return deterministic, chronologically ordered OHLCV columns.

    Preserves optional columns such as ``adj_close`` when present. Does not
    invent adjusted prices.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("market data must be a pandas DataFrame")

    frame = data.copy()
    frame.columns = [str(column).strip().lower().replace(" ", "_") for column in frame.columns]
    # Yahoo-style "adj close" → adj_close after space→underscore; also accept adjclose.
    if "adjclose" in frame.columns and "adj_close" not in frame.columns:
        frame = frame.rename(columns={"adjclose": "adj_close"})
    if "date" not in frame.columns:
        if isinstance(frame.index, pd.DatetimeIndex):
            frame.insert(0, "date", frame.index)
        else:
            raise ValueError("market data must contain a date column or DatetimeIndex")

    missing_columns = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing_columns:
        columns = ", ".join(sorted(missing_columns))
        raise ValueError(f"market data is missing required columns: {columns}")

    keep = list(REQUIRED_COLUMNS) + [c for c in OPTIONAL_COLUMNS if c in frame.columns]
    frame = frame.loc[:, keep]
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for column in ("open", "high", "low", "close", "volume"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "adj_close" in frame.columns:
        frame["adj_close"] = pd.to_numeric(frame["adj_close"], errors="coerce")

    return frame.sort_values("date", kind="stable").reset_index(drop=True)
