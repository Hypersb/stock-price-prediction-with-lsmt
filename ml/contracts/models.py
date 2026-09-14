"""Structural model contract for tabular predictors.

LSTM/torch modules keep their own APIs; walk-forward adapters already wrap them.
This Protocol describes the common baseline ``fit`` / ``predict`` surface.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
import pandas as pd


@runtime_checkable
class Predictor(Protocol):
    """Minimal fit/predict surface used by tabular baseline walk-forward paths."""

    def fit(self, X: pd.DataFrame, y: pd.Series) -> object:
        """Fit using training rows only."""

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Return predictions aligned to ``X`` rows."""
