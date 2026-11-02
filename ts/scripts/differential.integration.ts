import { expect, test } from "bun:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

test("both dumps rewrite duplicate records, original CRLF bytes, and open and closed threads", async () => {
  const root = await mkdtemp(join(tmpdir(), "lodge-differential-"));
  try {
    await mkdir(join(root, "lodge/spec/storage"), { recursive: true });
    await writeFile(join(root, ".lodge.toml"), "");
    const text = "---\nkind: spec\nid: s-aaaaaa\ntitle: Storage\n---\n\nKept.\n";
    for (const name of ["a.md", "b.md"]) {
      await writeFile(join(root, "lodge/spec/storage", name), text.replaceAll("\n", "\r\n"));
    }
    await mkdir(join(root, "lodge/threads"));
    for (const [id, state] of [
      ["q-aaaaaa", "open"],
      ["q-bbbbbb", "closed"],
    ]) {
      await writeFile(
        join(root, `lodge/threads/${id}.md`),
        `---\nkind: thread\nid: ${id}\nabout: s-aaaaaa\nraises: doubt\nstate: ${state}\nopened: 2026-10-28T10:00:00+01:00\n---\n\n## Message 1\nby: author\nwhen: 2026-10-28T10:00:00+01:00\nwhere: a session\n\nA message.\n`,
      );
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
    expect(Object.keys(dump.rewrite)).toHaveLength(4);
    expect(dump.rewrite["lodge/spec/storage/a.md"][1]).toBe(false);
    const reference = join(root, "python.json");
    await writeFile(reference, python.stdout);
    const compared = Bun.spawnSync([
      process.execPath,
      join(import.meta.dir, "differential.ts"),
      root,
      reference,
    ]);
    expect(compared.stdout.toString()).toContain("0 differences");
    expect(compared.exitCode).toBe(0);
    expect(compared.stdout.toString()).toContain("4 rewritten files");
    expect(compared.stdout.toString()).toContain("2 threads");
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});
