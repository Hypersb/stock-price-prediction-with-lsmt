/** Helpers for Next.js search-param parsing used by research pages. */

import { appConfig } from "@/lib/env";

export function firstSearchValue(
  value: string | string[] | undefined,
): string | undefined {
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

/** Prefer a non-empty ticker; otherwise fall back to the platform default. */
export function resolveResearchSymbol(
  value: string | string[] | undefined,
  fallback: string = appConfig.defaultSymbol,
): string {
  const raw = firstSearchValue(value);
  const trimmed = raw?.trim() ?? "";
  return (trimmed || fallback).toUpperCase();
}

export function resolveSearchDate(
  value: string | string[] | undefined,
  fallback: string,
): string {
  const raw = firstSearchValue(value);
  const trimmed = raw?.trim() ?? "";
  return trimmed || fallback;
}
