"""Fetch historical market data through the ingestion service.

Preferred invocation from the repository root:

    PYTHONPATH=. python -m scripts.fetch_market_data AAPL 2020-01-01 2024-01-01 --save
"""

from __future__ import annotations

import argparse
import sys

from ml.data.ingestion import MarketDataIngestionService
from ml.data.storage import HistoricalDataStore
from ml.data.symbols import normalize_symbol
from ml.data.yahoo import YahooFinanceProvider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch historical OHLCV market data via the research ingestion service."
    )
    parser.add_argument("symbol", help="ticker symbol, such as AAPL or BRK-B")
    parser.add_argument("start_date", help="inclusive start date, such as 2020-01-01")
    parser.add_argument("end_date", help="exclusive end date, such as 2026-01-01")
    parser.add_argument(
        "--save",
        action="store_true",
        help="save normalized data under data/raw/",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        symbol = normalize_symbol(args.symbol)
        store = HistoricalDataStore() if args.save else None
        service = MarketDataIngestionService(YahooFinanceProvider(), store)
        data = service.ingest(
            symbol, args.start_date, args.end_date, persist=args.save
        )
    except Exception as exc:  # noqa: BLE001 - CLI must surface failures as exit codes
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if data.empty:
        print(f"error: no rows returned for {symbol}", file=sys.stderr)
        return 1

    print(
        f"fetched {len(data)} rows for {symbol} "
        f"from {data['date'].min().date()} through {data['date'].max().date()}"
    )
    if args.save:
        print(f"saved normalized data to data/raw/{symbol}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
