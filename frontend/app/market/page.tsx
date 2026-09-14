import { Suspense } from "react";
import type { Metadata } from "next";

import { TimeSeriesChart } from "@/components/charts/TimeSeriesChart";
import { ResearchControls } from "@/components/research/ResearchControls";
import { ChartFrame } from "@/components/ui/ChartFrame";
import { MetricCard } from "@/components/ui/MetricCard";
import { MetricGrid } from "@/components/ui/MetricGrid";
import { PageHeader } from "@/components/ui/PageHeader";
import { LoadingPanel, StatePanel } from "@/components/ui/StatePanel";
import { getAnalysisSummary, getMarketData } from "@/lib/api";
import {
  defaultDateRange,
  formatDate,
  formatNumber,
  formatPercent,
  formatPrice,
} from "@/lib/format";
import {
  resolveResearchSymbol,
  resolveSearchDate,
} from "@/lib/searchParams";
import { ApiError } from "@/types/api";
import type { AnalysisSummaryResponse, MarketDataResponse } from "@/types/api";

export const metadata: Metadata = { title: "Market" };

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function buildCumulativeSeries(market: MarketDataResponse) {
  const values: { date: string; value: number }[] = [];
  let cumulative = 0;
  for (let index = 0; index < market.data.length; index += 1) {
    const row = market.data[index];
    if (index === 0) {
      values.push({ date: row.date, value: 0 });
      continue;
    }
    const previous = market.data[index - 1].close;
    const ret = previous === 0 ? 0 : row.close / previous - 1;
    cumulative = (1 + cumulative) * (1 + ret) - 1;
    values.push({ date: row.date, value: cumulative });
  }
  return values;
}

function MarketSuccess({
  market,
  analysis,
}: {
  market: MarketDataResponse;
  analysis: AnalysisSummaryResponse;
}) {
  const closes = market.data.map((row) => ({ date: row.date, value: row.close }));
  const volumes = market.data.map((row) => ({ date: row.date, value: row.volume }));
  const cumulativeSeries = buildCumulativeSeries(market);
  const latest = market.data[market.data.length - 1];
  const rangeLabel = `${formatDate(analysis.start_date)} → ${formatDate(analysis.end_date)}`;

  return (
    <div className="space-y-10">
      <MetricGrid>
        <MetricCard label="Symbol" value={market.symbol} />
        <MetricCard
          label="Latest close"
          value={formatPrice(latest.close)}
          hint={`As of ${formatDate(latest.date)}`}
        />
        <MetricCard
          label="Observations"
          value={String(analysis.observation_count)}
          hint={rangeLabel}
        />
        <MetricCard
          label="Chart rows"
          value={`${market.returned} / ${market.total}`}
          hint={
            market.returned < market.total
              ? `Paginated · limit ${market.limit}`
              : "Full series in response"
          }
        />
        <MetricCard
          label="Cumulative return"
          value={formatPercent(analysis.cumulative_return)}
          hint="Historical path, not a forecast"
        />
        <MetricCard
          label="Volatility"
          value={formatPercent(analysis.volatility)}
          hint="Return sample standard deviation"
        />
        <MetricCard
          label="Maximum drawdown"
          value={formatPercent(analysis.maximum_drawdown)}
        />
        <MetricCard
          label="Mean / median"
          value={`${formatPercent(analysis.mean_return)} · ${formatPercent(analysis.median_return)}`}
        />
      </MetricGrid>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <ChartFrame
          title="Closing price"
          subtitle="Daily closes for the selected window. This chart is history, not a model prediction."
          meta={`${market.returned} pts`}
        >
          <TimeSeriesChart
            data={closes}
            valueLabel="Close"
            valueFormat="price"
            variant="area"
            height={340}
          />
        </ChartFrame>

        <ChartFrame
          title="Cumulative return"
          subtitle="Compounded simple returns from closing prices."
          meta={formatPercent(analysis.cumulative_return)}
        >
          <TimeSeriesChart
            data={cumulativeSeries}
            valueLabel="Cumulative"
            valueFormat="percent"
            color="var(--positive)"
            variant="area"
            height={340}
          />
        </ChartFrame>
      </div>

      <ChartFrame
        title="Volume"
        subtitle="Share volume paired with the same observation window."
        meta={`last ${formatNumber(latest.volume, 0)}`}
      >
        <TimeSeriesChart
          data={volumes}
          valueLabel="Volume"
          valueFormat="number"
          variant="volume"
          height={180}
        />
      </ChartFrame>
    </div>
  );
}

async function MarketContent({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const defaults = defaultDateRange();
  const symbol = resolveResearchSymbol(params.symbol);
  const start = resolveSearchDate(params.start, defaults.startDate);
  const end = resolveSearchDate(params.end, defaults.endDate);

  let market: MarketDataResponse | null = null;
  let analysis: AnalysisSummaryResponse | null = null;
  let loadError: string | null = null;
  try {
    [market, analysis] = await Promise.all([
      getMarketData(symbol, start, end),
      getAnalysisSummary(symbol, start, end),
    ]);
  } catch (error) {
    loadError =
      error instanceof ApiError
        ? error.detail ?? error.message
        : "Unexpected error while loading market research data.";
  }

  if (loadError) {
    return <StatePanel title="Market data unavailable" message={loadError} />;
  }
  if (!market || !analysis || market.count === 0) {
    return (
      <StatePanel
        title="No market data"
        message={`The API returned no observations for ${symbol} between ${start} and ${end}.`}
      />
    );
  }

  return <MarketSuccess market={market} analysis={analysis} />;
}

export default function MarketPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Prices"
        title="Market"
        description="Inspect historical OHLCV and quantitative summary statistics. Nothing on this page is a buy or sell call."
      />
      <Suspense fallback={<LoadingPanel label="Loading controls" />}>
        <ResearchControls basePath="/market" />
      </Suspense>
      <Suspense fallback={<LoadingPanel />}>
        <MarketContent searchParams={searchParams} />
      </Suspense>
    </div>
  );
}
