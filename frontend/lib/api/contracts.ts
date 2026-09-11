/**
 * Dashboard-consumed API routes. Kept in sync with
 * backend/app/contracts/frontend_api.py via backend contract tests and this list.
 */
export const FRONTEND_API_ROUTES = [
  { method: "GET", path: "/api/v1/health" },
  { method: "GET", path: "/api/v1/market-data/{symbol}" },
  { method: "GET", path: "/api/v1/analysis/{symbol}/summary" },
  { method: "GET", path: "/api/v1/features/{symbol}" },
  { method: "GET", path: "/api/v1/models" },
  { method: "GET", path: "/api/v1/experiments" },
  { method: "GET", path: "/api/v1/experiments/{experiment_id}" },
  { method: "GET", path: "/api/v1/experiments/{experiment_id}/metrics" },
  { method: "GET", path: "/api/v1/walk-forward/{run_id}" },
  { method: "GET", path: "/api/v1/backtests" },
  { method: "GET", path: "/api/v1/backtests/{backtest_id}" },
] as const;
