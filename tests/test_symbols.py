"""Tests for canonical research symbol normalization."""

import pytest

from ml.data.symbols import normalize_symbol


def test_normalize_symbol_strips_and_uppercases() -> None:
    assert normalize_symbol("  aapl ") == "AAPL"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("brk-b", "BRK-B"),
        ("BRK.B", "BRK.B"),
        ("btc-usd", "BTC-USD"),
        ("^gspc", "^GSPC"),
    ],
)
def test_normalize_symbol_preserves_provider_characters(raw: str, expected: str) -> None:
    assert normalize_symbol(raw) == expected


def test_normalize_symbol_rejects_empty() -> None:
    with pytest.raises(ValueError, match="provided"):
        normalize_symbol("   ")


def test_normalize_symbol_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        normalize_symbol(123)  # type: ignore[arg-type]
