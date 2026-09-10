/**
 * Frontend environment helpers.
 * Only NEXT_PUBLIC_* values are available in the browser.
 */

export function getApiBaseUrl(): string {
  const value = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!value) {
    return "http://localhost:8000";
  }
  return value.replace(/\/$/, "");
}

export const appConfig = {
  defaultSymbol: "AAPL",
  apiV1Prefix: "/api/v1",
} as const;
