import type { Metadata } from "next";

export const metadata: Metadata = { title: "Models" };

export default function ModelsPage() {
  return (
    <section className="space-y-2">
      <h2 className="text-2xl font-semibold tracking-tight">Models</h2>
      <p className="max-w-2xl text-sm leading-6 text-muted">
        Supported research model families will be listed from the backend catalog.
      </p>
    </section>
  );
}
