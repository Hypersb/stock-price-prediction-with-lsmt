import type { Metadata } from "next";

export const metadata: Metadata = { title: "Experiments" };

export default function ExperimentsPage() {
  return (
    <section className="space-y-2">
      <h2 className="text-2xl font-semibold tracking-tight">Experiments</h2>
      <p className="max-w-2xl text-sm leading-6 text-muted">
        Stored experiment history will appear here when persistence records exist.
      </p>
    </section>
  );
}
