"""Quantitative analysis application service."""

from __future__ import annotations

from datetime import date

import pandas as pd

from backend.app.core.errors import BadRequestError
from backend.app.core.json_utils import to_json_number
from backend.app.schemas.analysis import AnalysisSummaryResponse
from backend.app.schemas.market_data import MarketDataResponse
from backend.app.services.market_data import MarketDataService
from ml.analysis.cumulative import cumulative_returns
from ml.analysis.drawdown import maximum_drawdown
from ml.analysis.returns import simple_returns
from ml.analysis.statistics import return_statistics
from ml.data.provider import MarketDataProvider


class AnalysisService:
    """Compute research summaries using existing analysis utilities."""

    def __init__(
        self,
        market_data_service: MarketDataService | None = None,
        provider: MarketDataProvider | None = None,
    ) -> None:
        if market_data_service is not None:
            self.market_data_service = market_data_service
        else:
            self.market_data_service = MarketDataService(provider=provider)

    def summarize(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> AnalysisSummaryResponse:
        market = self.market_data_service.get_ohlcv(symbol, start_date, end_date)
        frame = _frame_from_market_response(market)
        returns = simple_returns(frame)
        observed = returns.dropna()
        if observed.empty:
            raise BadRequestError("insufficient observations to compute returns")

        stats = return_statistics(returns)
        cumulative = cumulative_returns(observed)
        drawdown = maximum_drawdown(returns)

        return AnalysisSummaryResponse(
            symbol=market.symbol,
            start_date=market.start_date,
            end_date=market.end_date,
            observation_count=market.count,
            return_count=int(stats["count"]),
            mean_return=to_json_number(stats["mean"]),
            median_return=to_json_number(stats["median"]),
            volatility=to_json_number(stats["std"]),
            cumulative_return=to_json_number(cumulative.iloc[-1]),
            maximum_drawdown=to_json_number(drawdown),
        )


def _frame_from_market_response(market: MarketDataResponse) -> pd.DataFrame:
    rows = [observation.model_dump() for observation in market.data]
    return pd.DataFrame(rows)
