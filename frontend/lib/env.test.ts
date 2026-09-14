import { describe, expect, it } from "vitest";

import { appConfig, getApiBaseUrl } from "@/lib/env";

describe("getApiBaseUrl", () => {
  it("defaults to local development backend", () => {
    const previous = process.env.NEXT_PUBLIC_API_BASE_URL;
    const previousInternal = process.env.API_INTERNAL_BASE_URL;
    delete process.env.NEXT_PUBLIC_API_BASE_URL;
    delete process.env.API_INTERNAL_BASE_URL;
    try {
      expect(getApiBaseUrl()).toBe(appConfig.defaultApiBaseUrl);
    } finally {
      if (previous === undefined) {
        delete process.env.NEXT_PUBLIC_API_BASE_URL;
      } else {
        process.env.NEXT_PUBLIC_API_BASE_URL = previous;
      }
      if (previousInternal === undefined) {
        delete process.env.API_INTERNAL_BASE_URL;
      } else {
        process.env.API_INTERNAL_BASE_URL = previousInternal;
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

  it("prefers server-only API_INTERNAL_BASE_URL during ssr", () => {
    const previousPublic = process.env.NEXT_PUBLIC_API_BASE_URL;
    const previousInternal = process.env.API_INTERNAL_BASE_URL;
    process.env.NEXT_PUBLIC_API_BASE_URL = "http://localhost:8000";
    process.env.API_INTERNAL_BASE_URL = "http://backend:8000";
    try {
      expect(typeof window).toBe("undefined");
      expect(getApiBaseUrl()).toBe("http://backend:8000");
    } finally {
      if (previousPublic === undefined) {
        delete process.env.NEXT_PUBLIC_API_BASE_URL;
      } else {
        process.env.NEXT_PUBLIC_API_BASE_URL = previousPublic;
      }
      if (previousInternal === undefined) {
        delete process.env.API_INTERNAL_BASE_URL;
      } else {
        process.env.API_INTERNAL_BASE_URL = previousInternal;
      }
    }
  });
});
