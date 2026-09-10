/** Brief research notes for common engineered features. */

const NOTES: Record<string, string> = {
  simple_return: "One-period simple return from close prices.",
  log_return: "One-period logarithmic return from close prices.",
  rsi_14: "14-period relative strength index. A research feature, not a trade signal.",
  atr_14: "14-period average true range measuring recent range.",
};

export function describeFeature(name: string): string {
  if (NOTES[name]) {
    return NOTES[name];
  }
  if (name.startsWith("return_lag_")) {
    return "Lagged simple return used as a historical predictor input.";
  }
  if (name.startsWith("momentum_")) {
    return "Price momentum over a trailing window. Research feature only.";
  }
  if (name.startsWith("sma_")) {
    return "Simple moving average of close prices.";
  }
  if (name.startsWith("ema_")) {
    return "Exponential moving average of close prices.";
  }
  if (name.includes("volatility") || name.startsWith("vol_")) {
    return "Trailing realized volatility feature.";
  }
  if (name.startsWith("volume") || name.includes("volume")) {
    return "Volume-based research feature.";
  }
  if (name.startsWith("macd")) {
    return "MACD family feature derived from EMAs. Not an automatic buy/sell signal.";
  }
  return "Engineered quantitative feature from the research pipeline.";
}
