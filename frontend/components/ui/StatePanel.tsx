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
    <div className="border-2 border-border bg-surface p-5" role="status">
      <div className="section-rule mb-4" />
      <h3 className="font-display text-2xl tracking-tight">{title}</h3>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">{message}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

export function LoadingPanel({ label = "Loading research data…" }: { label?: string }) {
  return (
    <div
      className="animate-pulse border-2 border-border bg-surface p-5"
      role="status"
      aria-live="polite"
    >
      <div className="h-3 w-36 bg-surface-muted" />
      <div className="mt-4 h-3 w-full max-w-lg bg-surface-muted" />
      <p className="sr-only">{label}</p>
    </div>
  );
}
