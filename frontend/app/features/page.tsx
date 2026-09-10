import type { Metadata } from "next";

export const metadata: Metadata = { title: "Features" };

export default function FeaturesPage() {
  return (
    <section className="space-y-2">
      <h2 className="text-2xl font-semibold tracking-tight">Features</h2>
      <p className="max-w-2xl text-sm leading-6 text-muted">
        Feature explorer placeholder for engineered quantitative inputs.
      </p>
    </section>
  );
}
