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

test("both dumps rewrite duplicate record files and compare original CRLF bytes", async () => {
  const root = await mkdtemp(join(tmpdir(), "lodge-differential-"));
  try {
    await mkdir(join(root, "lodge/spec/storage"), { recursive: true });
    await writeFile(join(root, ".lodge.toml"), "");
    const text = "---\nkind: spec\nid: s-aaaaaa\ntitle: Storage\n---\n\nKept.\n";
    for (const name of ["a.md", "b.md"]) {
      await writeFile(join(root, "lodge/spec/storage", name), text.replaceAll("\n", "\r\n"));
    }
    const python = Bun.spawnSync(
      [
        "uv",
        "run",
        "--frozen",
        "--quiet",
        "python",
        join(import.meta.dir, "../../scripts/differential_dump.py"),
        root,
      ],
      { cwd: join(import.meta.dir, "../..") },
    );
    expect(python.exitCode).toBe(0);
    const dump = JSON.parse(python.stdout.toString());
    expect(Object.keys(dump.rewrite)).toHaveLength(2);
    expect(dump.rewrite["lodge/spec/storage/a.md"][1]).toBe(false);
    const reference = join(root, "python.json");
    await writeFile(reference, python.stdout);
    const compared = Bun.spawnSync([
      process.execPath,
      join(import.meta.dir, "differential.ts"),
      root,
      reference,
    ]);
    expect(compared.exitCode).toBe(0);
    expect(compared.stdout.toString()).toContain("2 rewritten files");
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});
