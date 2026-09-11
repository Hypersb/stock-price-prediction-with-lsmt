import { describe, expect, it } from "vitest";

import { appConfig, getApiBaseUrl } from "@/lib/env";

describe("getApiBaseUrl", () => {
  it("defaults to local development backend", () => {
    const previous = process.env.NEXT_PUBLIC_API_BASE_URL;
    delete process.env.NEXT_PUBLIC_API_BASE_URL;
    try {
      expect(getApiBaseUrl()).toBe(appConfig.defaultApiBaseUrl);
    } finally {
      if (previous === undefined) {
        delete process.env.NEXT_PUBLIC_API_BASE_URL;
      } else {
        process.env.NEXT_PUBLIC_API_BASE_URL = previous;
      }
    }
  });

  it("rejects non-absolute urls", () => {
    const previous = process.env.NEXT_PUBLIC_API_BASE_URL;
    process.env.NEXT_PUBLIC_API_BASE_URL = "localhost:8000";
    try {
      expect(() => getApiBaseUrl()).toThrow(/absolute http\(s\) URL/i);
    } finally {
      if (previous === undefined) {
        delete process.env.NEXT_PUBLIC_API_BASE_URL;
      } else {
        process.env.NEXT_PUBLIC_API_BASE_URL = previous;
      }
    }
  });
});
