export function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  showMotif?: boolean;
}) {
  return (
    <header className="border-2 border-border bg-surface p-5 sm:p-6">
      {eyebrow ? (
        <p className="text-[0.68rem] font-extrabold uppercase tracking-[0.14em] text-accent">
          {eyebrow}
        </p>
      ) : null}
      <h2 className="font-display mt-2 text-4xl tracking-tight sm:text-5xl">
        {title}
      </h2>
      {description ? (
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted sm:text-base">
          {description}
        </p>
      ) : null}
      <div className="section-rule mt-5" />
    </header>
  );
}
