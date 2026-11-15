import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { project } from "./project.ts";
import { seed } from "./support.ts";

test("search_limit_says_what_it_left_out", async () => {
  const p = await project();
  await seed(p);
  const r = await p.run("search", "transcripts", "--limit", "1");
  expect([r.code, r.err]).toEqual([0, ""]);
  expect(splitLines(r.out).at(-1)).toBe("1 of 2 shown; narrow the query or give --limit 2");
  expect((await p.run("search", "transcripts", "--limit", "2")).out).not.toContain(" shown;");
});
test("search_limit_must_be_a_positive_whole_number", async () => {
  const p = await project();
  await seed(p);
  for (const bad of ["0", "-1", "many"]) {
    const r = await p.run("search", "transcripts", "--limit", bad);
    expect(r.code).toBe(2);
    expect(r.err).toContain("is not a positive whole number");
  }
});
