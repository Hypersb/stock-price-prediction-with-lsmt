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
) -> TemporalSplit:
    """Split oldest observations first without shuffling or overlap."""
    fractions = (train_fraction, validation_fraction, test_fraction)
    if any(fraction <= 0 for fraction in fractions) or abs(sum(fractions) - 1.0) > 1e-9:
        raise ValueError("split fractions must be positive and sum to 1")
    row_count = len(frame.X)
    train_end = int(row_count * train_fraction)
    validation_end = train_end + int(row_count * validation_fraction)
    if train_end <= 0 or validation_end <= train_end or validation_end >= row_count:
        raise ValueError("dataset is too small for non-empty chronological splits")

    return TemporalSplit(
        train=_slice(frame, 0, train_end),
        validation=_slice(frame, train_end, validation_end),
        test=_slice(frame, validation_end, row_count),
    )


def _slice(frame: SupervisedFrame, start: int, stop: int) -> SupervisedFrame:
    return SupervisedFrame(
        X=frame.X.iloc[start:stop].copy(),
        y=frame.y.iloc[start:stop].copy(),
        dates=frame.dates.iloc[start:stop].copy(),
        feature_names=frame.feature_names,
    )