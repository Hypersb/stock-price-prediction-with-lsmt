export function ChartFrame({
  title,
  subtitle,
  meta,
  children,
}: {
  title: string;
  subtitle?: string;
  meta?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="chart-frame">
      <div className="flex flex-wrap items-end justify-between gap-3 border-b-2 border-border px-4 py-3">
        <div>
          <h3 className="text-sm font-extrabold uppercase tracking-wide">{title}</h3>
          {subtitle ? (
            <p className="mt-1 max-w-2xl text-xs leading-5 text-muted">{subtitle}</p>
          ) : null}
        </div>
        {meta ? (
          <p className="font-data text-[0.7rem] uppercase tracking-[0.1em] text-accent">
            {meta}
          </p>
        ) : null}
      </div>
      <div className="px-2 pb-2 pt-3 sm:px-3">{children}</div>
    </section>
  );
}
