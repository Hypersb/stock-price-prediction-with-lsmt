import Link from "next/link";

import { getHealth, listExperiments, listBacktests, listModels } from "@/lib/api";
import { StatePanel } from "@/components/ui/StatePanel";
import { MetricCard } from "@/components/ui/MetricCard";
import { ApiError } from "@/types/api";

export default async function OverviewPage() {
  let healthLabel = "unknown";
  let experimentTotal = 0;
  let backtestTotal = 0;
  let modelCount = 0;
  let backendError: string | null = null;

  try {
    const [health, experiments, backtests, models] = await Promise.all([
      getHealth(),
      listExperiments({ limit: 5, offset: 0 }),
      listBacktests({ limit: 5, offset: 0 }),
      listModels(),
    ]);
    healthLabel = `${health.status} · ${health.version}`;
    experimentTotal = experiments.total;
    backtestTotal = backtests.total;
    modelCount = models.count;
  } catch (error) {
    backendError =
      error instanceof ApiError
        ? error.detail ?? error.message
        : "Backend unavailable.";
  }

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold tracking-tight">Overview</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
          Research dashboard connected to the FastAPI quantitative platform.
          Empty sections mean no stored results yet — values are never fabricated.
        </p>
      </section>

      {backendError ? (
        <StatePanel
          title="Backend unavailable"
          message={backendError}
          action={
            <p className="text-sm text-muted">
              Start the API with{" "}
              <code className="rounded bg-surface-muted px-1.5 py-0.5">
                uvicorn backend.app.main:app --reload
              </code>
            </p>
          }
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="API health" value={healthLabel} />
          <MetricCard label="Model families" value={String(modelCount)} />
          <MetricCard label="Stored experiments" value={String(experimentTotal)} />
          <MetricCard label="Stored backtests" value={String(backtestTotal)} />
        </div>
      )}

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {[
          ["Market", "/market", "OHLCV and return summary"],
          ["Features", "/features", "Leakage-aware feature frames"],
          ["Experiments", "/experiments", "Persisted model runs"],
          ["Walk Forward", "/walk-forward", "Fold-level temporal metrics"],
          ["Backtests", "/backtests", "Costs, equity, and drawdown"],
          ["Models", "/models", "Supported research families"],
        ].map(([title, href, detail]) => (
          <Link
            key={href}
            href={href}
            className="rounded-md border border-border bg-surface px-4 py-3 transition-colors hover:bg-surface-muted"
          >
            <h3 className="text-sm font-semibold">{title}</h3>
            <p className="mt-1 text-sm text-muted">{detail}</p>
          </Link>
        ))}
      </section>
    </div>
  );
}
