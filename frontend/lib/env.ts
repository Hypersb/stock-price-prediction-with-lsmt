/**
 * Frontend environment helpers.
 *
 * CLIENT-EXPOSED: only NEXT_PUBLIC_* values may enter browser bundles.
 * SERVER-ONLY: API_INTERNAL_BASE_URL may be used during SSR/Docker networking.
 *
 * Never place DATABASE_URL, MARKET_DATA_API_KEY, or other secrets in
 * NEXT_PUBLIC_* variables.
 */

const DEFAULT_API_BASE_URL = "http://localhost:8000";

function normalizeApiBaseUrl(value: string): string {
  const normalized = value.replace(/\/$/, "");
  if (!/^https?:\/\//i.test(normalized)) {
    throw new Error(
      "API base URL must be an absolute http(s) URL",
    );
  }
  return normalized;
}

/**
 * Resolve the FastAPI origin for API calls.
 * On the server, prefer API_INTERNAL_BASE_URL when set (Docker Compose SSR).
 * In the browser, only NEXT_PUBLIC_API_BASE_URL is available.
 */
export function getApiBaseUrl(): string {
  if (typeof window === "undefined") {
    const internal = process.env.API_INTERNAL_BASE_URL?.trim();
    if (internal) {
      return normalizeApiBaseUrl(internal);
    }
  }

  const value = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!value) {
    return DEFAULT_API_BASE_URL;
  }
  return normalizeApiBaseUrl(value);
}

/** Non-secret frontend configuration defaults (not experiment parameters). */
export const appConfig = {
  defaultSymbol: "AAPL",
  apiV1Prefix: "/api/v1",
  defaultApiBaseUrl: DEFAULT_API_BASE_URL,
} as const;
