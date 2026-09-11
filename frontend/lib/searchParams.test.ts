import { describe, expect, it } from "vitest";

import {
  resolveResearchSymbol,
  resolveSearchDate,
} from "@/lib/searchParams";

describe("resolveResearchSymbol", () => {
  it("falls back when the symbol query is empty", () => {
    expect(resolveResearchSymbol("")).toBe("AAPL");
    expect(resolveResearchSymbol("   ")).toBe("AAPL");
    expect(resolveResearchSymbol(undefined)).toBe("AAPL");
  });

  it("normalizes lowercase tickers", () => {
    expect(resolveResearchSymbol("msft")).toBe("MSFT");
  });
});

describe("resolveSearchDate", () => {
  it("falls back when the date query is empty", () => {
    expect(resolveSearchDate("", "2024-01-01")).toBe("2024-01-01");
    expect(resolveSearchDate(undefined, "2024-01-01")).toBe("2024-01-01");
  });
});
