import { getApiBaseUrl, appConfig } from "@/lib/env";
import { ApiError } from "@/types/api";

type QueryValue = string | number | boolean | null | undefined;

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  query?: Record<string, QueryValue>,
): Promise<T> {
  const base = getApiBaseUrl();
  const url = new URL(`${appConfig.apiV1Prefix}${path}`, `${base}/`);

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null || value === "") {
        continue;
      }
      url.searchParams.set(key, String(value));
    }
  }

  let response: Response;
  try {
    response = await fetch(url.toString(), {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.headers ?? {}),
      },
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      "unable to reach the research api",
      0,
      "network_error",
      "network request failed",
    );
  }

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? String((payload as { detail: unknown }).detail)
        : response.statusText || "request failed";
    const code =
      payload && typeof payload === "object" && "code" in payload
        ? String((payload as { code: unknown }).code)
        : undefined;
    throw new ApiError(detail, response.status, code, detail);
  }

  return payload as T;
}
