"""Forecast-horizon purging for walk-forward temporal folds."""

from ml.validation.config import WalkForwardConfig
from ml.validation.folds import WalkForwardFold


def purge_fold(fold: WalkForwardFold, config: WalkForwardConfig) -> WalkForwardFold:
    """Remove partition-tail labels whose future horizon reaches a later partition.

    With target at row ``t`` depending on ``t + horizon``, train rows must end
    before validation starts minus the horizon. Validation rows use the same
    rule relative to test. Existing configured gaps remain between partitions.
    """
    validation_start = int(fold.validation_indices[0])
    test_start = int(fold.test_indices[0])
    train_indices = fold.train_indices[fold.train_indices + config.forecast_horizon < validation_start]
    validation_indices = fold.validation_indices[
        fold.validation_indices + config.forecast_horizon < test_start
    ]
    if len(train_indices) == 0 or len(validation_indices) == 0:
        raise ValueError("forecast horizon purged an entire train or validation partition")
    return WalkForwardFold(
        fold=fold.fold,
        train_indices=train_indices,
        validation_indices=validation_indices,
        test_indices=fold.test_indices.copy(),
        train_dates=None if fold.train_dates is None else fold.train_dates[-len(train_indices) :],
        validation_dates=None if fold.validation_dates is None else fold.validation_dates[: len(validation_indices)],
        test_dates=fold.test_dates,
    )