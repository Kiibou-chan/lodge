import { expect, test } from "bun:test";
import { project } from "./project.ts";
import { initialise } from "./support.ts";

test("add_bad_yaml_exits_2_naming_file_and_line", async () => {
  const p = await project();
  await initialise(p);
  const path = p.draft("broken.md", "---\nkind: decision\ntitle: [unclosed\n---\n\nText.\n");
  const r = await p.run("add", path);
  expect([r.code, r.out]).toEqual([2, ""]);
  expect(r.err.startsWith(`lodge: ${path}:`)).toBe(true);
  expect(r.err.split("\n").length - 1).toBe(1);
  expect(r.err.includes(`${path}:3`) || r.err.includes(`${path}:4`)).toBe(true);
});
test("add_missing_fence_exits_2", async () => {
  const p = await project();
  await initialise(p);
  const path = p.draft("nofence.md", "kind: decision\n");
  const r = await p.run("add", path);
  expect(r.code).toBe(2);
  expect(r.err.startsWith(`lodge: ${path}`)).toBe(true);
});
