import { apiFetch } from "@/lib/api/client";
import type {
  ExperimentDetail,
  ExperimentListResponse,
  ExperimentMetricsResponse,
  ExperimentRelatedResponse,
  WalkForwardRunResponse,
} from "@/types/api";

export function listExperiments(params?: {
  limit?: number;
  offset?: number;
  symbol?: string;
}) {
  return apiFetch<ExperimentListResponse>("/experiments", {}, params);
}

export function getExperiment(experimentId: string) {
  return apiFetch<ExperimentDetail>(`/experiments/${encodeURIComponent(experimentId)}`);
}

export function getExperimentMetrics(experimentId: string) {
  return apiFetch<ExperimentMetricsResponse>(
    `/experiments/${encodeURIComponent(experimentId)}/metrics`,
  );
}

export function getExperimentRelated(experimentId: string) {
  return apiFetch<ExperimentRelatedResponse>(
    `/experiments/${encodeURIComponent(experimentId)}/related`,
  );
}

export function getWalkForwardRun(runId: string) {
  return apiFetch<WalkForwardRunResponse>(
    `/walk-forward/${encodeURIComponent(runId)}`,
  );
}
