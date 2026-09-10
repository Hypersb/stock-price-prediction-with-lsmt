import type { Metadata } from "next";

export const metadata: Metadata = { title: "Backtests" };

export default function BacktestsPage() {
  return (
    <section className="space-y-2">
      <h2 className="text-2xl font-semibold tracking-tight">Backtests</h2>
      <p className="max-w-2xl text-sm leading-6 text-muted">
        Persisted backtest and risk analytics will appear when results are available.
      </p>
    </section>
  );
}
