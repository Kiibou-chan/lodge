import { expect } from "bun:test";
import { realpathSync } from "node:fs";
import { dirname, isAbsolute, parse } from "node:path";
import { type HookContext, type Resolve, type respond, run } from "#hook";

export const resolve: Resolve = (path) => {
  const absolute = isAbsolute(path) ? path : `${process.cwd()}/${path}`;
  const root = parse(absolute).root;
  let found = root;
  for (const part of absolute.slice(root.length).split("/")) {
    if (!part || part === ".") continue;
    if (part === "..") {
      found = dirname(found);
      continue;
    }
    const next = `${found === root ? root : `${found}/`}${part}`;
    try {
      found = realpathSync(next);
    } catch (error) {
      if (
        !(error instanceof Error) ||
        !("code" in error) ||
        !["ENOENT", "ENOTDIR"].includes(String(error.code))
      )
        throw error;
      found = next;
    }
  }
  return found;
};
export function context(
  root: string,
  data: string | null = `${root}/lodge`,
  frozen: readonly string[] = [],
  server: string | null = null,
): HookContext {
  return { repoRoot: root, dataRoot: data, frozen, server };
}
export function payload(path: string, tool = "Edit") {
  return { tool_name: tool, tool_input: { file_path: path } };
}
export function text(response: ReturnType<typeof respond>): string {
  expect(response).not.toBeNull();
  if (!response) throw new Error("missing response");
  expect(response.hookSpecificOutput.hookEventName).toBe("PostToolUse");
  expect(typeof response.hookSpecificOutput.additionalContext).toBe("string");
  return response.hookSpecificOutput.additionalContext;
}
export async function drive(raw: string, finder: (path: string) => Promise<HookContext | null>) {
  let output = "";
  const code = await run(
    async () => raw,
    (value) => {
      output += value;
    },
    finder,
    resolve,
    null,
  );
  return [code, output] as const;
}
export function reversal(value: string) {
  expect(value).toContain("with the same tool");
  expect(value).toContain("tell the author");
  expect(value.toLowerCase()).not.toContain("undo");
  const warning = value.indexOf("Do not run");
  expect(warning).toBeGreaterThanOrEqual(0);
  for (const command of ["git checkout", "git restore", "git stash", "git clean"])
    expect(value.indexOf(command)).toBeGreaterThan(warning);
}
