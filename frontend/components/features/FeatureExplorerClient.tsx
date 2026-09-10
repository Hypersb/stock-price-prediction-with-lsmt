"use client";

import { useMemo, useState } from "react";

import { TimeSeriesChart } from "@/components/charts/TimeSeriesChart";
import { describeFeature } from "@/lib/featureNotes";
import { formatNumber } from "@/lib/format";
import type { FeatureResponse } from "@/types/api";

export function FeatureExplorerClient({ data }: { data: FeatureResponse }) {
  const [selected, setSelected] = useState(data.feature_names[0] ?? "");

  const series = useMemo(() => {
    if (!selected) {
      return [];
    }
    return data.features
      .map((row) => ({
        date: row.date,
        value: row.values[selected],
      }))
      .filter((row): row is { date: string; value: number } => row.value !== null);
  }, [data.features, selected]);

  const missingCount = data.features.reduce((count, row) => {
    if (!selected) {
      return count;
    }
    return row.values[selected] === null ? count + 1 : count;
  }, 0);

  if (data.feature_names.length === 0) {
    return (
      <p className="text-sm text-muted">No feature columns were returned.</p>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-[16rem_1fr]">
        <label className="block text-sm">
          <span className="mb-1 block text-muted">Feature</span>
          <select
            className="w-full rounded-md border border-border bg-background px-3 py-2"
            value={selected}
            onChange={(event) => setSelected(event.target.value)}
            aria-label="Selected feature"
          >
            {data.feature_names.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <div className="rounded-md border border-border bg-surface px-4 py-3">
          <p className="text-sm font-medium">{selected}</p>
          <p className="mt-1 text-sm leading-6 text-muted">
            {describeFeature(selected)} Warm-up periods may appear as missing values.
          </p>
          <p className="mt-2 text-xs text-muted">
            Plotted points: {series.length}. Missing in returned window: {missingCount}.
          </p>
        </div>
      </div>

      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Feature series</h3>
        <div className="mt-4">
          <TimeSeriesChart
            data={series}
            valueLabel={selected}
            valueFormatter={(value) => formatNumber(value, 4)}
          />
        </div>
      </section>
    </div>
  );
}
