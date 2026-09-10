import pandas as pd
import pytest

from ml.models.baselines import NaiveDirection


def test_naive_direction_uses_training_labels_only() -> None:
    model = NaiveDirection().fit(pd.DataFrame({"feature": [1, 2]}), pd.Series([0, 0]))

    predictions = model.predict(pd.DataFrame({"feature": [3, 4]}))

    assert predictions.tolist() == [0, 0]


def test_naive_direction_rejects_unusable_labels() -> None:
    with pytest.raises(ValueError, match="binary"):
        NaiveDirection().fit(pd.DataFrame({"feature": [1]}), pd.Series([2]))

    with pytest.raises(ValueError, match="non-empty"):
        NaiveDirection().fit(pd.DataFrame({"feature": [1]}), pd.Series([pd.NA]))