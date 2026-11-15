import { expect, test } from "bun:test";
import { project } from "./project.ts";
import { seed } from "./support.ts";

test("show_ambiguous_code_one_line", async () => {
  const p = await project(),
    first = await seed(p),
    other = (await p.run("id", "d")).out.trim();
  await p.handEdit({
    [`lodge/decisions/${other}-another.md`]: `---\nid: ${other}\nkind: decision\ncode: item-1\ntitle: Another\nscope: product\ndecided_by: coordinator\ndate: 2026-10-29T12:00:00+01:00\n---\n\nAnother statement.\n`,
  });
  const r = await p.run("show", "ITEM-1");
  expect([r.code, r.out]).toEqual([2, ""]);
  expect(r.err.split("\n")).toHaveLength(2);
  expect(r.err.startsWith("lodge: the code ITEM-1 names more than one record: ")).toBe(true);
  expect(r.err).toContain(first.decision);
  expect(r.err).toContain(other);
});
