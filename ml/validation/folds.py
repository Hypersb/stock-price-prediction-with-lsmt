"""Deterministic chronological walk-forward fold generation."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml.validation.config import WalkForwardConfig


@dataclass(frozen=True)
class WalkForwardFold:
    """One train, validation, and test temporal partition."""

    fold: int
    train_indices: np.ndarray
    validation_indices: np.ndarray
    test_indices: np.ndarray
    train_dates: pd.DatetimeIndex | None = None
    validation_dates: pd.DatetimeIndex | None = None
    test_dates: pd.DatetimeIndex | None = None


def generate_expanding_folds(
    observation_count: int,
    config: WalkForwardConfig,
    dates: pd.Series | pd.Index | None = None,
) -> list[WalkForwardFold]:
    """Generate expanding folds without shuffling observations."""
    if observation_count <= 0:
        raise ValueError("observation_count must be positive")
    date_index = _dates(dates, observation_count)
    folds: list[WalkForwardFold] = []
    fold_number = 1
    train_end = config.initial_train_size
    while True:
        validation_start = train_end + config.gap
        validation_end = validation_start + config.validation_size
        test_start = validation_end + config.gap
        test_end = test_start + config.test_size
        if test_end > observation_count:
            break
        folds.append(
            _make_fold(
                fold_number,
                np.arange(0, train_end),
                np.arange(validation_start, validation_end),
                np.arange(test_start, test_end),
                date_index,
            )
        )
        fold_number += 1
        train_end += config.step_size
    if not folds:
        raise ValueError("observation_count cannot produce a complete fold")
    return folds


def generate_rolling_folds(
    observation_count: int,
    config: WalkForwardConfig,
    dates: pd.Series | pd.Index | None = None,
) -> list[WalkForwardFold]:
    """Generate fixed-length rolling training windows."""
    if config.window_type != "rolling":
        raise ValueError("rolling fold generation requires rolling configuration")
    date_index = _dates(dates, observation_count)
    folds: list[WalkForwardFold] = []
    train_start = 0
    fold_number = 1
    while True:
        train_end = train_start + config.maximum_train_size
        validation_start = train_end + config.gap
        validation_end = validation_start + config.validation_size
        test_start = validation_end + config.gap
        test_end = test_start + config.test_size
        if test_end > observation_count:
            break
        folds.append(
            _make_fold(
                fold_number,
                np.arange(train_start, train_end),
                np.arange(validation_start, validation_end),
                np.arange(test_start, test_end),
                date_index,
            )
        )
        fold_number += 1
        train_start += config.step_size
    if not folds:
        raise ValueError("observation_count cannot produce a complete fold")
    return folds


def _dates(dates: pd.Series | pd.Index | None, count: int) -> pd.DatetimeIndex | None:
    if dates is None:
        return None
    parsed = pd.DatetimeIndex(pd.to_datetime(dates, errors="coerce"))
    if len(parsed) != count or parsed.isna().any() or parsed.has_duplicates or not parsed.is_monotonic_increasing:
        raise ValueError("dates must be valid, unique, and chronological")
    return parsed


def _make_fold(
    number: int,
    train: np.ndarray,
    validation: np.ndarray,
    test: np.ndarray,
    dates: pd.DatetimeIndex | None,
) -> WalkForwardFold:
    return WalkForwardFold(
        number,
        train,
        validation,
        test,
        None if dates is None else dates[train],
        None if dates is None else dates[validation],
        None if dates is None else dates[test],
    )