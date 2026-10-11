import { loadAppEnv } from "@/core/env";

export async function register(): Promise<void> {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    loadAppEnv();
  }
}
