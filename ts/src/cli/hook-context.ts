import { existsSync } from "node:fs";
import { join } from "node:path";
import { parseHookSettings } from "#app";
import { readExact } from "./files.ts";
import { tomlTable } from "./settings.ts";

function table(value: unknown): value is Readonly<Record<string, unknown>> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
export async function hookContextFor(
  edited: string,
  git: {
    readonly repoRootOf: (edited: string) => Promise<string>;
    readonly isFolder: (path: string) => boolean;
  },
): Promise<{
  readonly repoRoot: string;
  readonly dataRoot: string | null;
  readonly frozen: readonly string[];
  readonly server: string | null;
} | null> {
  try {
    const repoRoot = await git.repoRootOf(edited);
    const path = join(repoRoot, ".lodge.toml");
    const parsed = existsSync(path)
      ? tomlTable(readExact(path, "cannot be read: not UTF-8 text"))
      : {};
    const store = Object.hasOwn(parsed, "store") ? parsed["store"] : {};
    if (!table(store)) return null;
    const mode = Object.hasOwn(store, "mode") ? store["mode"] : "checkout";
    if (mode !== "checkout" && mode !== "branch") return null;
    let server: string | null = null;
    if (Object.hasOwn(parsed, "server")) {
      const section = parsed["server"];
      if (!table(section) || typeof section["url"] !== "string") return null;
      server = section["url"];
    }
    const frozen = parseHookSettings(Object.hasOwn(parsed, "hook") ? parsed["hook"] : {});
    const dataRoot = mode === "checkout" ? join(repoRoot, "lodge") : null;
    if (
      server === null &&
      dataRoot !== null &&
      (!git.isFolder(join(dataRoot, "decisions")) || !git.isFolder(join(dataRoot, "spec")))
    )
      return null;
    return { repoRoot, dataRoot, frozen, server };
  } catch {
    return null;
  }
}
