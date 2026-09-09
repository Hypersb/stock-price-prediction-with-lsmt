import pandas as pd
import pytest

from ml.data.validation import MarketDataValidationError, validate_ohlcv


def valid_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02"],
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "volume": [1000, 1100],
        }
    )


def test_valid_ohlcv_data_passes() -> None:
    validate_ohlcv(valid_data())


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda frame: frame.drop(columns="close"), "missing required columns"),
        (lambda frame: frame.iloc[0:0], "must not be empty"),
        (lambda frame: frame.assign(date=["2020-01-01", "2020-01-01"]), "duplicate dates"),
        (lambda frame: frame.assign(date=["bad-date", "2020-01-02"]), "invalid dates"),
        (lambda frame: frame.assign(volume=[1000, -1]), "volume must not be negative"),
        (lambda frame: frame.assign(close=[100.0, None]), "missing required values"),
        (lambda frame: frame.assign(open=["bad", 101.0]), "'open' must be numeric"),
    ],
)
def test_invalid_ohlcv_data_reports_reason(mutator, message: str) -> None:
    with pytest.raises(MarketDataValidationError, match=message):
        validate_ohlcv(mutator(valid_data()))


def test_non_dataframe_is_rejected() -> None:
    with pytest.raises(MarketDataValidationError, match="pandas DataFrame"):
        validate_ohlcv([])