import numpy as np
import pandas as pd

from ml.supervised import build_supervised_dataset


def ohlcv(rows: int = 80) -> pd.DataFrame:
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


def parameters() -> dict[str, object]:
    return {
        "return_lags": (1,),
        "momentum_windows": (2,),
        "moving_average_windows": (2,),
        "ema_spans": (2,),
        "volatility_windows": (2,),
        "volume_window": 2,
        "rsi_period": 3,
        "macd_fast": 2,
        "macd_slow": 4,
        "macd_signal": 2,
        "atr_period": 3,
    }


def test_supervised_pipeline_returns_scaled_chronological_regression_data() -> None:
    result = build_supervised_dataset(ohlcv(), feature_parameters=parameters())

    assert result.metadata["target_type"] == "regression"
    assert "future_return_1" not in result.feature_names
    assert len(result.X_train) == len(result.y_train) == len(result.dates_train)
    assert result.dates_train.iloc[-1] < result.dates_validation.iloc[0]
    assert result.dates_validation.iloc[-1] < result.dates_test.iloc[0]
    assert np.isclose(result.X_train.mean().mean(), 0.0)


def test_supervised_pipeline_supports_direction_targets() -> None:
    result = build_supervised_dataset(
        ohlcv(), target_type="direction", horizon=2, feature_parameters=parameters()
    )

    assert result.metadata["horizon"] == 2
    assert set(result.y_train.unique()).issubset({0, 1})