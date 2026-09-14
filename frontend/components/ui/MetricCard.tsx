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
    <article className="border-2 border-border bg-surface p-4">
      <p className="text-[0.68rem] font-extrabold uppercase tracking-[0.12em] text-muted">
        {label}
      </p>
      <p className="font-data mt-2 text-2xl font-semibold tracking-tight">
        {value}
      </p>
      {hint ? <p className="mt-1 text-xs leading-5 text-muted">{hint}</p> : null}
    </article>
  );
}
