"""Local persistence for normalized historical market data."""

import os
import re
from pathlib import Path

import pandas as pd

from ml.data.normalize import normalize_ohlcv


def default_raw_data_directory() -> Path:
    """Resolve the default CSV store under QUANT_DATA_ROOT or repo ``data/raw``."""
    override = os.getenv("QUANT_DATA_ROOT", "").strip()
    if override:
        root = Path(override)
        if not root.is_absolute():
            root = Path(__file__).resolve().parents[2] / root
        return (root / "raw").resolve()
    return (Path(__file__).resolve().parents[2] / "data" / "raw").resolve()


DEFAULT_RAW_DATA_DIRECTORY = default_raw_data_directory()


class HistoricalDataStore:
    """Save and load historical data as CSV files under one directory."""

    def __init__(self, directory: Path | str | None = None) -> None:
        self.directory = (
            Path(directory) if directory is not None else default_raw_data_directory()
        )
        self.directory.mkdir(parents=True, exist_ok=True)
        self.directory = self.directory.resolve()

    def save(self, symbol: str, data: pd.DataFrame) -> Path:
        """Normalize and save data, returning its deterministic path."""
        path = self._path_for(symbol)
        normalized = normalize_ohlcv(data)
        normalized.to_csv(path, index=False)
        return path

    def load(self, symbol: str) -> pd.DataFrame:
        """Load one symbol's CSV and restore its datetime column."""
        path = self._path_for(symbol)
        if not path.exists():
            raise FileNotFoundError(f"historical data file does not exist: {path}")
        data = pd.read_csv(path, parse_dates=["date"])
        return normalize_ohlcv(data)

    def _path_for(self, symbol: str) -> Path:
        normalized_symbol = _safe_symbol(symbol)
        path = (self.directory / f"{normalized_symbol}.csv").resolve()
        if path.parent != self.directory:
            raise ValueError("symbol resolves outside the historical data directory")
        return path


def _safe_symbol(symbol: str) -> str:
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("symbol must be provided for persistence")
    normalized = re.sub(r"[^A-Z0-9._-]", "_", symbol.strip().upper())
    return normalized or "unknown"
