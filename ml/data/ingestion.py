"""Orchestration for validating, retrieving, normalizing, and storing data."""

import pandas as pd

from ml.data.normalize import normalize_ohlcv
from ml.data.provider import DateLike, MarketDataProvider
from ml.data.requests import MarketDataRequest
from ml.data.storage import HistoricalDataStore
from ml.data.validation import validate_ohlcv


class MarketDataIngestionService:
    """Coordinate market-data ingestion through an injected provider."""

    def __init__(
        self,
        provider: MarketDataProvider,
        store: HistoricalDataStore | None = None,
    ) -> None:
        self.provider = provider
        self.store = store

    def ingest(
        self,
        symbol: str,
        start_date: DateLike,
        end_date: DateLike,
        *,
        persist: bool = False,
    ) -> pd.DataFrame:
        """Retrieve and validate data, optionally persisting the result."""
        request = MarketDataRequest.create(symbol, start_date, end_date)
        raw_data = self.provider.get_historical_data(
            request.symbol, request.start_date, request.end_date
        )
        if isinstance(raw_data, pd.DataFrame) and raw_data.empty:
            validate_ohlcv(raw_data)
        normalized_data = normalize_ohlcv(raw_data)
        validate_ohlcv(normalized_data)

        if persist:
            if self.store is None:
                raise ValueError("a data store is required when persist is true")
            self.store.save(request.symbol, normalized_data)
        return normalized_data