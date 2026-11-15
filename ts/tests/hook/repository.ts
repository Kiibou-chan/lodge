import { afterEach } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { hookContextFor, run } from "#cli";
import { run as gitRun, isFolder, repoRootOf, resolvePath } from "#git";
import { run as hookRun } from "#hook";
import { isolateGit } from "../git/isolated.ts";

isolateGit();
const roots: string[] = [];
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});
export function hookProject() {
  const folder = mkdtempSync(join(tmpdir(), "lodge-hook-command-"));
  roots.push(folder);
  const root = join(folder, "work");
  mkdirSync(root);
  gitRun(["init", "-b", "main"], root);
  return {
    root,
    configure(text: string | Uint8Array) {
      writeFileSync(join(root, ".lodge.toml"), text);
    },
    initialise() {
      for (const name of ["decisions", "spec"]) {
        const folder = join(root, "lodge", name);
        mkdirSync(folder, { recursive: true });
        writeFileSync(join(folder, ".gitkeep"), "");
      }
      gitRun(["add", "--", "lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"], root);
    },
    git: (...args: string[]) => gitRun(args, root),
    async run(argv: readonly string[], input = "", cwd = root) {
      let out = "";
      let err = "";
      const output = (text: string) => {
        out += text;
      };
      const code = await run(argv, {
        cwd,
        env: {},
        version: "test",
        out: output,
        err: (text) => {
          err += text;
        },
        fetch: async () => {
          throw new Error("unexpected request");
        },
        hook: () =>
          hookRun(
            async () => input,
            output,
            (edited) => hookContextFor(edited, { repoRootOf, isFolder }),
            resolvePath,
            cwd,
          ),
      });
      return { code, out, err };
    },
  };
}
