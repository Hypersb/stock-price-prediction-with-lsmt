import pandas as pd

from ml.backtesting.execution import align_execution


def test_execution_uses_future_return_not_same_date_return() -> None:
    signals = pd.DataFrame({"date": pd.to_datetime(["2020-01-01"]), "signal": [1]})
    returns = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
            "realized_return": [0.99, 0.10, -0.10],
        }
    )

    result = align_execution(signals, returns)

    assert result.loc[0, "prediction_date"] == pd.Timestamp("2020-01-01")
    assert result.loc[0, "realization_date"] == pd.Timestamp("2020-01-02")
    assert result.loc[0, "realized_return"] == 0.10