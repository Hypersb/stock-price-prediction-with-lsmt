import pandas as pd

from ml.data.normalize import normalize_ohlcv


def test_normalize_ohlcv_standardizes_columns_order_and_dates() -> None:
    source = pd.DataFrame(
        {
            "Close": [102, 101],
            "Volume": [1100, 1000],
            "High": [103, 102],
            "Low": [100, 99],
            "Open": [101, 100],
        },
        index=pd.DatetimeIndex(["2020-01-02", "2020-01-01"]),
    )
    source["Date"] = ["2020-01-02", "2020-01-01"]

    result = normalize_ohlcv(source)

    assert list(result.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert result["date"].tolist() == list(pd.to_datetime(["2020-01-01", "2020-01-02"]))
    assert result.index.tolist() == [0, 1]
    assert result["volume"].dtype.kind in "iu"