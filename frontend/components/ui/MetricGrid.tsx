export function MetricGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid gap-x-8 gap-y-6 border-y border-border py-6 sm:grid-cols-2 xl:grid-cols-4">
      {children}
    </div>
  );
}
