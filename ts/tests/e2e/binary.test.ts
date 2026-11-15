import { afterAll, beforeAll, expect, test } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import pkg from "../../package.json" with { type: "json" };

const dir = mkdtempSync(join(tmpdir(), "lodge-binary-"));
const cwd = mkdtempSync(join(tmpdir(), "lodge-away-"));
const binary = join(dir, "lodge");
beforeAll(async () => {
  const build = Bun.spawn(
    [process.execPath, "build", "--compile", "src/main.ts", "--outfile", binary],
    { cwd: resolve(import.meta.dir, "../.."), stdout: "pipe", stderr: "pipe" },
  );
  const [code, error] = await Promise.all([build.exited, new Response(build.stderr).text()]);
  expect(error).toBe("");
  expect(code).toBe(0);
});
afterAll(() => {
  rmSync(dir, { recursive: true });
  rmSync(cwd, { recursive: true });
});
async function invoke(argument: string) {
  const child = Bun.spawn([binary, argument], {
    cwd,
    env: { PATH: process.env["PATH"] },
    stdout: "pipe",
    stderr: "pipe",
  });
  const [code, out, err] = await Promise.all([
    child.exited,
    new Response(child.stdout).text(),
    new Response(child.stderr).text(),
  ]);
  return { code, out, err };
}
test("version", async () => {
  expect(await invoke("--version")).toEqual({ code: 0, out: `lodge ${pkg.version}\n`, err: "" });
});
test("compiled_binary_runs", async () => {
  const result = await invoke("guide");
  expect(result.code).toBe(0);
  expect(result.out.startsWith("# ")).toBe(true);
  expect(result.out).toContain("lodge add");
});
