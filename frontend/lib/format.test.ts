import { describe, expect, it } from "vitest";

import { formatNumber, formatPercent, formatPrice } from "@/lib/format";

describe("format helpers", () => {
  it("formats percentages without false precision", () => {
    expect(formatPercent(0.12345)).toBe("12.35%");
    expect(formatPercent(null)).toBe("—");
  });

  it("formats prices and numbers", () => {
    expect(formatPrice(101.2)).toContain("101.20");
    expect(formatNumber(null)).toBe("—");
  });
});
