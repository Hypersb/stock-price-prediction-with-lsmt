"""Chronological supervised-dataset splitting."""

from dataclasses import dataclass

from ml.dataset import SupervisedFrame


@dataclass(frozen=True)
class TemporalSplit:
    """Contiguous train, validation, and test datasets."""

    train: SupervisedFrame
    validation: SupervisedFrame
    test: SupervisedFrame


def chronological_split(
    frame: SupervisedFrame,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
    test_fraction: float = 0.15,
    *,
    forecast_horizon: int = 0,
) -> TemporalSplit:
    """Split oldest observations first without shuffling.

    When ``forecast_horizon`` > 0, purge partition tails so that a label at
    index ``t`` depending on ``t + horizon`` cannot reach a later partition
    (same rule as walk-forward ``purge_fold``). Default ``forecast_horizon=0``
    preserves historical unpurged single-split behavior (TD-003).
    """
    fractions = (train_fraction, validation_fraction, test_fraction)
    if any(fraction <= 0 for fraction in fractions) or abs(sum(fractions) - 1.0) > 1e-9:
        raise ValueError("split fractions must be positive and sum to 1")
    if forecast_horizon < 0:
        raise ValueError("forecast_horizon must be nonnegative")
    row_count = len(frame.X)
    train_end = int(row_count * train_fraction)
    validation_end = train_end + int(row_count * validation_fraction)
    if train_end <= 0 or validation_end <= train_end or validation_end >= row_count:
        raise ValueError("dataset is too small for non-empty chronological splits")

    train_stop = train_end
    validation_stop = validation_end
    if forecast_horizon > 0:
        # Drop train rows whose target horizon reaches into validation.
        train_stop = max(0, train_end - forecast_horizon)
        # Drop validation rows whose target horizon reaches into test.
        validation_stop = max(train_end, validation_end - forecast_horizon)
        if train_stop <= 0 or validation_stop <= train_end or validation_stop >= row_count:
            raise ValueError("forecast horizon purged an entire train or validation partition")

    return TemporalSplit(
        train=_slice(frame, 0, train_stop),
        validation=_slice(frame, train_end, validation_stop),
        test=_slice(frame, validation_end, row_count),
    )


def _slice(frame: SupervisedFrame, start: int, stop: int) -> SupervisedFrame:
    return SupervisedFrame(
        X=frame.X.iloc[start:stop].copy(),
        y=frame.y.iloc[start:stop].copy(),
        dates=frame.dates.iloc[start:stop].copy(),
        feature_names=frame.feature_names,
    )
