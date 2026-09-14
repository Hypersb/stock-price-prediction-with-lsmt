"use client";

import { FormEvent, useMemo, useState, useTransition } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { appConfig } from "@/lib/env";
import { defaultDateRange } from "@/lib/format";

export function ResearchControls({
  basePath,
}: {
  basePath: string;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const defaults = useMemo(() => defaultDateRange(), []);
  const [pending, startTransition] = useTransition();

  const [symbol, setSymbol] = useState(() => {
    const raw = searchParams.get("symbol");
    return raw && raw.trim() ? raw.trim().toUpperCase() : appConfig.defaultSymbol;
  });
  const [startDate, setStartDate] = useState(
    () => searchParams.get("start")?.trim() || defaults.startDate,
  );
  const [endDate, setEndDate] = useState(
    () => searchParams.get("end")?.trim() || defaults.endDate,
  );

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const params = new URLSearchParams();
    const nextSymbol = symbol.trim().toUpperCase() || appConfig.defaultSymbol;
    params.set("symbol", nextSymbol);
    params.set("start", startDate || defaults.startDate);
    params.set("end", endDate || defaults.endDate);
    startTransition(() => {
      router.push(`${basePath}?${params.toString()}`);
    });
  }

  return (
    <form
      onSubmit={onSubmit}
      className="grid gap-4 border-2 border-border bg-surface p-4 md:grid-cols-[1fr_1fr_1fr_auto] md:items-end"
    >
      <label className="block text-sm">
        <span className="mb-2 block text-[0.68rem] font-extrabold uppercase tracking-[0.12em] text-muted">
          Ticker
        </span>
        <input
          className="field-input font-data"
          value={symbol}
          onChange={(event) => setSymbol(event.target.value.toUpperCase())}
          name="symbol"
          aria-label="Ticker symbol"
          required
        />
      </label>
      <label className="block text-sm">
        <span className="mb-2 block text-[0.68rem] font-extrabold uppercase tracking-[0.12em] text-muted">
          Start
        </span>
        <input
          type="date"
          className="field-input font-data"
          value={startDate}
          onChange={(event) => setStartDate(event.target.value)}
          name="start"
          required
        />
      </label>
      <label className="block text-sm">
        <span className="mb-2 block text-[0.68rem] font-extrabold uppercase tracking-[0.12em] text-muted">
          End
        </span>
        <input
          type="date"
          className="field-input font-data"
          value={endDate}
          onChange={(event) => setEndDate(event.target.value)}
          name="end"
          required
        />
      </label>
      <button type="submit" className="btn-primary w-full md:w-auto" disabled={pending}>
        {pending ? "Updating…" : "Apply"}
      </button>
    </form>
  );
}
