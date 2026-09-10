export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col justify-center gap-4 px-6 py-16">
      <p className="text-sm font-medium uppercase tracking-[0.14em] text-muted">
        Stock Price Prediction with LSTM
      </p>
      <h1 className="text-3xl font-semibold tracking-tight">
        Quantitative research dashboard
      </h1>
      <p className="max-w-2xl text-base leading-7 text-muted">
        Frontend foundation for the research platform. Navigation, API client,
        and analytical views will be added in subsequent increments.
      </p>
    </main>
  );
}
