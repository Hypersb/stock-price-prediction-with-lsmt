import type { Metadata } from "next";
import Link from "next/link";

import { MetricCard } from "@/components/ui/MetricCard";
import { PageHeader } from "@/components/ui/PageHeader";
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
    <div className="space-y-8">
      <PageHeader
        eyebrow="Families"
        title="Models"
        description="Supported research model families. Being listed does not mean a trained artifact exists."
      />
      <MetricCard label="Supported families" value={String(catalog?.count ?? 0)} />
      <div className="overflow-x-auto border-y border-border">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Family</th>
              <th>Tasks</th>
              <th>Trained artifact</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {(catalog?.models ?? []).map((model) => (
              <tr key={model.name}>
                <td className="font-semibold">{model.name}</td>
                <td>{model.family}</td>
                <td className="font-data text-xs">{model.tasks.join(", ")}</td>
                <td>{model.trained ? "yes" : "no"}</td>
                <td className="max-w-md text-muted">{model.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-sm text-muted">
        Review stored runs on the{" "}
        <Link className="font-semibold text-accent underline-offset-2 hover:underline" href="/experiments">
          Experiments
        </Link>{" "}
        page.
      </p>
    </div>
  );
}
