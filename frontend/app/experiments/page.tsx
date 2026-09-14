import type { Metadata } from "next";
import Link from "next/link";

import { MetricCard } from "@/components/ui/MetricCard";
import { PageHeader } from "@/components/ui/PageHeader";
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
      <div className="space-y-6">
        <PageHeader
          eyebrow="Persistence"
          title="Experiments"
          description="Stored research runs from PostgreSQL-backed persistence."
        />
        <StatePanel
          title="No experiments yet"
          message="The persistence API returned no stored experiments. Empty history is preferred over fabricated results."
        />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Persistence"
        title="Experiments"
        description="Stored research runs from PostgreSQL-backed persistence. High training performance alone does not imply a successful strategy."
      />
      <MetricCard label="Stored experiments" value={String(data.total)} />
      <div className="overflow-x-auto border-y border-border">
        <table className="data-table">
          <thead>
            <tr>
              <th>Created</th>
              <th>Symbol</th>
              <th>Model</th>
              <th>Task</th>
              <th>Horizon</th>
              <th>Best epoch</th>
              <th>Status</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item) => (
              <tr key={item.id}>
                <td className="font-data">{formatDate(item.created_at)}</td>
                <td>{item.symbol}</td>
                <td>{item.model_name}</td>
                <td>{item.task}</td>
                <td className="font-data">{item.forecast_horizon}</td>
                <td className="font-data">
                  {item.best_epoch === null ? "—" : item.best_epoch}
                </td>
                <td>{item.status}</td>
                <td>
                  <Link
                    className="font-semibold text-accent underline-offset-2 hover:underline"
                    href={`/experiments/${item.id}`}
                  >
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
