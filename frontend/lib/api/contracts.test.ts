import { describe, expect, it } from "vitest";

import { FRONTEND_API_ROUTES } from "@/lib/api/contracts";

describe("frontend api contracts", () => {
  it("lists dashboard routes under /api/v1", () => {
    expect(FRONTEND_API_ROUTES.length).toBeGreaterThanOrEqual(10);
    for (const route of FRONTEND_API_ROUTES) {
      expect(route.method).toBe("GET");
      expect(route.path.startsWith("/api/v1/")).toBe(true);
    }
  });

  it("includes persistence and market research routes", () => {
    const paths = FRONTEND_API_ROUTES.map((route) => route.path);
    expect(paths).toContain("/api/v1/health");
    expect(paths).toContain("/api/v1/market-data/{symbol}");
    expect(paths).toContain("/api/v1/experiments");
    expect(paths).toContain("/api/v1/walk-forward/{run_id}");
    expect(paths).toContain("/api/v1/backtests");
  });
});
