"""Date-aligned correlation analysis for asset return series."""

from collections.abc import Mapping

import pandas as pd


def return_correlation_matrix(returns: Mapping[str, pd.Series]) -> pd.DataFrame:
    """Calculate correlations using only dates shared by all assets.

    Inputs are return series indexed by observation date. Price levels are not
    accepted by this function, and non-overlapping dates are excluded through
    an explicit inner date alignment before correlation is calculated.
    """
    if not returns:
        raise ValueError("returns must contain at least one labeled series")
    if any(not isinstance(label, str) or not label for label in returns):
        raise ValueError("return series labels must be non-empty strings")
    if any(not isinstance(series, pd.Series) for series in returns.values()):
        raise TypeError("returns must map labels to pandas Series")

    aligned = pd.concat(returns, axis=1, join="inner").dropna()
    if aligned.empty:
        raise ValueError("return series have no overlapping observed dates")
    return aligned.corr()