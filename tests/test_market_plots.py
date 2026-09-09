import matplotlib
import pandas as pd

matplotlib.use("Agg")

from ml.visualization.market_plots import (
    plot_close_history,
    plot_cumulative_returns,
    plot_drawdown,
    plot_return_histogram,
    plot_return_history,
    plot_rolling_volatility,
)


def test_market_plot_helpers_return_labeled_figures() -> None:
    dates = pd.date_range("2020-01-01", periods=3, freq="D")
    data = pd.DataFrame({"date": dates, "close": [100, 101, 102]})
    series = pd.Series([None, 0.01, 0.02], index=dates)

    plots = [
        plot_close_history(data),
        plot_return_history(series),
        plot_cumulative_returns(series),
        plot_rolling_volatility(series),
        plot_drawdown(series),
        plot_return_histogram(series),
    ]

    assert all(figure.axes for figure, _ in plots)
    assert plots[0][1].get_ylabel() == "Close price"

    for figure, _ in plots:
        figure.clear()