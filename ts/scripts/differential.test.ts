import { expect, test } from "bun:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

test("differential compares an empty synthetic store and reports nested differences", async () => {
  const root = await mkdtemp(join(tmpdir(), "lodge-differential-"));
  try {
    await mkdir(join(root, "lodge"));
    await writeFile(join(root, ".lodge.toml"), "");
    const expected = { spec: "", problems: [], levels: {}, search: {}, rewrite: {} };
    const reference = join(root, "python.json");
    await writeFile(reference, JSON.stringify(expected));
    const run = () =>
      Bun.spawnSync([process.execPath, join(import.meta.dir, "differential.ts"), root, reference]);
    const same = run();
    expect(same.exitCode).toBe(0);
    expect(same.stdout.toString()).toContain(
      "0 records, 0 areas, 0 threads, 0 problems, 0 queries, 0 rewritten files",
    );
    await writeFile(
      reference,
      JSON.stringify({ ...expected, levels: { "s-aaaaaa": ["different"] } }),
    );
    const different = run();
    expect(different.exitCode).toBe(1);
    expect(different.stdout.toString()).toContain('levels["s-aaaaaa"]');
    expect(different.stdout.toString()).toContain("different");
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});
