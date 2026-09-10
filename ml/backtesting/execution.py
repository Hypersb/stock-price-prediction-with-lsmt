"""Align prediction-time signals with future realized returns."""

import pandas as pd


def align_execution(
    signals: pd.DataFrame,
    market_returns: pd.DataFrame,
    *,
    forecast_horizon: int = 1,
) -> pd.DataFrame:
    """Map prediction date t to the return observed on the next date.

    The first market-return row after a prediction date is the realized period;
    same-date returns are never assigned to a prediction. Only one-day horizon
    is supported until overlapping multi-day accounting is specified.
    """
    if forecast_horizon != 1:
        raise ValueError("execution alignment currently supports forecast_horizon=1 only")
    required_signal = {"date", "signal"}
    required_returns = {"date", "realized_return"}
    if not required_signal.issubset(signals.columns) or not required_returns.issubset(market_returns.columns):
        raise ValueError("signals and market_returns have missing required columns")
    predictions = signals.copy()
    returns = market_returns.copy()
    predictions["prediction_date"] = pd.to_datetime(predictions["date"])
    returns["realization_date"] = pd.to_datetime(returns["date"])
    if returns["realization_date"].duplicated().any() or not returns["realization_date"].is_monotonic_increasing:
        raise ValueError("market returns must have unique chronological dates")
    return pd.merge_asof(
        predictions.sort_values("prediction_date"),
        returns[["realization_date", "realized_return"]].sort_values("realization_date"),
        left_on="prediction_date",
        right_on="realization_date",
        direction="forward",
        allow_exact_matches=False,
    ).dropna(subset=["realization_date", "realized_return"])