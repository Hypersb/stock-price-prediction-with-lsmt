import pandas as pd
import pytest

from ml.data.storage import HistoricalDataStore


def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2020-01-02", "2020-01-01"],
            "open": [101.0, 100.0],
            "high": [103.0, 102.0],
            "low": [100.0, 99.0],
            "close": [102.0, 101.0],
            "volume": [1100, 1000],
        }
    )


def test_storage_round_trip_uses_safe_deterministic_csv_path(tmp_path) -> None:
    store = HistoricalDataStore(tmp_path)

    path = store.save(" aapl ", sample_data())
    result = store.load("AAPL")

    assert path == tmp_path.resolve() / "AAPL.csv"
    assert result["date"].tolist() == list(pd.to_datetime(["2020-01-01", "2020-01-02"]))
    assert result["close"].tolist() == [101.0, 102.0]


def test_storage_reports_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="does not exist"):
        HistoricalDataStore(tmp_path).load("AAPL")