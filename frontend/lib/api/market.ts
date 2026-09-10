import { apiFetch } from "@/lib/api/client";
import type {
  AnalysisSummaryResponse,
  HealthResponse,
  MarketDataResponse,
} from "@/types/api";

export function getHealth() {
  return apiFetch<HealthResponse>("/health");
}

export function getMarketData(symbol: string, startDate: string, endDate: string) {
  return apiFetch<MarketDataResponse>(
    `/market-data/${encodeURIComponent(symbol)}`,
    {},
    { start_date: startDate, end_date: endDate },
  );
}

export function getAnalysisSummary(
  symbol: string,
  startDate: string,
  endDate: string,
) {
  return apiFetch<AnalysisSummaryResponse>(
    `/analysis/${encodeURIComponent(symbol)}/summary`,
    {},
    { start_date: startDate, end_date: endDate },
  );
}
