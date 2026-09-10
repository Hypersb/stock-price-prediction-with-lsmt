import type { Metadata } from "next";

export const metadata: Metadata = { title: "Market" };

export default function MarketPage() {
  return (
    <Placeholder
      title="Market"
      body="Market overview controls and charts will load from the FastAPI market-data and analysis endpoints."
    />
  );
}

function Placeholder({ title, body }: { title: string; body: string }) {
  return (
    <section className="space-y-2">
      <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
      <p className="max-w-2xl text-sm leading-6 text-muted">{body}</p>
    </section>
  );
}
