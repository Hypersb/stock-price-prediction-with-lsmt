"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatNumber, formatPercent, formatPrice } from "@/lib/format";

export type ChartPoint = { date: string; value: number };

export type ChartValueFormat =
  | "raw"
  | "price"
  | "percent"
  | "number"
  | "number3"
  | "number4";

export type ChartVariant = "line" | "area" | "drawdown" | "volume";

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

function shortDate(value: string): string {
  if (value.length >= 10) {
    return value.slice(5, 10);
  }
  return value;
}

function ChartTooltip({
  active,
  payload,
  label,
  valueLabel,
  valueFormat,
}: {
  active?: boolean;
  payload?: Array<{ value?: number | string }>;
  label?: string;
  valueLabel: string;
  valueFormat: ChartValueFormat;
}) {
  if (!active || !payload?.length) {
    return null;
  }
  const raw = payload[0]?.value;
  const numeric = typeof raw === "number" ? raw : Number(raw);
  return (
    <div className="chart-tooltip">
      <p className="font-data text-[0.65rem] uppercase tracking-[0.12em] text-muted">
        {label}
      </p>
      <p className="mt-1 text-sm text-foreground">
        <span className="text-muted">{valueLabel}: </span>
        <span className="font-data font-medium">
          {formatChartValue(numeric, valueFormat)}
        </span>
      </p>
    </div>
  );
}

export function TimeSeriesChart({
  data,
  valueLabel,
  valueFormat = "raw",
  color = "var(--accent)",
  variant = "line",
  height = 300,
}: {
  data: ChartPoint[];
  valueLabel: string;
  valueFormat?: ChartValueFormat;
  color?: string;
  variant?: ChartVariant;
  height?: number;
}) {
  if (data.length === 0) {
    return (
      <p className="px-3 py-10 text-sm text-muted">
        No series values available for this chart.
      </p>
    );
  }

  const gradientId = `fill-${valueLabel.replace(/[^a-zA-Z0-9]/g, "")}-${variant}`;
  const showZero =
    variant === "drawdown" ||
    valueFormat === "percent" ||
    data.some((point) => point.value < 0);

  const axisProps = {
    tick: { fontSize: 11, fill: "var(--muted)" },
    axisLine: false as const,
    tickLine: false as const,
  };

  const commonMargin = { top: 12, right: 16, left: 4, bottom: 4 };

  if (variant === "volume") {
    return (
      <div style={{ height }} className="w-full" role="img" aria-label={`${valueLabel} volume chart`}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={commonMargin}>
            <CartesianGrid stroke="var(--border)" strokeDasharray="2 8" vertical={false} />
            <XAxis
              dataKey="date"
              minTickGap={32}
              tickFormatter={shortDate}
              {...axisProps}
            />
            <YAxis
              width={56}
              tickFormatter={(value: number) => formatChartValue(value, valueFormat)}
              {...axisProps}
            />
            <Tooltip
              cursor={{ fill: "color-mix(in oklab, var(--accent) 10%, transparent)" }}
              content={
                <ChartTooltip valueLabel={valueLabel} valueFormat={valueFormat} />
              }
            />
            <Bar dataKey="value" radius={[1, 1, 0, 0]} isAnimationActive={false}>
              {data.map((point) => (
                <Cell
                  key={point.date}
                  fill={point.value >= 0 ? color : "var(--negative)"}
                  fillOpacity={0.78}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (variant === "area" || variant === "drawdown") {
    const fillColor = variant === "drawdown" ? "var(--negative)" : color;
    return (
      <div style={{ height }} className="w-full" role="img" aria-label={`${valueLabel} area chart`}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={commonMargin}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={fillColor} stopOpacity={0.35} />
                <stop offset="100%" stopColor={fillColor} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border)" strokeDasharray="2 8" vertical={false} />
            <XAxis
              dataKey="date"
              minTickGap={32}
              tickFormatter={shortDate}
              {...axisProps}
            />
            <YAxis
              width={64}
              tickFormatter={(value: number) => formatChartValue(value, valueFormat)}
              {...axisProps}
            />
            {showZero ? (
              <ReferenceLine y={0} stroke="var(--ink-soft)" strokeOpacity={0.35} />
            ) : null}
            <Tooltip
              content={
                <ChartTooltip valueLabel={valueLabel} valueFormat={valueFormat} />
              }
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke={fillColor}
              fill={`url(#${gradientId})`}
              strokeWidth={1.8}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return (
    <div style={{ height }} className="w-full" role="img" aria-label={`${valueLabel} line chart`}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={commonMargin}>
          <CartesianGrid stroke="var(--border)" strokeDasharray="2 8" vertical={false} />
          <XAxis
            dataKey="date"
            minTickGap={32}
            tickFormatter={shortDate}
            {...axisProps}
          />
          <YAxis
            width={64}
            tickFormatter={(value: number) => formatChartValue(value, valueFormat)}
            {...axisProps}
          />
          {showZero ? (
            <ReferenceLine y={0} stroke="var(--ink-soft)" strokeOpacity={0.35} />
          ) : null}
          <Tooltip
            content={
              <ChartTooltip valueLabel={valueLabel} valueFormat={valueFormat} />
            }
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            dot={false}
            strokeWidth={1.9}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
