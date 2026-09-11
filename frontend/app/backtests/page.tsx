import type { Metadata } from "next";
import Link from "next/link";

import { TimeSeriesChart } from "@/components/charts/TimeSeriesChart";
import { MetricCard } from "@/components/ui/MetricCard";
import { StatePanel } from "@/components/ui/StatePanel";
import { getBacktest, listBacktests } from "@/lib/api";
import { formatDate, formatNumber, formatPercent } from "@/lib/format";
import { ApiError } from "@/types/api";
import type {
  PersistedBacktestDetail,
  PersistedBacktestListResponse,
} from "@/types/api";

export const metadata: Metadata = { title: "Backtests" };

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function metricMap(detail: PersistedBacktestDetail): Record<string, number | null> {
  return Object.fromEntries(
    detail.metrics.map((item) => [item.metric_name, item.metric_value]),
  );
}

function buildDrawdownSeries(
  equityPoints: { date: string; equity: number | null }[],
): { date: string; value: number }[] {
  const values: { date: string; value: number }[] = [];
  let peak = Number.NEGATIVE_INFINITY;
  for (const point of equityPoints) {
    if (point.equity === null) {
      continue;
    }
    peak = Math.max(peak, point.equity);
    const dd = peak === 0 ? 0 : point.equity / peak - 1;
    values.push({ date: point.date, value: dd });
  }
  return values;
}

function BacktestDetailView({ detail }: { detail: PersistedBacktestDetail }) {
  const metrics = metricMap(detail);
  const equityPoints = detail.equity_curve.filter((point) => point.equity !== null);
  const equity = equityPoints.map((point) => ({
    date: point.date,
    value: point.equity as number,
  }));
  const drawdown = buildDrawdownSeries(detail.equity_curve);

  return (
    <div className="space-y-6">
      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Configuration</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Model" value={detail.model_name} />
          <MetricCard label="Task" value={detail.task} />
          <MetricCard label="Strategy mode" value={detail.strategy_mode} />
          <MetricCard label="Sample kind" value={detail.sample_kind} />
          <MetricCard
            label="Transaction cost"
            value={`${formatNumber(detail.transaction_cost_bps, 1)} bps`}
          />
          <MetricCard
            label="Slippage"
            value={`${formatNumber(detail.slippage_bps, 1)} bps`}
          />
          <MetricCard
            label="Initial capital"
            value={formatNumber(detail.initial_capital, 2)}
          />
          <MetricCard
            label="Date range"
            value={`${formatDate(detail.start_date)} → ${formatDate(detail.end_date)}`}
          />
        </div>
      </section>

      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Performance and risk</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <MetricCard
            label="Total return"
            value={formatPercent(metrics.total_return)}
          />
          <MetricCard
            label="Annualized return"
            value={formatPercent(metrics.annualized_return)}
          />
          <MetricCard
            label="Annualized volatility"
            value={formatPercent(metrics.annualized_volatility)}
          />
          <MetricCard
            label="Sharpe ratio"
            value={formatNumber(metrics.sharpe_ratio, 2)}
          />
          <MetricCard
            label="Sortino ratio"
            value={formatNumber(metrics.sortino_ratio, 2)}
          />
          <MetricCard
            label="Maximum drawdown"
            value={formatPercent(metrics.maximum_drawdown)}
          />
        </div>
      </section>

      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Trading analytics</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <MetricCard
            label="Long exposure"
            value={formatPercent(metrics.long_exposure)}
          />
          <MetricCard
            label="Short exposure"
            value={formatPercent(metrics.short_exposure)}
          />
          <MetricCard
            label="Flat exposure"
            value={formatPercent(metrics.flat_exposure)}
          />
          <MetricCard
            label="Total turnover"
            value={formatNumber(metrics.total_turnover, 2)}
          />
          <MetricCard
            label="Completed trades"
            value={
              metrics.completed_trades === null || metrics.completed_trades === undefined
                ? "—"
                : String(metrics.completed_trades)
            }
          />
          <MetricCard
            label="Trade win rate"
            value={formatPercent(metrics.trade_win_rate)}
          />
        </div>
      </section>

      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Strategy equity curve</h3>
        <p className="mt-1 text-xs text-muted">
          Net equity after configured transaction costs and slippage.
        </p>
        <div className="mt-4">
          <TimeSeriesChart
            data={equity}
            valueLabel="Equity"
            valueFormat="number3"
          />
        </div>
      </section>

      <section className="rounded-md border border-border bg-surface p-4">
        <h3 className="text-sm font-semibold">Drawdown</h3>
        <p className="mt-1 text-xs text-muted">
          Peak-to-trough decline of the strategy equity path.
        </p>
        <div className="mt-4">
          <TimeSeriesChart
            data={drawdown}
            valueLabel="Drawdown"
            valueFormat="percent"
            color="var(--negative)"
          />
        </div>
      </section>

      <p className="rounded-md border border-border bg-surface-muted px-4 py-3 text-sm text-muted">
        Historical simulation does not guarantee future performance. Costs and
        drawdowns are first-class research outputs, not secondary details.
      </p>
    </div>
  );
}

export default async function BacktestsPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const selectedId = String(params.id ?? "").trim();

  let list: PersistedBacktestListResponse | null = null;
  let detail: PersistedBacktestDetail | null = null;
  let loadError: string | null = null;

  try {
    list = await listBacktests({ limit: 50, offset: 0 });
    if (selectedId) {
      detail = await getBacktest(selectedId);
    } else if (list.items[0]) {
      detail = await getBacktest(list.items[0].id);
    }
  } catch (error) {
    loadError =
      error instanceof ApiError
        ? error.detail ?? error.message
        : "Unable to load backtests.";
  }

  if (loadError) {
    return <StatePanel title="Backtests unavailable" message={loadError} />;
  }

  if (!list || list.total === 0) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold tracking-tight">Backtests</h2>
        <StatePanel
          title="No backtests yet"
          message="No persisted backtest results were returned by the API. Empty states are shown instead of fabricated profitability."
        />
      </div>
    );
  }

  const activeId = detail?.id ?? list.items[0].id;

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold tracking-tight">Backtests</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
          Research backtests with visible cost assumptions and risk metrics.
        </p>
      </section>

      <div className="overflow-x-auto rounded-md border border-border bg-surface">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-border bg-surface-muted text-xs uppercase tracking-[0.08em] text-muted">
            <tr>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3">Symbol</th>
              <th className="px-4 py-3">Model</th>
              <th className="px-4 py-3">Mode</th>
              <th className="px-4 py-3">Observations</th>
              <th className="px-4 py-3">Open</th>
            </tr>
          </thead>
          <tbody>
            {list.items.map((item) => (
              <tr
                key={item.id}
                className={`border-b border-border last:border-b-0 ${
                  item.id === activeId ? "bg-accent-muted/40" : ""
                }`}
              >
                <td className="px-4 py-3">{formatDate(item.created_at)}</td>
                <td className="px-4 py-3">{item.symbol}</td>
                <td className="px-4 py-3">{item.model_name}</td>
                <td className="px-4 py-3">{item.strategy_mode}</td>
                <td className="px-4 py-3">{item.observation_count}</td>
                <td className="px-4 py-3">
                  <Link
                    className="text-accent underline"
                    href={`/backtests?id=${item.id}`}
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {detail ? <BacktestDetailView detail={detail} /> : null}
    </div>
  );
}
