from datetime import date

import pytest

from ml.data.requests import MarketDataRequest


def test_request_normalizes_symbol_and_dates() -> None:
    request = MarketDataRequest.create(" aapl ", "2020-01-01", date(2020, 1, 3))

    assert request.symbol == "AAPL"
    assert request.start_date == date(2020, 1, 1)
    assert request.end_date == date(2020, 1, 3)


@pytest.mark.parametrize("symbol", ["", "   "])
def test_request_rejects_missing_symbol(symbol: str) -> None:
    with pytest.raises(ValueError, match="symbol must be provided"):
        MarketDataRequest.create(symbol, "2020-01-01", "2020-01-03")


def test_request_rejects_non_string_symbol() -> None:
    with pytest.raises(TypeError, match="symbol must be a string"):
        MarketDataRequest.create(None, "2020-01-01", "2020-01-03")


def test_request_rejects_invalid_date() -> None:
    with pytest.raises(ValueError, match="start_date must be a valid date"):
        MarketDataRequest.create("AAPL", "not-a-date", "2020-01-03")


def test_request_rejects_invalid_range() -> None:
    with pytest.raises(ValueError, match="start_date must occur before end_date"):
        MarketDataRequest.create("AAPL", "2020-01-03", "2020-01-03")