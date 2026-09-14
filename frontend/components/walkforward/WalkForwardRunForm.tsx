"use client";

import { FormEvent, useState, useTransition } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export function WalkForwardRunForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [runId, setRunId] = useState(searchParams.get("run_id") ?? "");
  const [pending, startTransition] = useTransition();

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const params = new URLSearchParams();
    if (runId.trim()) {
      params.set("run_id", runId.trim());
    }
    startTransition(() => {
      router.push(`/walk-forward?${params.toString()}`);
    });
  }

  return (
    <form
      onSubmit={onSubmit}
      className="flex flex-col gap-4 border-y border-border py-5 sm:flex-row sm:items-end"
    >
      <label className="block flex-1 text-sm">
        <span className="mb-2 block text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-muted">
          Walk-forward run id
        </span>
        <input
          className="field-input font-data text-sm"
          value={runId}
          onChange={(event) => setRunId(event.target.value)}
          placeholder="uuid from the persistence API"
          aria-label="Walk-forward run id"
        />
      </label>
      <button type="submit" className="btn-primary" disabled={pending}>
        {pending ? "Loading…" : "Load run"}
      </button>
    </form>
  );
}
