from datetime import date

from backend.app.db.base import Base
from backend.app.db.metrics import normalize_metric_value
from backend.app.db.models import (
    BacktestEquityPoint,
    BacktestMetric,
    BacktestRun,
)
from backend.app.db.session import build_database


def test_backtest_run_persists_metrics_and_equity_points() -> None:
    database = build_database("sqlite:///:memory:")
    Base.metadata.create_all(database.engine)

    with database.create_session() as session:
        run = BacktestRun(
            symbol="AAPL",
            model_name="oos_model",
            task="regression",
            strategy_mode="long_only",
            signal_threshold=0.0,
            transaction_cost_bps=10.0,
            slippage_bps=1.0,
            initial_capital=1.0,
            start_date=date(2020, 1, 2),
            end_date=date(2020, 1, 4),
            observation_count=3,
            sample_kind="out_of_sample",
        )
        session.add(run)
        session.flush()
        session.add_all(
            [
                BacktestMetric(
                    backtest_id=run.id,
                    metric_name="sharpe_ratio",
                    metric_value=normalize_metric_value(1.2),
                ),
                BacktestMetric(
                    backtest_id=run.id,
                    metric_name="maximum_drawdown",
                    metric_value=normalize_metric_value(float("-inf")),
                ),
                BacktestEquityPoint(
                    backtest_id=run.id,
                    date=date(2020, 1, 2),
                    position=1.0,
                    gross_return=0.01,
                    cost=0.0001,
                    net_return=0.0099,
                    equity=1.0099,
                ),
            ]
        )
        session.commit()
        loaded = session.get(BacktestRun, run.id)
        assert loaded is not None
        assert loaded.observation_count == 3
        assert len(loaded.metrics) == 2
        metric_map = {item.metric_name: item.metric_value for item in loaded.metrics}
        assert metric_map["sharpe_ratio"] == 1.2
        assert metric_map["maximum_drawdown"] is None
        assert len(loaded.equity_points) == 1
        assert loaded.equity_points[0].equity == 1.0099

    database.engine.dispose()
