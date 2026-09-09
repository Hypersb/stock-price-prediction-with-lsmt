import numpy as np
import pandas as pd
import pytest

from ml.analysis.statistics import return_statistics


def test_return_statistics_exclude_missing_observations() -> None:
    result = return_statistics(pd.Series([np.nan, 0.01, 0.02, 0.03, 0.04, 0.05]))

    assert result["count"] == 5
    assert np.isclose(result["mean"], 0.03)
    assert result["median"] == 0.03
    assert np.isclose(result["min"], 0.01)
    assert np.isclose(result["max"], 0.05)
    assert np.isfinite(result["skewness"])
    assert np.isfinite(result["kurtosis"])


def test_return_statistics_rejects_no_observations() -> None:
    with pytest.raises(ValueError, match="at least one observed"):
        return_statistics(pd.Series([np.nan]))