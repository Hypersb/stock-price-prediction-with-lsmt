import type { Metadata } from "next";
import Link from "next/link";

import { MetricCard } from "@/components/ui/MetricCard";
import { StatePanel } from "@/components/ui/StatePanel";
import {
  getExperiment,
  getExperimentMetrics,
  getExperimentRelated,
} from "@/lib/api";
import { formatDate, formatNumber } from "@/lib/format";
import { ApiError } from "@/types/api";
import type {
  ExperimentDetail,
  ExperimentMetricsResponse,
  ExperimentRelatedResponse,
} from "@/types/api";

type Params = Promise<{ id: string }>;

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const { id } = await params;
  return { title: `Experiment ${id.slice(0, 8)}` };
}

export default async function ExperimentDetailPage({
  params,
}: {
  params: Params;
}) {
  const { id } = await params;

  let experiment: ExperimentDetail | null = null;
  let metrics: ExperimentMetricsResponse | null = null;
  let related: ExperimentRelatedResponse | null = null;
  let loadError: string | null = null;
  try {
    [experiment, metrics, related] = await Promise.all([
      getExperiment(id),
      getExperimentMetrics(id),
      getExperimentRelated(id),
    ]);
  } catch (error) {
    loadError =
      error instanceof ApiError
        ? error.detail ?? error.message
        : "Unable to load experiment detail.";
  }

  if (loadError || !experiment || !metrics) {
    return (
      <StatePanel
        title="Experiment not found"
        message={loadError ?? "No experiment exists for this identifier."}
        action={
          <Link className="text-sm text-accent underline" href="/experiments">
            Back to experiments
          </Link>
        }
      />
    );
  }

  const validation = metrics.metrics.filter((item) => item.split === "validation");
  const test = metrics.metrics.filter((item) => item.split === "test");
  const walkForwardRuns = related?.walk_forward_runs ?? [];
  const backtests = related?.backtests ?? [];

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm text-muted">
          <Link href="/experiments" className="text-accent underline">
            Experiments
          </Link>
        </p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight">
          {experiment.symbol} · {experiment.model_name}
        </h2>
        <p className="mt-2 font-mono text-xs text-muted">{experiment.id}</p>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-muted">
          Persisted experiment metadata and linked research artifacts. Advanced
          multi-asset or sensitivity reports are produced by the offline research
          pipeline and are not executed by this page.
        </p>
      </section>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Task" value={experiment.task} />
        <MetricCard label="Status" value={experiment.status} />
        <MetricCard label="Forecast horizon" value={String(experiment.forecast_horizon)} />
        <MetricCard
          label="Lookback"
          value={experiment.lookback === null ? "—" : String(experiment.lookback)}
        />
        <MetricCard
          label="Best epoch"
          value={experiment.best_epoch === null ? "—" : String(experiment.best_epoch)}
        />
        <MetricCard
          label="Best validation loss"
          value={formatNumber(experiment.best_validation_loss, 4)}
        />
        <MetricCard label="Created" value={formatDate(experiment.created_at)} />
        <MetricCard
          label="Checkpoint"
          value={experiment.checkpoint_reference ? "referenced" : "none"}
          hint={experiment.checkpoint_reference ?? undefined}
        />
      </div>

      <section className="grid gap-4 lg:grid-cols-2">
        <MetricGroup title="Validation metrics" rows={validation} />
        <MetricGroup title="Test metrics" rows={test} />
      </section>

      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Linked walk-forward runs</h3>
        <p className="mt-1 text-xs text-muted">
          Out-of-sample fold metadata persisted with this experiment.
        </p>
        {walkForwardRuns.length === 0 ? (
          <p className="mt-3 text-sm text-muted">
            No walk-forward runs are linked yet.
          </p>
        ) : (
          <ul className="mt-3 space-y-2 text-sm">
            {walkForwardRuns.map((run) => (
              <li key={run.id} className="flex flex-wrap items-center justify-between gap-2">
                <span>
                  {run.window_type} · {run.folds.length} folds · horizon{" "}
                  {run.forecast_horizon}
                </span>
                <Link
                  className="font-mono text-xs text-accent underline"
                  href={`/walk-forward?run_id=${encodeURIComponent(run.id)}`}
                >
                  {run.id.slice(0, 8)}…
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Linked backtests</h3>
        <p className="mt-1 text-xs text-muted">
          Historical strategy simulations only. Past performance does not
          guarantee future results.
        </p>
        {backtests.length === 0 ? (
          <p className="mt-3 text-sm text-muted">No backtests are linked yet.</p>
        ) : (
          <ul className="mt-3 space-y-2 text-sm">
            {backtests.map((item) => (
              <li key={item.id} className="flex flex-wrap items-center justify-between gap-2">
                <span>
                  {item.strategy_mode} · {item.observation_count} observations
                </span>
                <Link
                  className="font-mono text-xs text-accent underline"
                  href={`/backtests?backtest_id=${encodeURIComponent(item.id)}`}
                >
                  {item.id.slice(0, 8)}…
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function MetricGroup({
  title,
  rows,
}: {
  title: string;
  rows: { metric_name: string; metric_value: number | null }[];
}) {
  return (
    <section className="rounded-md border border-border bg-surface p-4">
      <h3 className="text-sm font-semibold">{title}</h3>
      {rows.length === 0 ? (
        <p className="mt-3 text-sm text-muted">No metrics stored for this split.</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {rows.map((row) => (
            <li
              key={row.metric_name}
              className="flex items-center justify-between gap-3 text-sm"
            >
              <span>{row.metric_name}</span>
              <span className="font-mono">{formatNumber(row.metric_value, 4)}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
