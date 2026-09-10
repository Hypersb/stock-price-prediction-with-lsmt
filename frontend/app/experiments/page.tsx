import type { Metadata } from "next";
import Link from "next/link";

import { MetricCard } from "@/components/ui/MetricCard";
import { StatePanel } from "@/components/ui/StatePanel";
import { listExperiments } from "@/lib/api";
import { formatDate, formatNumber } from "@/lib/format";
import { ApiError } from "@/types/api";
import type { ExperimentListResponse } from "@/types/api";

export const metadata: Metadata = { title: "Experiments" };

export default async function ExperimentsPage() {
  let data: ExperimentListResponse | null = null;
  let loadError: string | null = null;
  try {
    data = await listExperiments({ limit: 50, offset: 0 });
  } catch (error) {
    loadError =
      error instanceof ApiError
        ? error.detail ?? error.message
        : "Unable to load experiments.";
  }

  if (loadError) {
    return <StatePanel title="Experiments unavailable" message={loadError} />;
  }

  if (!data || data.total === 0) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold tracking-tight">Experiments</h2>
        <StatePanel
          title="No experiments yet"
          message="The persistence API returned no stored experiments. Empty history is preferred over fabricated results."
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold tracking-tight">Experiments</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
          Stored research runs from PostgreSQL-backed persistence. High training
          performance alone does not imply a successful strategy.
        </p>
      </section>
      <MetricCard label="Stored experiments" value={String(data.total)} />
      <div className="overflow-x-auto rounded-md border border-border bg-surface">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-border bg-surface-muted text-xs uppercase tracking-[0.08em] text-muted">
            <tr>
              <th className="px-4 py-3 font-medium">Created</th>
              <th className="px-4 py-3 font-medium">Symbol</th>
              <th className="px-4 py-3 font-medium">Model</th>
              <th className="px-4 py-3 font-medium">Task</th>
              <th className="px-4 py-3 font-medium">Horizon</th>
              <th className="px-4 py-3 font-medium">Best epoch</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Detail</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item) => (
              <tr key={item.id} className="border-b border-border last:border-b-0">
                <td className="px-4 py-3">{formatDate(item.created_at)}</td>
                <td className="px-4 py-3">{item.symbol}</td>
                <td className="px-4 py-3">{item.model_name}</td>
                <td className="px-4 py-3">{item.task}</td>
                <td className="px-4 py-3">{item.forecast_horizon}</td>
                <td className="px-4 py-3">
                  {item.best_epoch === null ? "—" : item.best_epoch}
                </td>
                <td className="px-4 py-3">{item.status}</td>
                <td className="px-4 py-3">
                  <Link className="text-accent underline" href={`/experiments/${item.id}`}>
                    Open
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-muted">
        Best validation loss shown only on detail pages when available (
        {formatNumber(data.items[0]?.best_validation_loss ?? null, 4)} on newest row).
      </p>
    </div>
  );
}
