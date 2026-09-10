"""Future-direction classification target construction."""

from collections.abc import Iterable

import pandas as pd

from ml.targets.returns import future_return_targets


def direction_targets(
    close: pd.Series,
    horizons: Iterable[int],
) -> pd.DataFrame:
    """Return 1 for positive future returns and 0 otherwise.

    Missing future returns remain missing and are not converted to class zero.
    """
    future_returns = future_return_targets(close, horizons)
    return future_returns.gt(0).where(future_returns.notna()).astype("Int64").rename(
        columns=lambda name: name.replace("future_return_", "direction_")
    )