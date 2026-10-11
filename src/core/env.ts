import "server-only";

export type AppEnvironment = Readonly<{
  nodeEnvironment: "development" | "test" | "production";
  supabase: Readonly<{
    url: string;
    publishableKey: string;
    secretKey?: string;
  }>;
}>;

export class AppInitializationError extends Error {
  readonly code = "APP_INITIALIZATION_FAILED";
  readonly missingVariables: readonly string[];

  constructor(message: string, missingVariables: readonly string[] = []) {
    super(message);
    this.name = "AppInitializationError";
    this.missingVariables = Object.freeze([...missingVariables]);
  }
}

type EnvironmentSource = Readonly<Record<string, string | undefined>>;

const PLACEHOLDER_VALUES = new Set([
  "",
  "change-me",
  "changeme",
  "replace-me",
  "your-key-here",
  "your-project-url",
]);

function readRequired(source: EnvironmentSource, key: string, missing: string[]): string {
  const value = source[key]?.trim();
  if (!value || PLACEHOLDER_VALUES.has(value.toLowerCase())) {
    missing.push(key);
    return "";
  }
  return value;
}

function parseNodeEnvironment(value: string | undefined): AppEnvironment["nodeEnvironment"] {
  if (value === undefined || value === "") return "development";
  if (value === "development" || value === "test" || value === "production") return value;
  throw new AppInitializationError(
    'APP_INITIALIZATION_FAILED: NODE_ENV must be "development", "test", or "production".',
  );
}

function jwtRole(value: string): string | undefined {
  const segments = value.split(".");
  if (segments.length !== 3 || !segments[1]) return undefined;
  try {
    const payload: unknown = JSON.parse(Buffer.from(segments[1], "base64url").toString("utf8"));
    if (typeof payload === "object" && payload !== null && "role" in payload) {
      const role = (payload as { role?: unknown }).role;
      return typeof role === "string" ? role : undefined;
    }
    return undefined;
  } catch {
    return undefined;
  }
}

function isPublishableSupabaseKey(value: string): boolean {
  return (value.startsWith("sb_publishable_") && value.length > "sb_publishable_".length)
    || jwtRole(value) === "anon";
}

function isPrivilegedSupabaseKey(value: string): boolean {
  return value.startsWith("sb_secret_") || jwtRole(value) === "service_role";
}

function parseSupabaseUrl(value: string, nodeEnvironment: AppEnvironment["nodeEnvironment"]): string {
  let parsed: URL;
  try {
    parsed = new URL(value);
  } catch {
    throw new AppInitializationError(
      "APP_INITIALIZATION_FAILED: NEXT_PUBLIC_SUPABASE_URL must be a valid absolute URL.",
    );
  }

  const localHttpAllowed = nodeEnvironment !== "production"
    && (parsed.hostname === "localhost" || parsed.hostname === "127.0.0.1");
  if (parsed.protocol !== "https:" && !(parsed.protocol === "http:" && localHttpAllowed)) {
    throw new AppInitializationError(
      "APP_INITIALIZATION_FAILED: Supabase URL must use HTTPS, except for local development URLs.",
    );
  }
  if (!parsed.hostname || parsed.username || parsed.password) {
    throw new AppInitializationError(
      "APP_INITIALIZATION_FAILED: Supabase URL must include a host and must not embed credentials.",
    );
  }
  return parsed.origin;
}

export function loadAppEnv(source: EnvironmentSource = process.env): AppEnvironment {
  const missing: string[] = [];
  const nodeEnvironment = parseNodeEnvironment(source.NODE_ENV);
  const rawUrl = readRequired(source, "NEXT_PUBLIC_SUPABASE_URL", missing);
  const publishableKey = readRequired(source, "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", missing);

  if (missing.length > 0) {
    const names = [...new Set(missing)].sort();
    const error = new AppInitializationError(
      `APP_INITIALIZATION_FAILED: Missing required environment variable(s): ${names.join(", ")}. Set them in the runtime environment before starting the application. No credential values were logged.`,
      names,
    );
    console.error(error.message);
    throw error;
  }

  const url = parseSupabaseUrl(rawUrl, nodeEnvironment);
  if (isPrivilegedSupabaseKey(publishableKey) || !isPublishableSupabaseKey(publishableKey)) {
    throw new AppInitializationError(
      "APP_INITIALIZATION_FAILED: NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY must be a valid publishable Supabase key; privileged keys must never use a NEXT_PUBLIC_ variable.",
    );
  }

  const secretKey = source.SUPABASE_SECRET_KEY?.trim();
  if (secretKey && !isPrivilegedSupabaseKey(secretKey)) {
    throw new AppInitializationError(
      "APP_INITIALIZATION_FAILED: SUPABASE_SECRET_KEY must be a valid server-only Supabase secret key; leave it unset until a privileged server operation is required.",
    );
  }

  return Object.freeze({
    nodeEnvironment,
    supabase: Object.freeze({
      url,
      publishableKey,
      ...(secretKey ? { secretKey } : {}),
    }),
  });
}
