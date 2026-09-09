from datetime import date

import pandas as pd
import pytest

from ml.data.ingestion import MarketDataIngestionService
from ml.data.provider import MarketDataProvider
from ml.data.storage import HistoricalDataStore
from ml.data.validation import MarketDataValidationError


class FakeProvider(MarketDataProvider):
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.calls: list[tuple[str, date, date]] = []

    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        self.calls.append((symbol, start_date, end_date))
        return self.data


def data_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": ["2020-01-01", "2020-01-02"],
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1000, 1100],
        }
    )


def test_ingestion_injects_provider_and_optionally_persists(tmp_path) -> None:
    provider = FakeProvider(data_frame())
    service = MarketDataIngestionService(provider, HistoricalDataStore(tmp_path))

    result = service.ingest(" aapl ", "2020-01-01", "2020-01-03", persist=True)

    assert provider.calls == [("AAPL", date(2020, 1, 1), date(2020, 1, 3))]
    assert result.loc[0, "close"] == 101.0
    assert (tmp_path / "AAPL.csv").exists()


def test_ingestion_rejects_empty_provider_response() -> None:
    provider = FakeProvider(pd.DataFrame())

    with pytest.raises(MarketDataValidationError, match="must not be empty"):
        MarketDataIngestionService(provider).ingest("AAPL", "2020-01-01", "2020-01-03")


def test_ingestion_requires_store_for_persistence() -> None:
    with pytest.raises(ValueError, match="data store is required"):
        MarketDataIngestionService(FakeProvider(data_frame())).ingest(
            "AAPL", "2020-01-01", "2020-01-03", persist=True
        )