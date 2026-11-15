import { expect, test } from "bun:test";
import { project } from "./project.ts";
import { seed } from "./support.ts";

test("search_shows_unparsable_file", async () => {
  const p = await project();
  await seed(p);
  const broken = "lodge/decisions/d-zzzzzz-broken.md";
  await p.handEdit({ [broken]: "---\ntitle: [unclosed\n---\n" });
  const r = await p.run("search", "transcripts");
  expect(r.code).toBe(0);
  const lines = r.out.split("\n");
  expect(lines[0]?.startsWith(`problem: ${broken}:2: `)).toBe(true);
  expect(lines[1]?.startsWith("d-")).toBe(true);
});
