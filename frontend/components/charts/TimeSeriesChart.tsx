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

type Point = { date: string; value: number };

export function TimeSeriesChart({
  data,
  valueLabel,
  valueFormatter,
  color = "var(--accent)",
}: {
  data: Point[];
  valueLabel: string;
  valueFormatter?: (value: number) => string;
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
            tickFormatter={(value: number) =>
              valueFormatter ? valueFormatter(value) : String(value)
            }
          />
          <Tooltip
            formatter={(value) => [
              valueFormatter ? valueFormatter(Number(value)) : String(value),
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
