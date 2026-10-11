import { afterEach, describe, expect, it, vi } from "vitest";
import { AppInitializationError, loadAppEnv } from "@/core/env";

const VALID_ENV = {
  NODE_ENV: "test",
  NEXT_PUBLIC_SUPABASE_URL: "https://project.example.supabase.co/path",
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "sb_publishable_example",
};

function legacySupabaseKey(role: "anon" | "service_role"): string {
  const payload = Buffer.from(JSON.stringify({ role })).toString("base64url");
  return `header.${payload}.signature`;
}

afterEach(() => vi.restoreAllMocks());

describe("loadAppEnv", () => {
  it("normalizes the Supabase URL and returns a frozen public configuration", () => {
    const result = loadAppEnv(VALID_ENV);
    expect(result).toEqual({
      nodeEnvironment: "test",
      supabase: {
        url: "https://project.example.supabase.co",
        publishableKey: "sb_publishable_example",
      },
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.supabase)).toBe(true);
  });

  it("uses development when NODE_ENV is absent", () => {
    const { NODE_ENV: _nodeEnvironment, ...source } = VALID_ENV;
    expect(loadAppEnv(source).nodeEnvironment).toBe("development");
  });

  it("uses development when NODE_ENV is empty", () => {
    expect(loadAppEnv({ ...VALID_ENV, NODE_ENV: "" }).nodeEnvironment).toBe("development");
  });

  it.each(["development", "test", "production"] as const)("accepts NODE_ENV %s", (nodeEnvironment) => {
    expect(loadAppEnv({ ...VALID_ENV, NODE_ENV: nodeEnvironment }).nodeEnvironment).toBe(nodeEnvironment);
  });

  it("reports all missing required names without logging their values", () => {
    const errorLog = vi.spyOn(console, "error").mockImplementation(() => undefined);
    expect(() => loadAppEnv({ NODE_ENV: "test" })).toThrowError(AppInitializationError);
    try {
      loadAppEnv({ NODE_ENV: "test" });
    } catch (error) {
      expect(error).toMatchObject({
        code: "APP_INITIALIZATION_FAILED",
        missingVariables: ["NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", "NEXT_PUBLIC_SUPABASE_URL"],
      });
      expect((error as Error).message).toContain("APP_INITIALIZATION_FAILED");
    }
    expect(errorLog).toHaveBeenCalledTimes(2);
    expect(errorLog.mock.calls[0]?.[0]).not.toContain("secret");
  });

  it.each(["", " change-me ", "YOUR-PROJECT-URL"])("rejects missing or placeholder values: %s", (value) => {
    expect(() => loadAppEnv({ ...VALID_ENV, NEXT_PUBLIC_SUPABASE_URL: value }))
      .toThrowError(/APP_INITIALIZATION_FAILED: Missing required environment variable/);
  });

  it("rejects unsupported NODE_ENV values", () => {
    expect(() => loadAppEnv({ ...VALID_ENV, NODE_ENV: "staging" }))
      .toThrowError(/NODE_ENV must be/);
  });

  it("rejects malformed URLs", () => {
    expect(() => loadAppEnv({ ...VALID_ENV, NEXT_PUBLIC_SUPABASE_URL: "not-a-url" }))
      .toThrowError(/must be a valid absolute URL/);
  });

  it("allows local HTTP URLs outside production", () => {
    const result = loadAppEnv({
      ...VALID_ENV,
      NEXT_PUBLIC_SUPABASE_URL: "http://localhost:54321",
    });
    expect(result.supabase.url).toBe("http://localhost:54321");
  });

  it("allows a loopback IP over HTTP outside production", () => {
    const result = loadAppEnv({
      ...VALID_ENV,
      NEXT_PUBLIC_SUPABASE_URL: "http://127.0.0.1:54321",
    });
    expect(result.supabase.url).toBe("http://127.0.0.1:54321");
  });

  it.each(["http://example.supabase.co", "ftp://example.supabase.co"])("rejects non-HTTPS non-local URLs: %s", (url) => {
    expect(() => loadAppEnv({ ...VALID_ENV, NEXT_PUBLIC_SUPABASE_URL: url }))
      .toThrowError(/must use HTTPS/);
  });

  it("rejects local HTTP URLs in production", () => {
    expect(() => loadAppEnv({
      ...VALID_ENV,
      NODE_ENV: "production",
      NEXT_PUBLIC_SUPABASE_URL: "http://localhost:54321",
    })).toThrowError(/must use HTTPS/);
  });

  it("rejects credentials embedded in the URL", () => {
    expect(() => loadAppEnv({
      ...VALID_ENV,
      NEXT_PUBLIC_SUPABASE_URL: "https://username:password@example.supabase.co",
    })).toThrowError(/must not embed credentials/);
  });

  it("rejects a password embedded without a URL username", () => {
    expect(() => loadAppEnv({
      ...VALID_ENV,
      NEXT_PUBLIC_SUPABASE_URL: "https://:password@example.supabase.co",
    })).toThrowError(/must not embed credentials/);
  });

  it("includes an optional server-only secret in the returned server configuration", () => {
    const result = loadAppEnv({ ...VALID_ENV, SUPABASE_SECRET_KEY: "sb_secret_example" });
    expect(result.supabase.secretKey).toBe("sb_secret_example");
  });

  it("accepts a legacy anonymous JWT as a public key", () => {
    const result = loadAppEnv({
      ...VALID_ENV,
      NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: legacySupabaseKey("anon"),
    });
    expect(result.supabase.publishableKey).toContain(".");
  });

  it("rejects a missing or malformed publishable API token", () => {
    expect(() => loadAppEnv({
      ...VALID_ENV,
      NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "not-a-supabase-key",
    })).toThrowError(/must be a valid publishable Supabase key/);
  });

  it("rejects a secret key accidentally placed in a public variable", () => {
    expect(() => loadAppEnv({ ...VALID_ENV, SUPABASE_SECRET_KEY: "sb_publishable_wrong_place" }))
      .toThrowError(/SUPABASE_SECRET_KEY must be a valid server-only/);
    expect(() => loadAppEnv({
      ...VALID_ENV,
      NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "sb_secret_wrong_place",
    })).toThrowError(/privileged keys must never use a NEXT_PUBLIC_/);
  });

  it("accepts a valid optional Supabase server secret", () => {
    expect(loadAppEnv({ ...VALID_ENV, SUPABASE_SECRET_KEY: "sb_secret_example" })
      .supabase.secretKey).toBe("sb_secret_example");
    expect(loadAppEnv({
      ...VALID_ENV,
      SUPABASE_SECRET_KEY: legacySupabaseKey("service_role"),
    }).supabase.secretKey).toContain(".");
  });

  it("rejects a malformed legacy JWT without logging its value", () => {
    const errorLog = vi.spyOn(console, "error").mockImplementation(() => undefined);
    expect(() => loadAppEnv({
      ...VALID_ENV,
      NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "header.not-base64-json.signature",
    })).toThrowError(/must be a valid publishable Supabase key/);
    expect(errorLog).not.toHaveBeenCalled();
  });
});
