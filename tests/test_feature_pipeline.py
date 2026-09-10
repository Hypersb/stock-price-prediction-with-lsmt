import numpy as np
import pandas as pd

from ml.features.pipeline import build_features


def ohlcv(rows: int = 40) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    close = np.arange(100.0, 100.0 + rows)
    return pd.DataFrame(
        {
            "date": dates,
            "open": close - 0.5,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": np.arange(1000, 1000 + rows),
        }
    )


def test_feature_pipeline_preserves_data_and_expected_columns() -> None:
    source = ohlcv()

    result = build_features(
        source,
        return_lags=(1,),
        momentum_windows=(2,),
        moving_average_windows=(2,),
        ema_spans=(2,),
        volatility_windows=(2,),
        volume_window=2,
        rsi_period=3,
        macd_fast=2,
        macd_slow=4,
        macd_signal=2,
        atr_period=3,
    )

    expected = {
        "date", "open", "high", "low", "close", "volume", "simple_return",
        "log_return", "return_lag_1", "momentum_2", "sma_2", "close_to_sma_2",
        "ema_2", "close_to_ema_2", "volatility_2", "volume_change", "volume_lag_1",
        "volume_sma_2", "relative_volume_2", "rsi_3", "macd", "macd_signal",
        "macd_histogram", "atr_3",
    }
    assert expected.issubset(result.columns)
    assert result["date"].is_monotonic_increasing
    assert source.equals(ohlcv())