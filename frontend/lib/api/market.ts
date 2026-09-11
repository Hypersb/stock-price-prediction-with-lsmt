import { apiFetch } from "@/lib/api/client";
import type {
  AnalysisSummaryResponse,
  HealthResponse,
  MarketDataResponse,
  ReadinessResponse,
} from "@/types/api";

export function getHealth() {
  return apiFetch<HealthResponse>("/health");
}

export function getReady() {
  return apiFetch<ReadinessResponse>("/ready");
}

export function getMarketData(
  symbol: string,
  startDate: string,
  endDate: string,
  options?: { limit?: number; offset?: number },
) {
  return apiFetch<MarketDataResponse>(
    `/market-data/${encodeURIComponent(symbol)}`,
    {},
    {
      start_date: startDate,
      end_date: endDate,
      limit: options?.limit,
      offset: options?.offset,
    },
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
