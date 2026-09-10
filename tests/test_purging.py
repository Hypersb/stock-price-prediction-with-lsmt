import pytest

from ml.validation.config import WalkForwardConfig
from ml.validation.folds import generate_expanding_folds
from ml.validation.purging import purge_fold


@pytest.mark.parametrize("horizon, expected_train, expected_validation", [(1, 4, 1), (5, 0, 0)])
def test_purging_removes_horizon_unsafe_partition_tails(horizon, expected_train, expected_validation) -> None:
    config = WalkForwardConfig(
        initial_train_size=5,
        validation_size=2,
        test_size=2,
        step_size=1,
        forecast_horizon=horizon,
    )
    fold = generate_expanding_folds(9, config)[0]

    if expected_train == 0:
        with pytest.raises(ValueError, match="entire"):
            purge_fold(fold, config)
        return
    purged = purge_fold(fold, config)
    assert len(purged.train_indices) == expected_train
    assert len(purged.validation_indices) == expected_validation
    assert purged.train_indices[-1] + horizon < purged.validation_indices[0]


def test_configured_gap_is_preserved_by_fold_generation() -> None:
    config = WalkForwardConfig(initial_train_size=4, validation_size=2, test_size=2, step_size=1, gap=2)
    fold = generate_expanding_folds(12, config)[0]

    assert fold.validation_indices[0] - fold.train_indices[-1] == 3
    assert fold.test_indices[0] - fold.validation_indices[-1] == 3