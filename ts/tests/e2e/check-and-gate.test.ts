import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { project } from "./project.ts";
import { seed } from "./support.ts";

test("check_and_gate", async () => {
  const p = await project();
  await seed(p);
  expect(await p.run("check")).toEqual({ code: 0, out: "ok\n", err: "" });
  const id = (await p.run("id", "d")).out.trim(),
    path = `lodge/decisions/${id}-unquoted.md`;
  await p.handEdit({
    [path]: `---\nid: ${id}\nkind: decision\ntitle: Unquoted\nscope: product\ndecided_by: author\ndate: 2026-10-29T12:00:00+01:00\n---\n\nUnquoted statement.\n`,
  });
  const r = await p.run("check");
  expect([r.code, r.err]).toEqual([1, ""]);
  expect(r.out.startsWith("check 3: ")).toBe(true);
  expect(r.out).toContain(id);
  expect((await p.run("show", id)).out).toContain("fails check");
  const gate = await p.run("check", "--gate");
  expect([gate.code, gate.err]).toEqual([0, ""]);
  const lines = gate.out.split("\n");
  expect(lines[0]).toBe("ok");
  expect(lines[1]?.startsWith(`note: already published, check 3: ${path}: ${id}: `)).toBe(true);
});
test("check_prints_unreadable_files_and_fails", async () => {
  const p = await project();
  await seed(p);
  await p.handEdit({ "lodge/decisions/d-zzzzzz-broken.md": "---\ntitle: [unclosed\n---\n" });
  const r = await p.run("check");
  expect(r.code).toBe(1);
  const lines = splitLines(r.out);
  expect(lines[0]?.startsWith("problem: lodge/decisions/d-zzzzzz-broken.md:2: ")).toBe(true);
  expect(lines).toHaveLength(1);
});
