import numpy as np
import pandas as pd
import pytest

from ml.analysis.volatility import (
    annualized_rolling_volatility,
    daily_rolling_volatility,
)


def test_daily_and_annualized_volatility() -> None:
    returns = pd.Series([0.01, 0.02, 0.03])

    daily = daily_rolling_volatility(returns, 2)
    annualized = annualized_rolling_volatility(returns, 2, periods_per_year=4)

    expected_daily = np.std([0.01, 0.02], ddof=1)
    assert np.isnan(daily.iloc[0])
    assert np.isclose(daily.iloc[1], expected_daily)
    assert np.isclose(annualized.iloc[1], expected_daily * 2)


def test_volatility_rejects_invalid_annualization_factor() -> None:
    returns = pd.Series([0.01, 0.02])

    with pytest.raises(ValueError, match="periods_per_year must be positive"):
        annualized_rolling_volatility(returns, 2, periods_per_year=0)
