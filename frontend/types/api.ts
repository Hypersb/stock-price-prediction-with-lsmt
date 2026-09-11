/** Types aligned with FastAPI /api/v1 response contracts. */

export type HealthResponse = {
  status: string;
  service: string;
  version: string;
  environment: string;
};

export type DependencyCheck = {
  status: "ok" | "unavailable" | "unconfigured";
  detail: string;
};

export type ReadinessResponse = {
  status: "ready" | "not_ready";
  service: string;
  checks: Record<string, DependencyCheck>;
};

export type OhlcvObservation = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type MarketDataResponse = {
  symbol: string;
  start_date: string;
  end_date: string;
  count: number;
  data: OhlcvObservation[];
};

export type AnalysisSummaryResponse = {
  symbol: string;
  start_date: string;
  end_date: string;
  observation_count: number;
  return_count: number;
  mean_return: number | null;
  median_return: number | null;
  volatility: number | null;
  cumulative_return: number | null;
  maximum_drawdown: number | null;
};

export type FeatureObservation = {
  date: string;
  values: Record<string, number | null>;
};

export type FeatureResponse = {
  symbol: string;
  start_date: string;
  end_date: string;
  feature_names: string[];
  feature_count: number;
  observation_count: number;
  returned_rows: number;
  features: FeatureObservation[];
};

export type TaskType = "regression" | "classification";

export type SupportedModel = {
  name: string;
  family: string;
  tasks: TaskType[];
  trained: boolean;
  description: string;
};

export type ModelCatalogResponse = {
  models: SupportedModel[];
  count: number;
};

export type ExperimentSummary = {
  id: string;
  created_at: string;
  symbol: string;
  task: string;
  model_name: string;
  target_name: string;
  forecast_horizon: number;
  status: string;
  feature_count: number;
  best_epoch: number | null;
  best_validation_loss: number | null;
  checkpoint_reference: string | null;
};

export type ExperimentDetail = ExperimentSummary & {
  lookback: number | null;
  seed: number | null;
  feature_names: string[] | null;
  model_configuration: Record<string, unknown> | null;
  training_configuration: Record<string, unknown> | null;
  train_start: string | null;
  train_end: string | null;
  validation_start: string | null;
  validation_end: string | null;
  test_start: string | null;
  test_end: string | null;
  updated_at: string;
};

export type ExperimentListResponse = {
  items: ExperimentSummary[];
  total: number;
  limit: number;
  offset: number;
};

export type ExperimentMetricResponse = {
  id: string;
  split: string;
  metric_name: string;
  metric_value: number | null;
};

export type ExperimentMetricsResponse = {
  experiment_id: string;
  metrics: ExperimentMetricResponse[];
};

export type WalkForwardFoldResponse = {
  fold_number: number;
  train_start: string;
  train_end: string;
  validation_start: string | null;
  validation_end: string | null;
  test_start: string;
  test_end: string;
  train_count: number;
  validation_count: number;
  test_count: number;
  best_epoch: number | null;
  fold_metrics: Record<string, number | null> | null;
};

export type WalkForwardRunResponse = {
  id: string;
  created_at: string;
  experiment_id: string | null;
  symbol: string;
  model_name: string;
  task: string;
  window_type: string;
  initial_train_size: number;
  validation_size: number;
  test_size: number;
  step_size: number;
  gap: number;
  forecast_horizon: number;
  folds: WalkForwardFoldResponse[];
};

export type PersistedBacktestSummary = {
  id: string;
  created_at: string;
  symbol: string;
  model_name: string;
  task: string;
  strategy_mode: string;
  sample_kind: string;
  observation_count: number;
  start_date: string | null;
  end_date: string | null;
};

export type PersistedBacktestListResponse = {
  items: PersistedBacktestSummary[];
  total: number;
  limit: number;
  offset: number;
};

export type PersistedBacktestMetric = {
  metric_name: string;
  metric_value: number | null;
};

export type PersistedEquityPoint = {
  date: string;
  position: number | null;
  gross_return: number | null;
  cost: number | null;
  net_return: number | null;
  equity: number | null;
};

export type PersistedBacktestDetail = PersistedBacktestSummary & {
  experiment_id: string | null;
  walk_forward_run_id: string | null;
  signal_threshold: number;
  transaction_cost_bps: number;
  slippage_bps: number;
  initial_capital: number;
  metrics: PersistedBacktestMetric[];
  equity_curve: PersistedEquityPoint[];
};

export type ErrorResponse = {
  error: string;
  detail: string;
  code?: string | null;
};

export class ApiError extends Error {
  status: number;
  code?: string;
  detail?: string;

  constructor(message: string, status: number, code?: string, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.detail = detail;
  }
}
