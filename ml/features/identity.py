"""Feature-set identity helpers for reproducibility."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from ml.contracts.features import FeatureSetSpec


def feature_parameters_id(parameters: Mapping[str, Any]) -> str:
    """Stable short id for a feature-parameter dictionary."""
    payload = json.dumps(parameters, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def build_feature_set_spec(
    feature_names: tuple[str, ...],
    *,
    parameters: Mapping[str, Any],
    lookback_bars: int,
    notes: str = "",
) -> FeatureSetSpec:
    """Create a FeatureSetSpec with a deterministic feature_set_id."""
    feature_set_id = f"fs:{feature_parameters_id(parameters)}"
    return FeatureSetSpec(
        feature_set_id=feature_set_id,
        feature_names=feature_names,
        lookback_bars=lookback_bars,
        notes=notes,
    )
