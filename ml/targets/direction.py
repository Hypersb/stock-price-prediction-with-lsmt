"""Future-direction classification target construction."""

from collections.abc import Iterable

import pandas as pd

from ml.targets.returns import future_return_targets


def direction_targets(
    close: pd.Series,
    horizons: Iterable[int],
) -> pd.DataFrame:
    """Build binary direction labels from future returns.

    Binary policy when a future return is defined:
    ``1`` if ``future_return > 0``, else ``0`` (flat / non-positive returns are
    class 0 / non-up). Missing future returns remain NA and are not coerced to
    class zero.
    """
    future_returns = future_return_targets(close, horizons)
    return future_returns.gt(0).where(future_returns.notna()).astype("Int64").rename(
        columns=lambda name: name.replace("future_return_", "direction_")
    )