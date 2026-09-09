"""Fetch historical market data through the ingestion service."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.data.ingestion import MarketDataIngestionService
from ml.data.storage import HistoricalDataStore
from ml.data.yahoo import YahooFinanceProvider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch historical OHLCV market data.")
    parser.add_argument("symbol", help="ticker symbol, such as AAPL")
    parser.add_argument("start_date", help="inclusive start date, such as 2020-01-01")
    parser.add_argument("end_date", help="exclusive end date, such as 2026-01-01")
    parser.add_argument("--save", action="store_true", help="save normalized data to data/raw/")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    store = HistoricalDataStore() if args.save else None
    service = MarketDataIngestionService(YahooFinanceProvider(), store)
    data = service.ingest(args.symbol, args.start_date, args.end_date, persist=args.save)
    symbol = args.symbol.strip().upper()

    print(
        f"fetched {len(data)} rows for {symbol} "
        f"from {data['date'].min().date()} through {data['date'].max().date()}"
    )
    if args.save:
        print(f"saved normalized data to data/raw/{symbol}.csv")


if __name__ == "__main__":
    main()