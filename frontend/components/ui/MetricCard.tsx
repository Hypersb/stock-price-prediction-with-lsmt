export function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <article className="rounded-md border border-border bg-surface px-4 py-3">
      <p className="text-xs font-medium uppercase tracking-[0.08em] text-muted">
        {label}
      </p>
      <p className="mt-2 font-mono text-xl font-semibold tracking-tight">{value}</p>
      {hint ? <p className="mt-1 text-xs text-muted">{hint}</p> : null}
    </article>
  );
}
