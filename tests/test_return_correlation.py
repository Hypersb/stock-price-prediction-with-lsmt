import numpy as np
import pandas as pd
import pytest

from ml.analysis.correlation import return_correlation_matrix


def test_return_correlation_aligns_by_date() -> None:
    dates_a = pd.date_range("2020-01-01", periods=4, freq="D")
    dates_b = pd.date_range("2020-01-02", periods=4, freq="D")
    returns = {
        "AAPL": pd.Series([0.01, 0.02, 0.03, 0.04], index=dates_a),
        "SPY": pd.Series([0.02, 0.04, 0.06, 0.08], index=dates_b),
    }

    result = return_correlation_matrix(returns)

    assert list(result.columns) == ["AAPL", "SPY"]
    assert np.isclose(result.loc["AAPL", "SPY"], 1.0)


def test_return_correlation_rejects_no_overlap() -> None:
    returns = {
        "AAPL": pd.Series([0.01], index=pd.to_datetime(["2020-01-01"])),
        "QQQ": pd.Series([0.02], index=pd.to_datetime(["2020-01-02"])),
    }

    with pytest.raises(ValueError, match="no overlapping"):
        return_correlation_matrix(returns)