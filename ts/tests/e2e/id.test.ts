import { expect, test } from "bun:test";
import { project } from "./project.ts";
import { initialise } from "./support.ts";

test("id", async () => {
  const p = await project();
  await initialise(p);
  const d = await p.run("id", "d"),
    s = await p.run("id", "s");
  expect(d.out).toMatch(/^d-[0-9a-hjkmnp-tv-z]{6}\n$/u);
  expect(s.out).toMatch(/^s-[0-9a-hjkmnp-tv-z]{6}\n$/u);
  expect([d.code, s.code]).toEqual([0, 0]);
});
test("id_kind_is_d_or_s", async () => {
  const p = await project();
  await initialise(p);
  const r = await p.run("id", "x");
  expect(r.code).toBe(2);
  expect(r.err).toContain("invalid choice");
});
