import pandas as pd
import pytest

from ml.data.schema import OPTIONAL_COLUMNS, REQUIRED_COLUMNS
from ml.data.yahoo import YahooFinanceProvider


def test_yahoo_provider_returns_canonical_columns_with_optional_adj_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [101.0],
            "Low": [99.0],
            "Close": [100.5],
            "Adj Close": [100.4],
            "Volume": [1000],
        },
        index=pd.DatetimeIndex(["2020-01-02"], name="Date"),
    )
    monkeypatch.setattr("ml.data.yahoo.yf.download", lambda **kwargs: source)

    result = YahooFinanceProvider().get_historical_data("AAPL", "2020-01-01", "2020-01-03")

    assert tuple(result.columns)[: len(REQUIRED_COLUMNS)] == REQUIRED_COLUMNS
    assert "adj_close" in result.columns
    assert set(OPTIONAL_COLUMNS).issubset(result.columns)
    assert result.loc[0, "close"] == 100.5
    assert result.loc[0, "adj_close"] == 100.4


def test_yahoo_provider_returns_empty_canonical_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ml.data.yahoo.yf.download", lambda **kwargs: pd.DataFrame())

    result = YahooFinanceProvider().get_historical_data("AAPL", "2020-01-01", "2020-01-03")

    assert result.empty
    assert tuple(result.columns) == REQUIRED_COLUMNS
