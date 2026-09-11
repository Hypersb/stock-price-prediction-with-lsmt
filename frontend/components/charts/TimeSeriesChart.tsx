"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatNumber, formatPercent, formatPrice } from "@/lib/format";

type Point = { date: string; value: number };

export type ChartValueFormat = "raw" | "price" | "percent" | "number" | "number3" | "number4";

function formatChartValue(value: number, format: ChartValueFormat): string {
  switch (format) {
    case "price":
      return formatPrice(value);
    case "percent":
      return formatPercent(value);
    case "number":
      return formatNumber(value);
    case "number3":
      return formatNumber(value, 3);
    case "number4":
      return formatNumber(value, 4);
    default:
      return String(value);
  }
}

export function TimeSeriesChart({
  data,
  valueLabel,
  valueFormat = "raw",
  color = "var(--accent)",
}: {
  data: Point[];
  valueLabel: string;
  /** Serializable format kind — do not pass functions from Server Components. */
  valueFormat?: ChartValueFormat;
  color?: string;
}) {
  if (data.length === 0) {
    return (
      <p className="text-sm text-muted">No series values available for this chart.</p>
    );
  }

  return (
    <div className="h-72 w-full" role="img" aria-label={`${valueLabel} time series chart`}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={28} />
          <YAxis
            tick={{ fontSize: 11 }}
            width={64}
            tickFormatter={(value: number) => formatChartValue(value, valueFormat)}
          />
          <Tooltip
            formatter={(value) => [
              formatChartValue(Number(value), valueFormat),
              valueLabel,
            ]}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            dot={false}
            strokeWidth={1.75}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
