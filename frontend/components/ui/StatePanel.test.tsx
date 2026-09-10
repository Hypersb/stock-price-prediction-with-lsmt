import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { StatePanel } from "@/components/ui/StatePanel";

describe("StatePanel", () => {
  it("renders empty and error messaging", () => {
    const html = renderToStaticMarkup(
      <StatePanel title="No experiments yet" message="Nothing stored." />,
    );
    expect(html).toContain("No experiments yet");
    expect(html).toContain("Nothing stored.");
  });
});
