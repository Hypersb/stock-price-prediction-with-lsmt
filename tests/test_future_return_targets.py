import numpy as np
import pandas as pd
import pytest

from ml.targets.returns import future_return_targets


def test_future_return_targets_use_only_explicit_future_target_logic() -> None:
    close = pd.Series([100.0, 110.0, 121.0, 133.1])

    result = future_return_targets(close, [1, 2])

    assert np.isclose(result.loc[0, "future_return_1"], 0.1)
    assert np.isclose(result.loc[0, "future_return_2"], 0.21)
    assert np.isclose(result.loc[1, "future_return_1"], 0.1)
    assert pd.isna(result["future_return_1"].iloc[-1])
    assert result["future_return_2"].iloc[-2:].isna().all()
    assert close.tolist() == [100.0, 110.0, 121.0, 133.1]


@pytest.mark.parametrize("horizons", [[0], [-1], [True], [1, 1]])
def test_future_return_targets_reject_invalid_horizons(horizons) -> None:
    with pytest.raises(ValueError):
        future_return_targets(pd.Series([100.0]), horizons)