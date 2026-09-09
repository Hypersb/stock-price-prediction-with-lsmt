"""Interfaces for historical market-data providers."""

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
        """Return historical data for a symbol and half-open date range."""