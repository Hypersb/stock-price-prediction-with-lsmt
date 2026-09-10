import pandas as pd

from ml.targets.direction import direction_targets


def test_direction_targets_preserve_binary_convention_and_missing_tail() -> None:
    close = pd.Series([100.0, 110.0, 100.0, 100.0])

    result = direction_targets(close, [1])

    assert result["direction_1"].iloc[:3].tolist() == [1, 0, 0]
    assert pd.isna(result["direction_1"].iloc[3])
    assert str(result["direction_1"].dtype) == "Int64"