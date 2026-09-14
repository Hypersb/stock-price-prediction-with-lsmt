"""Run a legitimate startup empirical research study and render the report.

Usage:
  python -m scripts.run_startup_empirical_study

Requires network access to the configured market-data provider (Yahoo).
Does not fabricate metrics. Writes:
  - artifacts/empirics/<experiment_id>/ (gitignored)
  - docs/final-research-report.md (committed only after operator review)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from ml.backtesting.config import BacktestConfig
from ml.data.fingerprint import build_dataset_spec
from ml.data.ingestion import MarketDataIngestionService
from ml.data.storage import HistoricalDataStore
from ml.data.validation import assess_market_data_quality
from ml.data.yahoo import YahooFinanceProvider
from ml.research.config import FinalResearchConfig
from ml.research.pipeline import run_final_research_evaluation
from ml.research.regimes import RegimeConfig
from ml.research.report import render_final_research_report
from ml.research.universe import ResearchUniverse
from ml.validation.config import WalkForwardConfig

REPO_ROOT = Path(__file__).resolve().parents[1]
STARTUP_UNIVERSE = ("AAPL", "MSFT", "NVDA", "SPY")


def startup_empirical_config() -> FinalResearchConfig:
    """Explicit configuration for the startup empirical study.

    Choices are documented for reproducibility — not tuned on holdout results.
    Price basis remains unadjusted Yahoo closes.
    """
    return FinalResearchConfig(
        symbols=STARTUP_UNIVERSE,
        target_type="regression",
        horizon=1,
        feature_parameters={
            "return_lags": (1, 2, 3, 5, 10),
            "momentum_windows": (5, 10, 20),
            "moving_average_windows": (5, 10, 20, 50),
            "ema_spans": (12, 26),
            "volatility_windows": (5, 10, 20),
            "volume_window": 20,
            "rsi_period": 14,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "atr_period": 14,
        },
        walk_forward=WalkForwardConfig(
            initial_train_size=252,
            validation_size=63,
            test_size=63,
            step_size=63,
            forecast_horizon=1,
            window_type="expanding",
        ),
        model_families=("naive", "linear", "boosting", "lstm"),
        random_seed=42,
        lookback=20,
        hidden_size=32,
        lstm_epochs=8,
        regime=RegimeConfig(),
        backtest=BacktestConfig(transaction_cost_bps=10.0, slippage_bps=5.0),
        cost_scenarios_bps=(0.0, 5.0, 10.0, 25.0),
        signal_thresholds=(0.0,),
        compare_model_a="linear_regression",
        compare_model_b="lstm",
        bootstrap_iterations=200,
        block_length=10,
        include_ablation=True,
        include_complexity=True,
        include_explainability=True,
        include_regimes=True,
        include_sensitivity=True,
        include_statistics=True,
    )


def fetch_universe(
    symbols: tuple[str, ...],
    start: date,
    end: date,
) -> dict[str, object]:
    service = MarketDataIngestionService(
        YahooFinanceProvider(),
        store=HistoricalDataStore(),
    )
    market_data: dict[str, object] = {}
    for symbol in symbols:
        frame = service.ingest(symbol, start.isoformat(), end.isoformat(), persist=True)
        assess_market_data_quality(frame)
        market_data[symbol] = frame
    return market_data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2018-01-01")
    parser.add_argument("--end", default="2025-01-01")
    parser.add_argument(
        "--write-docs-report",
        action="store_true",
        help="Overwrite docs/final-research-report.md with rendered results",
    )
    args = parser.parse_args(argv)

    config = startup_empirical_config()
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    print(f"fetching {config.symbols} {start}→{end} (unadjusted Yahoo)...", flush=True)
    market_data = fetch_universe(config.symbols, start, end)

    dataset_specs = {
        symbol: build_dataset_spec(frame, symbol=symbol, provider="yahoo").__dict__
        for symbol, frame in market_data.items()
    }
    print("running walk-forward empirical evaluation (may take several minutes)...", flush=True)
    result = run_final_research_evaluation(market_data, config)  # type: ignore[arg-type]
    document = render_final_research_report(result)

    out_dir = REPO_ROOT / "artifacts" / "empirics" / result.experiment_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.md").write_text(document.markdown, encoding="utf-8")
    (out_dir / "config.json").write_text(
        json.dumps(config.to_dict(), indent=2, default=str),
        encoding="utf-8",
    )
    (out_dir / "datasets.json").write_text(
        json.dumps(dataset_specs, indent=2, default=str),
        encoding="utf-8",
    )
    summary = result.multi_asset.summary_table()
    summary.to_csv(out_dir / "model_summary.csv", index=False)
    print(f"wrote artifacts to {out_dir}", flush=True)
    print(summary.to_string(index=False), flush=True)

    if args.write_docs_report:
        report_path = REPO_ROOT / "docs" / "final-research-report.md"
        header = (
            "# Final Quantitative Research Report\n\n"
            "Generated by `python -m scripts.run_startup_empirical_study "
            "--write-docs-report`.\n\n"
            f"- experiment_id: `{result.experiment_id}`\n"
            f"- universe: {', '.join(config.symbols)}\n"
            f"- period: {args.start} → {args.end} (provider half-open end)\n"
            "- price_basis: unadjusted Yahoo close (`auto_adjust=False`)\n"
            "- validation: expanding walk-forward with purge; horizon=1\n"
            "- costs: 10 bps transaction + 5 bps slippage (base backtest)\n\n"
            "Historical simulations are not guarantees of future performance.\n\n"
            "---\n\n"
        )
        report_path.write_text(header + document.markdown, encoding="utf-8")
        print(f"updated {report_path}", flush=True)

    _ = ResearchUniverse(symbols=config.symbols)
    return 0


if __name__ == "__main__":
    sys.exit(main())
