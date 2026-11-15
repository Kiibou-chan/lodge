import type { ZeroTwoCopy } from "#app";
import { ZERO_TWO_STORE } from "../core/zero-two-store.ts";

export function zeroTwoCopy(): ZeroTwoCopy {
  return {
    rev: "synthetic-revision",
    files: new Map([...ZERO_TWO_STORE].filter(([path]) => path.startsWith("lodge/"))),
    settings: Bun.TOML.parse(ZERO_TWO_STORE.get(".lodge.toml") as string) as Record<
      string,
      unknown
    >,
  };
}
