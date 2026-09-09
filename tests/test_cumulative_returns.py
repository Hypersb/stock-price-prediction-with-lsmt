import numpy as np
import pandas as pd

from ml.analysis.cumulative import cumulative_returns


def test_cumulative_returns_compound_instead_of_summing() -> None:
    returns = pd.Series([np.nan, 0.1, -0.1])

    result = cumulative_returns(returns)

    assert np.isnan(result.iloc[0])
    assert np.isclose(result.iloc[1], 0.1)
    assert np.isclose(result.iloc[2], -0.01)