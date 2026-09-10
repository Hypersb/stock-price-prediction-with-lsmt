export function StatePanel({
  title,
  message,
  action,
}: {
  title: string;
  message: string;
  action?: React.ReactNode;
}) {
  return (
    <div
      className="rounded-md border border-border bg-surface px-4 py-6"
      role="status"
    >
      <h3 className="text-sm font-semibold">{title}</h3>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{message}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

export function LoadingPanel({ label = "Loading research data…" }: { label?: string }) {
  return (
    <div
      className="animate-pulse rounded-md border border-border bg-surface px-4 py-8"
      role="status"
      aria-live="polite"
    >
      <div className="h-4 w-40 rounded bg-surface-muted" />
      <div className="mt-4 h-3 w-full max-w-xl rounded bg-surface-muted" />
      <p className="sr-only">{label}</p>
    </div>
  );
}
