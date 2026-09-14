import { Suspense } from "react";
import type { Metadata } from "next";

import { FeatureExplorerClient } from "@/components/features/FeatureExplorerClient";
import { ResearchControls } from "@/components/research/ResearchControls";
import { MetricCard } from "@/components/ui/MetricCard";
import { MetricGrid } from "@/components/ui/MetricGrid";
import { PageHeader } from "@/components/ui/PageHeader";
import { LoadingPanel, StatePanel } from "@/components/ui/StatePanel";
import { getFeatures } from "@/lib/api";
import { defaultDateRange, formatDate } from "@/lib/format";
import {
  resolveResearchSymbol,
  resolveSearchDate,
} from "@/lib/searchParams";
import { ApiError } from "@/types/api";
import type { FeatureResponse } from "@/types/api";

export const metadata: Metadata = { title: "Features" };

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

async function FeaturesContent({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const defaults = defaultDateRange();
  const symbol = resolveResearchSymbol(params.symbol);
  const start = resolveSearchDate(params.start, defaults.startDate);
  const end = resolveSearchDate(params.end, defaults.endDate);

  let data: FeatureResponse | null = null;
  let loadError: string | null = null;
  try {
    data = await getFeatures(symbol, start, end, 120);
  } catch (error) {
    loadError =
      error instanceof ApiError
        ? error.detail ?? error.message
        : "Unexpected error while loading features.";
  }

  if (loadError) {
    return <StatePanel title="Features unavailable" message={loadError} />;
  }
  if (!data || data.feature_count === 0 || data.returned_rows === 0) {
    return (
      <StatePanel
        title="No features returned"
        message={`No engineered features were available for ${symbol} in the selected range.`}
      />
    );
  }

  return (
    <div className="space-y-8">
      <MetricGrid>
        <MetricCard label="Symbol" value={data.symbol} />
        <MetricCard label="Feature count" value={String(data.feature_count)} />
        <MetricCard
          label="Returned rows"
          value={String(data.returned_rows)}
          hint={`of ${data.observation_count} observations`}
        />
        <MetricCard
          label="Range"
          value={`${formatDate(data.start_date)} → ${formatDate(data.end_date)}`}
        />
      </MetricGrid>
      <FeatureExplorerClient data={data} />
    </div>
  );
}

export default function FeaturesPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Inputs"
        title="Features"
        description="Leakage-aware engineered inputs for research models. These are diagnostics, not trading signals."
      />
      <Suspense fallback={<LoadingPanel label="Loading controls" />}>
        <ResearchControls basePath="/features" />
      </Suspense>
      <Suspense fallback={<LoadingPanel />}>
        <FeaturesContent searchParams={searchParams} />
      </Suspense>
    </div>
  );
}
