import pandas as pd

from ml.backtesting.costs import calculate_costs, calculate_turnover


def test_turnover_and_costs_follow_position_changes() -> None:
    positions = pd.Series([0, 1, 1, -1, 0], dtype=float)

    turnover = calculate_turnover(positions)
    costs = calculate_costs(turnover, transaction_cost_bps=10, slippage_bps=5)

    assert turnover.tolist() == [0.0, 1.0, 0.0, 2.0, 1.0]
    assert costs.tolist() == [0.0, 0.0015, 0.0, 0.003, 0.0015]