from datetime import date

import pandas as pd

from ml.data.provider import MarketDataProvider


class FakeProvider(MarketDataProvider):
    def get_historical_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        return pd.DataFrame({"symbol": [symbol], "start": [start_date], "end": [end_date]})


def test_provider_contract_can_be_implemented_without_provider_specific_logic() -> None:
    provider = FakeProvider()

    result = provider.get_historical_data("AAPL", date(2020, 1, 1), date(2020, 1, 2))

    assert result.loc[0, "symbol"] == "AAPL"