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
      className="grid gap-3 rounded-md border border-border bg-surface p-4 md:grid-cols-[1fr_1fr_1fr_auto]"
    >
      <label className="block text-sm">
        <span className="mb-1 block text-muted">Ticker</span>
        <input
          className="w-full rounded-md border border-border bg-background px-3 py-2"
          value={symbol}
          onChange={(event) => setSymbol(event.target.value.toUpperCase())}
          name="symbol"
          aria-label="Ticker symbol"
          required
        />
      </label>
      <label className="block text-sm">
        <span className="mb-1 block text-muted">Start date</span>
        <input
          type="date"
          className="w-full rounded-md border border-border bg-background px-3 py-2"
          value={startDate}
          onChange={(event) => setStartDate(event.target.value)}
          name="start"
          required
        />
      </label>
      <label className="block text-sm">
        <span className="mb-1 block text-muted">End date</span>
        <input
          type="date"
          className="w-full rounded-md border border-border bg-background px-3 py-2"
          value={endDate}
          onChange={(event) => setEndDate(event.target.value)}
          name="end"
          required
        />
      </label>
      <div className="flex items-end">
        <button
          type="submit"
          className="w-full rounded-md bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-60 dark:text-background"
          disabled={pending}
        >
          {pending ? "Updating…" : "Apply"}
        </button>
      </div>
    </form>
  );
}
