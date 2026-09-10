import { apiFetch } from "@/lib/api/client";
import type {
  PersistedBacktestDetail,
  PersistedBacktestListResponse,
} from "@/types/api";

export function listBacktests(params?: {
  limit?: number;
  offset?: number;
  symbol?: string;
}) {
  return apiFetch<PersistedBacktestListResponse>("/backtests", {}, params);
}

export function getBacktest(backtestId: string) {
  return apiFetch<PersistedBacktestDetail>(
    `/backtests/${encodeURIComponent(backtestId)}`,
  );
}
