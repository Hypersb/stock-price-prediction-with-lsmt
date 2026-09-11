/**
 * Frontend environment helpers.
 * Only NEXT_PUBLIC_* values are available in the browser.
 * Never place DATABASE_URL, private API keys, or secrets in NEXT_PUBLIC_*.
 */

const DEFAULT_API_BASE_URL = "http://localhost:8000";

export function getApiBaseUrl(): string {
  const value = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!value) {
    return DEFAULT_API_BASE_URL;
  }
  const normalized = value.replace(/\/$/, "");
  if (!/^https?:\/\//i.test(normalized)) {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL must be an absolute http(s) URL",
    );
  }
  return normalized;
}

export const appConfig = {
  defaultSymbol: "AAPL",
  apiV1Prefix: "/api/v1",
  defaultApiBaseUrl: DEFAULT_API_BASE_URL,
} as const;
