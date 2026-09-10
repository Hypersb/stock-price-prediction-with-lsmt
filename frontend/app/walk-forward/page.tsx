import type { Metadata } from "next";

export const metadata: Metadata = { title: "Walk Forward" };

export default function WalkForwardPage() {
  return (
    <section className="space-y-2">
      <h2 className="text-2xl font-semibold tracking-tight">Walk Forward</h2>
      <p className="max-w-2xl text-sm leading-6 text-muted">
        Walk-forward fold analytics will load from persisted validation runs.
      </p>
    </section>
  );
}
