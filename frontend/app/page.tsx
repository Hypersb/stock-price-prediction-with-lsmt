import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Overview",
};

export default function OverviewPage() {
  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold tracking-tight">Overview</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
          Use the navigation to inspect market data, engineered features,
          model metadata, stored experiments, walk-forward validation, and
          backtest risk analytics through the FastAPI research backend.
        </p>
      </section>
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {[
          ["Market", "OHLCV and return summary"],
          ["Features", "Leakage-aware feature frames"],
          ["Experiments", "Persisted model runs"],
          ["Walk Forward", "Fold-level temporal metrics"],
          ["Backtests", "Costs, equity, and drawdown"],
          ["Models", "Supported research families"],
        ].map(([title, detail]) => (
          <article
            key={title}
            className="rounded-md border border-border bg-surface px-4 py-3"
          >
            <h3 className="text-sm font-semibold">{title}</h3>
            <p className="mt-1 text-sm text-muted">{detail}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
