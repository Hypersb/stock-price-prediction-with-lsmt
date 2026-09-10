import { describe, expect, it } from "vitest";

import { describeFeature } from "@/lib/featureNotes";

describe("describeFeature", () => {
  it("avoids buy/sell language for indicators", () => {
    expect(describeFeature("rsi_14").toLowerCase()).not.toContain("buy");
    expect(describeFeature("rsi_14").toLowerCase()).not.toContain("sell");
    expect(describeFeature("macd").toLowerCase()).toContain("not an automatic");
  });
});
