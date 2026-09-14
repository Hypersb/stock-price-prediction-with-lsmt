import Link from "next/link";

import { HeroGraphic } from "@/components/brand/HeroGraphic";
import { StatePanel } from "@/components/ui/StatePanel";
import { getHealth, listExperiments, listBacktests, listModels } from "@/lib/api";
import { ApiError } from "@/types/api";

export default async function OverviewPage() {
  let healthLabel = "unknown";
  let experimentTotal = 0;
  let backtestTotal = 0;
  let modelCount = 0;
  let backendError: string | null = null;

  try {
    const [health, experiments, backtests, models] = await Promise.all([
      getHealth(),
      listExperiments({ limit: 5, offset: 0 }),
      listBacktests({ limit: 5, offset: 0 }),
      listModels(),
    ]);
    healthLabel = `${health.status} · ${health.version}`;
    experimentTotal = experiments.total;
    backtestTotal = backtests.total;
    modelCount = models.count;
  } catch (error) {
    backendError =
      error instanceof ApiError
        ? error.detail ?? error.message
        : "Backend unavailable.";
  }

  return (
    <div>
      <section className="border-b-2 border-border bg-surface">
        <div className="mx-auto grid min-h-[calc(100svh-3.5rem)] max-w-6xl lg:grid-cols-2">
          <div className="flex flex-col justify-end border-b-2 border-border px-4 py-12 sm:px-6 lg:border-b-0 lg:border-r-2 lg:py-16">
            <p className="font-display text-[clamp(4.5rem,14vw,8.5rem)] leading-[0.85] tracking-tight">
              fold
            </p>
            <h1 className="mt-6 max-w-md text-2xl font-extrabold leading-tight sm:text-3xl">
              Stock research with teeth.
            </h1>
            <p className="mt-4 max-w-md text-base leading-7 text-muted">
              Prices, features, walk-forward folds, and costed backtests — no
              fake wins, no soft dashboard fluff.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/market" className="btn-primary">
                Open market
              </Link>
              <Link href="/backtests" className="btn-ghost">
                Backtests
              </Link>
            </div>
          </div>
          <div className="bg-foreground p-3 sm:p-4">
            <HeroGraphic />
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        {backendError ? (
          <StatePanel title="API offline" message={backendError} />
        ) : (
          <dl className="grid border-2 border-border bg-surface sm:grid-cols-4">
            {[
              ["API", healthLabel],
              ["Models", String(modelCount)],
              ["Experiments", String(experimentTotal)],
              ["Backtests", String(backtestTotal)],
            ].map(([label, value], index) => (
              <div
                key={label}
                className={`px-4 py-5 ${index < 3 ? "border-b-2 border-border sm:border-b-0 sm:border-r-2" : ""}`}
              >
                <dt className="text-[0.68rem] font-extrabold uppercase tracking-[0.12em] text-muted">
                  {label}
                </dt>
                <dd className="font-data mt-2 text-xl font-semibold">{value}</dd>
              </div>
            ))}
          </dl>
        )}
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-16 sm:px-6">
        <h2 className="font-display text-3xl tracking-tight sm:text-4xl">
          Start here
        </h2>
        <div className="section-rule mt-4" />
        <ol className="mt-8 border-2 border-border bg-surface">
          {[
            ["01", "Market", "/market"],
            ["02", "Features", "/features"],
            ["03", "Experiments", "/experiments"],
            ["04", "Walk-forward", "/walk-forward"],
            ["05", "Backtests", "/backtests"],
          ].map(([index, title, href], i, arr) => (
            <li
              key={href}
              className={i < arr.length - 1 ? "border-b-2 border-border" : ""}
            >
              <Link
                href={href}
                className="flex items-baseline gap-4 px-4 py-4 hover:bg-accent-muted sm:gap-8"
              >
                <span className="font-data text-sm text-accent">{index}</span>
                <span className="text-lg font-extrabold uppercase">{title}</span>
              </Link>
            </li>
          ))}
        </ol>
      </section>

      <footer className="border-t-2 border-border bg-foreground px-4 py-8 text-surface sm:px-6">
        <div className="mx-auto flex max-w-6xl items-end justify-between gap-4">
          <p className="font-display text-3xl">fold</p>
          <p className="max-w-xs text-right text-xs leading-5 text-[#bdbdbd]">
            Historical simulation only. No claim of future performance.
          </p>
        </div>
      </footer>
    </div>
  );
}
