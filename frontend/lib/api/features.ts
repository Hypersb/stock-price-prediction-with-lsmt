import { apiFetch } from "@/lib/api/client";
import type { FeatureResponse } from "@/types/api";

export function getFeatures(
  symbol: string,
  startDate: string,
  endDate: string,
  limit?: number,
) {
  return apiFetch<FeatureResponse>(
    `/features/${encodeURIComponent(symbol)}`,
    {},
    { start_date: startDate, end_date: endDate, limit },
  );
}
