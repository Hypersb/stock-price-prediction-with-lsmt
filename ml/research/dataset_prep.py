"""Shared leakage-safe preparation of walk-forward research frames."""

from dataclasses import dataclass

import pandas as pd

from ml.boundaries import prepare_model_ready
from ml.data.validation import validate_ohlcv
from ml.dataset import assemble_supervised
from ml.features.pipeline import build_features
from ml.features.validation import validate_features
from ml.targets.direction import direction_targets
from ml.targets.returns import future_return_targets
from ml.targets.validation import validate_targets


@dataclass(frozen=True)
class ResearchFrame:
    """Model-ready features, target, and dates for one asset."""

    symbol: str
    X: pd.DataFrame
    y: pd.Series
    dates: pd.Series
    feature_names: tuple[str, ...]
    target_column: str
    task: str
    horizon: int
    market_returns: pd.DataFrame


def prepare_research_frame(
    ohlcv: pd.DataFrame,
    *,
    symbol: str,
    target_type: str = "regression",
    horizon: int = 1,
    feature_parameters: dict[str, object] | None = None,
) -> ResearchFrame:
    """Build a comparable supervised frame for one asset without temporal splitting.

    Walk-forward evaluation consumes the full chronological series. Scaling is
    deferred to per-fold preprocessing so training folds never see future rows.
    """
    validate_ohlcv(ohlcv)
    feature_kwargs = feature_parameters or {}
    features = build_features(ohlcv, **feature_kwargs)
    validate_features(features)
    close = ohlcv["close"].reset_index(drop=True)
    dates = ohlcv["date"].reset_index(drop=True)
    if target_type == "regression":
        targets = future_return_targets(close, [horizon])
        target_column = f"future_return_{horizon}"
        task = "regression"
    elif target_type == "direction":
        targets = direction_targets(close, [horizon])
        target_column = f"direction_{horizon}"
        task = "classification"
    else:
        raise ValueError("target_type must be 'regression' or 'direction'")
    validate_targets(targets, target_type, horizon, dates)
    assembled = assemble_supervised(features, targets, target_column, include_ohlcv=False)
    ready = prepare_model_ready(assembled).frame
    simple = features["simple_return"].reset_index(drop=True)
    market_returns = pd.DataFrame(
        {
            "date": pd.to_datetime(features["date"]),
            "realized_return": simple,
        }
    )
    return ResearchFrame(
        symbol=symbol.strip().upper(),
        X=ready.X.reset_index(drop=True),
        y=ready.y.reset_index(drop=True),
        dates=ready.dates.reset_index(drop=True),
        feature_names=ready.feature_names,
        target_column=target_column,
        task=task,
        horizon=horizon,
        market_returns=market_returns,
    )
