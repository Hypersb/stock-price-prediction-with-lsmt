import { Suspense } from "react";
import type { Metadata } from "next";

import { TimeSeriesChart } from "@/components/charts/TimeSeriesChart";
import { ResearchControls } from "@/components/research/ResearchControls";
import { MetricCard } from "@/components/ui/MetricCard";
import { LoadingPanel, StatePanel } from "@/components/ui/StatePanel";
import { getAnalysisSummary, getMarketData } from "@/lib/api";
import { appConfig } from "@/lib/env";
import {
  defaultDateRange,
  formatDate,
  formatPercent,
  formatPrice,
} from "@/lib/format";
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
  const cumulativeSeries = buildCumulativeSeries(market);
  const latest = market.data[market.data.length - 1];

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Symbol" value={market.symbol} />
        <MetricCard
          label="Latest close"
          value={formatPrice(latest.close)}
          hint={`As of ${formatDate(latest.date)}`}
        />
        <MetricCard
          label="Observations"
          value={String(analysis.observation_count)}
          hint={`${formatDate(analysis.start_date)} → ${formatDate(analysis.end_date)}`}
        />
        <MetricCard
          label="Chart rows"
          value={`${market.returned} / ${market.total}`}
          hint={
            market.returned < market.total
              ? `Paginated (limit=${market.limit}, offset=${market.offset})`
              : "Full series in response"
          }
        />
        <MetricCard
          label="Cumulative return"
          value={formatPercent(analysis.cumulative_return)}
          hint="Historical, not a forecast"
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
        <MetricCard label="Mean return" value={formatPercent(analysis.mean_return)} />
        <MetricCard
          label="Median return"
          value={formatPercent(analysis.median_return)}
        />
      </div>

      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Closing price</h3>
        <p className="mt-1 text-xs text-muted">
          Historical closes for the selected range. This is not a forecast chart.
        </p>
        <div className="mt-4">
          <TimeSeriesChart
            data={closes}
            valueLabel="Close"
            valueFormat="price"
          />
        </div>
      </section>

      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Cumulative return</h3>
        <p className="mt-1 text-xs text-muted">
          Compounded simple returns derived from closing prices.
        </p>
        <div className="mt-4">
          <TimeSeriesChart
            data={cumulativeSeries}
            valueLabel="Cumulative return"
            valueFormat="percent"
            color="var(--positive)"
          />
        </div>
      </section>
    </div>
  );
}

async function MarketContent({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const defaults = defaultDateRange();
  const symbol = String(params.symbol ?? appConfig.defaultSymbol).toUpperCase();
  const start = String(params.start ?? defaults.startDate);
  const end = String(params.end ?? defaults.endDate);

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
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold tracking-tight">Market</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
          Inspect historical OHLCV and quantitative summary statistics from the
          FastAPI research backend.
        </p>
      </section>
      <Suspense fallback={<LoadingPanel label="Loading controls" />}>
        <ResearchControls basePath="/market" />
      </Suspense>
      <Suspense fallback={<LoadingPanel />}>
        <MarketContent searchParams={searchParams} />
      </Suspense>
    </div>
  );
}
