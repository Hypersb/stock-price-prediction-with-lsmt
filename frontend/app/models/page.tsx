import type { Metadata } from "next";
import Link from "next/link";

import { MetricCard } from "@/components/ui/MetricCard";
import { StatePanel } from "@/components/ui/StatePanel";
import { listModels } from "@/lib/api";
import { ApiError } from "@/types/api";
import type { ModelCatalogResponse } from "@/types/api";

export const metadata: Metadata = { title: "Models" };

export default async function ModelsPage() {
  let catalog: ModelCatalogResponse | null = null;
  let loadError: string | null = null;
  try {
    catalog = await listModels();
  } catch (error) {
    loadError =
      error instanceof ApiError
        ? error.detail ?? error.message
        : "Unable to load model catalog.";
  }

  if (loadError) {
    return <StatePanel title="Model catalog unavailable" message={loadError} />;
  }

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold tracking-tight">Models</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
          Supported research model families. A family being listed does not mean
          a trained artifact exists.
        </p>
      </section>
      <MetricCard label="Supported families" value={String(catalog?.count ?? 0)} />
      <div className="overflow-x-auto rounded-md border border-border bg-surface">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-border bg-surface-muted text-xs uppercase tracking-[0.08em] text-muted">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Family</th>
              <th className="px-4 py-3 font-medium">Tasks</th>
              <th className="px-4 py-3 font-medium">Trained artifact</th>
              <th className="px-4 py-3 font-medium">Description</th>
            </tr>
          </thead>
          <tbody>
            {(catalog?.models ?? []).map((model) => (
              <tr key={model.name} className="border-b border-border last:border-b-0">
                <td className="px-4 py-3 font-medium">{model.name}</td>
                <td className="px-4 py-3">{model.family}</td>
                <td className="px-4 py-3">{model.tasks.join(", ")}</td>
                <td className="px-4 py-3">{model.trained ? "yes" : "no"}</td>
                <td className="px-4 py-3 text-muted">{model.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-sm text-muted">
        Review stored runs on the{" "}
        <Link className="text-accent underline" href="/experiments">
          Experiments
        </Link>{" "}
        page.
      </p>
    </div>
  );
}
