"""Matplotlib plots for market prices and quantitative analysis series."""

import matplotlib.pyplot as plt
import pandas as pd


def plot_close_history(data: pd.DataFrame) -> tuple[plt.Figure, plt.Axes]:
    """Plot closing-price history from normalized market data."""
    dates, values = _data_column(data, "close")
    return _line_plot(dates, values, "Closing price", "Close price")


def plot_return_history(returns: pd.Series) -> tuple[plt.Figure, plt.Axes]:
    """Plot a daily-return series."""
    return _line_plot(returns.index, returns, "Daily returns", "Return")


def plot_cumulative_returns(cumulative: pd.Series) -> tuple[plt.Figure, plt.Axes]:
    """Plot cumulative compounded returns."""
    return _line_plot(cumulative.index, cumulative, "Cumulative returns", "Cumulative return")


def plot_rolling_volatility(volatility: pd.Series) -> tuple[plt.Figure, plt.Axes]:
    """Plot rolling volatility."""
    return _line_plot(volatility.index, volatility, "Rolling volatility", "Volatility")


def plot_drawdown(drawdown: pd.Series) -> tuple[plt.Figure, plt.Axes]:
    """Plot drawdown from the running peak."""
    return _line_plot(drawdown.index, drawdown, "Drawdown", "Drawdown")


def plot_return_histogram(
    returns: pd.Series, bins: int = 30
) -> tuple[plt.Figure, plt.Axes]:
    """Plot the observed return distribution without displaying it."""
    figure, axes = plt.subplots()
    axes.hist(returns.dropna(), bins=bins)
    axes.set_title("Return distribution")
    axes.set_xlabel("Return")
    axes.set_ylabel("Frequency")
    figure.autofmt_xdate()
    return figure, axes


def _data_column(data: pd.DataFrame, column: str) -> tuple[pd.Series, pd.Series]:
    if not isinstance(data, pd.DataFrame) or column not in data.columns:
        raise ValueError(f"market data must contain a '{column}' column")
    if "date" not in data.columns:
        raise ValueError("market data must contain a 'date' column")
    return data["date"], data[column]


def _line_plot(
    x_values: pd.Index | pd.Series,
    y_values: pd.Series,
    title: str,
    y_label: str,
) -> tuple[plt.Figure, plt.Axes]:
    figure, axes = plt.subplots()
    axes.plot(x_values, y_values)
    axes.set_title(title)
    axes.set_xlabel("Date")
    axes.set_ylabel(y_label)
    figure.autofmt_xdate()
    return figure, axes