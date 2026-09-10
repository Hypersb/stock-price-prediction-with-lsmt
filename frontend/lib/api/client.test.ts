import { afterEach, describe, expect, it, vi } from "vitest";

import { apiFetch } from "@/lib/api/client";
import { ApiError } from "@/types/api";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("apiFetch", () => {
  it("parses successful json responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: { get: () => "application/json" },
        json: async () => ({ status: "ok" }),
      }),
    );

    const result = await apiFetch<{ status: string }>("/health");
    expect(result.status).toBe("ok");
  });

  it("maps non-2xx payloads to ApiError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: "Not Found",
        headers: { get: () => "application/json" },
        json: async () => ({
          error: "not_found",
          detail: "experiment not found",
          code: "not_found",
        }),
      }),
    );

    await expect(apiFetch("/experiments/missing")).rejects.toMatchObject({
      name: "ApiError",
      status: 404,
      code: "not_found",
    } satisfies Partial<ApiError>);
  });

  it("surfaces network failures", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("failed to fetch")),
    );

    await expect(apiFetch("/health")).rejects.toMatchObject({
      status: 0,
      code: "network_error",
    });
  });
});
