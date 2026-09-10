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
      className="flex flex-col gap-3 rounded-md border border-border bg-surface p-4 sm:flex-row sm:items-end"
    >
      <label className="block flex-1 text-sm">
        <span className="mb-1 block text-muted">Walk-forward run id</span>
        <input
          className="w-full rounded-md border border-border bg-background px-3 py-2 font-mono text-sm"
          value={runId}
          onChange={(event) => setRunId(event.target.value)}
          placeholder="uuid from persistence api"
          aria-label="Walk-forward run id"
        />
      </label>
      <button
        type="submit"
        className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-60 dark:text-background"
        disabled={pending}
      >
        {pending ? "Loading…" : "Load run"}
      </button>
    </form>
  );
}
