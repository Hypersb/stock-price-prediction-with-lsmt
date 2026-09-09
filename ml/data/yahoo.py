"""Yahoo Finance implementation of the market-data provider interface."""

from collections.abc import Hashable

import pandas as pd
import yfinance as yf

from ml.data.provider import DateLike, MarketDataProvider
from ml.data.schema import REQUIRED_COLUMNS


class YahooFinanceProvider(MarketDataProvider):
    """Retrieve historical OHLCV data from Yahoo Finance."""

    def get_historical_data(
        self,
        symbol: str,
        start_date: DateLike,
        end_date: DateLike,
    ) -> pd.DataFrame:
        """Download and shape historical data for one ticker."""
        response = yf.download(
            tickers=symbol,
            start=start_date,
            end=end_date,
            auto_adjust=False,
            progress=False,
        )
        if response.empty:
            return pd.DataFrame(columns=REQUIRED_COLUMNS)

        frame = response.copy()
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)

        frame = frame.rename(columns={column: str(column).lower() for column in frame.columns})
        if "date" not in frame.columns:
            frame.insert(0, "date", frame.index)

        missing = set(REQUIRED_COLUMNS) - set(frame.columns)
        if missing:
            missing_columns = ", ".join(sorted(str(column) for column in missing))
            raise ValueError(f"Yahoo Finance response is missing columns: {missing_columns}")

        return frame.loc[:, REQUIRED_COLUMNS].reset_index(drop=True)


def _is_column_name(value: Hashable) -> bool:
    return isinstance(value, str)