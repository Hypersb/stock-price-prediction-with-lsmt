"use client";

import { useMemo, useState } from "react";

import { TimeSeriesChart } from "@/components/charts/TimeSeriesChart";
import { ChartFrame } from "@/components/ui/ChartFrame";
import { describeFeature } from "@/lib/featureNotes";
import type { FeatureResponse } from "@/types/api";

const FEATURE_GROUPS: { label: string; match: (name: string) => boolean }[] = [
  { label: "Returns", match: (name) => name.includes("return") || name.includes("momentum") },
  { label: "Moving averages", match: (name) => name.includes("sma") || name.includes("ema") },
  { label: "Volatility", match: (name) => name.includes("volatility") || name.includes("atr") },
  { label: "Volume", match: (name) => name.includes("volume") },
  {
    label: "Oscillators",
    match: (name) => name.includes("rsi") || name.includes("macd"),
  },
];

function groupFor(name: string): string {
  return FEATURE_GROUPS.find((group) => group.match(name))?.label ?? "Other";
}

export function FeatureExplorerClient({ data }: { data: FeatureResponse }) {
  const [selected, setSelected] = useState(data.feature_names[0] ?? "");

  const grouped = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const name of data.feature_names) {
      const key = groupFor(name);
      const bucket = map.get(key) ?? [];
      bucket.push(name);
      map.set(key, bucket);
    }
    return Array.from(map.entries());
  }, [data.feature_names]);

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
    return <p className="text-sm text-muted">No feature columns were returned.</p>;
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[16rem_1fr]">
      <aside className="space-y-5">
        <div>
          <p className="text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-muted">
            Feature catalog
          </p>
          <p className="mt-2 text-sm leading-6 text-muted">
            Pick a column. Warm-up windows stay missing on purpose.
          </p>
        </div>
        <div className="max-h-[34rem] space-y-4 overflow-y-auto pr-1">
          {grouped.map(([group, names]) => (
            <div key={group}>
              <p className="mb-2 text-[0.68rem] font-semibold uppercase tracking-[0.12em] text-accent">
                {group}
              </p>
              <ul className="space-y-1">
                {names.map((name) => {
                  const active = name === selected;
                  return (
                    <li key={name}>
                      <button
                        type="button"
                        className={`w-full border-l-2 px-3 py-1.5 text-left font-data text-xs transition-colors ${
                          active
                            ? "border-accent bg-accent-muted/70 text-foreground"
                            : "border-transparent text-muted hover:border-border hover:bg-surface"
                        }`}
                        onClick={() => setSelected(name)}
                      >
                        {name}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </aside>

      <div className="space-y-5">
        <div className="border-t border-border pt-5">
          <h3 className="font-display text-3xl text-foreground">{selected}</h3>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
            {describeFeature(selected)}
          </p>
          <p className="font-data mt-3 text-xs text-muted">
            plotted {series.length} · missing {missingCount}
          </p>
        </div>

        <ChartFrame
          title="Feature series"
          subtitle="Null warm-up values are omitted from the plot rather than invented."
          meta={selected}
        >
          <TimeSeriesChart
            data={series}
            valueLabel={selected}
            valueFormat="number4"
            variant="area"
            height={360}
            color="var(--ink-soft)"
          />
        </ChartFrame>
      </div>
    </div>
  );
}
