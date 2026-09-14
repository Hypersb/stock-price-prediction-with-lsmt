import { Suspense } from "react";
import type { Metadata } from "next";

import { MetricCard } from "@/components/ui/MetricCard";
import { LoadingPanel, StatePanel } from "@/components/ui/StatePanel";
import { PageHeader } from "@/components/ui/PageHeader";
import { WalkForwardRunForm } from "@/components/walkforward/WalkForwardRunForm";
import { getWalkForwardRun } from "@/lib/api";
import { formatDate, formatNumber } from "@/lib/format";
import { ApiError } from "@/types/api";
import type { WalkForwardRunResponse } from "@/types/api";

export const metadata: Metadata = { title: "Walk Forward" };

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function summarizeMetric(
  run: WalkForwardRunResponse,
  metricName: string,
): { mean: number | null; std: number | null; min: number | null; max: number | null } {
  const values = run.folds
    .map((fold) => fold.fold_metrics?.[metricName])
    .filter((value): value is number => typeof value === "number");
  if (values.length === 0) {
    return { mean: null, std: null, min: null, max: null };
  }
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  const variance =
    values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length;
  return {
    mean,
    std: Math.sqrt(variance),
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

async function WalkForwardContent({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const runId = String(params.run_id ?? "").trim();
  if (!runId) {
    return (
      <StatePanel
        title="No walk-forward run selected"
        message="Enter a persisted walk-forward run id to inspect fold ranges and metrics. No fabricated fold results are shown."
      />
    );
  }

  let run: WalkForwardRunResponse | null = null;
  let loadError: string | null = null;
  try {
    run = await getWalkForwardRun(runId);
  } catch (error) {
    loadError =
      error instanceof ApiError
        ? error.detail ?? error.message
        : "Unable to load walk-forward run.";
  }

  if (loadError || !run) {
    return (
      <StatePanel
        title="Walk-forward run unavailable"
        message={loadError ?? "Run not found."}
      />
    );
  }

  const metricNames = Array.from(
    new Set(
      run.folds.flatMap((fold) => Object.keys(fold.fold_metrics ?? {})),
    ),
  ).sort();

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Symbol" value={run.symbol} />
        <MetricCard label="Model" value={run.model_name} />
        <MetricCard label="Task" value={run.task} />
        <MetricCard label="Window" value={run.window_type} />
        <MetricCard label="Folds" value={String(run.folds.length)} />
        <MetricCard label="Horizon" value={String(run.forecast_horizon)} />
        <MetricCard label="Gap" value={String(run.gap)} />
        <MetricCard label="Step size" value={String(run.step_size)} />
      </div>

      <section className="border-t border-border pt-5">
        <h3 className="text-sm font-semibold tracking-wide">Stability summary</h3>
        <p className="mt-1 text-xs text-muted">
          Aggregate statistics across folds when numeric fold metrics exist.
        </p>
        {metricNames.length === 0 ? (
          <p className="mt-3 text-sm text-muted">No fold metrics were stored.</p>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-border text-xs uppercase tracking-[0.08em] text-muted">
                <tr>
                  <th className="px-3 py-2">Metric</th>
                  <th className="px-3 py-2">Mean</th>
                  <th className="px-3 py-2">Std</th>
                  <th className="px-3 py-2">Min</th>
                  <th className="px-3 py-2">Max</th>
                </tr>
              </thead>
              <tbody>
                {metricNames.map((name) => {
                  const stats = summarizeMetric(run, name);
                  return (
                    <tr key={name} className="border-b border-border last:border-b-0">
                      <td className="px-3 py-2">{name}</td>
                      <td className="px-3 py-2 font-mono">
                        {formatNumber(stats.mean, 4)}
                      </td>
                      <td className="px-3 py-2 font-mono">
                        {formatNumber(stats.std, 4)}
                      </td>
                      <td className="px-3 py-2 font-mono">
                        {formatNumber(stats.min, 4)}
                      </td>
                      <td className="px-3 py-2 font-mono">
                        {formatNumber(stats.max, 4)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="border-t border-border pt-5">
        <h3 className="text-sm font-semibold tracking-wide">Fold timeline</h3>
        <p className="mt-1 text-xs text-muted">
          Each fold evaluates a distinct future period. Weak folds remain visible.
        </p>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-border text-xs uppercase tracking-[0.08em] text-muted">
              <tr>
                <th className="px-3 py-2">Fold</th>
                <th className="px-3 py-2">Train</th>
                <th className="px-3 py-2">Validation</th>
                <th className="px-3 py-2">Test</th>
                <th className="px-3 py-2">Counts</th>
                <th className="px-3 py-2">Metrics</th>
              </tr>
            </thead>
            <tbody>
              {run.folds.map((fold) => (
                <tr key={fold.fold_number} className="border-b border-border last:border-b-0">
                  <td className="px-3 py-2 font-medium">{fold.fold_number}</td>
                  <td className="px-3 py-2">
                    {formatDate(fold.train_start)} → {formatDate(fold.train_end)}
                  </td>
                  <td className="px-3 py-2">
                    {fold.validation_start
                      ? `${formatDate(fold.validation_start)} → ${formatDate(fold.validation_end)}`
                      : "—"}
                  </td>
                  <td className="px-3 py-2">
                    {formatDate(fold.test_start)} → {formatDate(fold.test_end)}
                  </td>
                  <td className="px-3 py-2">
                    {fold.train_count}/{fold.validation_count}/{fold.test_count}
                  </td>
                  <td className="px-3 py-2 font-mono text-xs">
                    {fold.fold_metrics
                      ? Object.entries(fold.fold_metrics)
                          .map(
                            ([key, value]) => `${key}=${formatNumber(value, 4)}`,
                          )
                          .join(", ")
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default function WalkForwardPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Validation"
        title="Walk-forward"
        description="Temporal validation analytics for expanding or rolling research runs."
      />
      <Suspense fallback={<LoadingPanel label="Loading run form" />}>
        <WalkForwardRunForm />
      </Suspense>
      <Suspense fallback={<LoadingPanel />}>
        <WalkForwardContent searchParams={searchParams} />
      </Suspense>
    </div>
  );
}
