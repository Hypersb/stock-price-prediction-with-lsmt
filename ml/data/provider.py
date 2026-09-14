"""Interfaces for historical market-data providers.

Application and research code should depend on this ABC (or fakes in tests),
not on ``ml.data.yahoo`` / yfinance directly.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime

import pandas as pd

DateLike = date | datetime | str


class MarketDataProvider(ABC):
    """Source-independent contract for retrieving historical market data."""

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: DateLike,
        end_date: DateLike,
    ) -> pd.DataFrame:
        """Return OHLCV rows for a symbol and half-open date range.

        Implementations must return columns defined by ``ml.data.schema.REQUIRED_COLUMNS``
        (or an empty frame with those columns). Network I/O belongs only in adapters.
        """
