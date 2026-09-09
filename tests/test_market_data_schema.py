from ml.data.schema import REQUIRED_COLUMNS


def test_required_columns_define_canonical_ohlcv_order() -> None:
    assert REQUIRED_COLUMNS == ("date", "open", "high", "low", "close", "volume")