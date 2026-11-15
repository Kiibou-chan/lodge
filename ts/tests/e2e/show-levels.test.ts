import { expect, test } from "bun:test";
import { project } from "./project.ts";
import { QUOTE, seed } from "./support.ts";

test("show_levels", async () => {
  const p = await project(),
    ids = await seed(p, [QUOTE], { decidedBy: "author" }),
    l = await p.run("show", ids.decision);
  expect(l.code).toBe(0);
  expect(l.out.startsWith(`${ids.decision} ITEM-1 · current · author`)).toBe(true);
  expect(l.out).toContain('quote: "Keep them."');
  expect(l.out).not.toContain("## Reasoning");
  expect(l.out).not.toContain("## Provenance");
  const reasoning = await p.run("show", ids.decision, "--reasoning");
  expect(reasoning.out.startsWith(l.out.replace(/\n+$/u, ""))).toBe(true);
  expect(reasoning.out).toContain("\n## Reasoning\n");
  expect(reasoning.out).not.toContain("## Provenance");
  const prov = await p.run("show", "ITEM-1", "--provenance");
  expect(prov.out).toContain("\n## Provenance\n");
  expect(prov.out).toContain(`changes (create): ${ids.entry} (current)`);
  const both = await p.run("show", ids.decision.toUpperCase(), "--provenance", "--reasoning");
  expect(both.out.indexOf("## Reasoning")).toBeLessThan(both.out.indexOf("## Provenance"));
});
test("show_entry_reasoning_lists_its_decisions", async () => {
  const p = await project(),
    ids = await seed(p),
    out = (await p.run("show", ids.entry, "--reasoning")).out;
  expect(out.indexOf("## Reasoning")).toBeLessThan(out.indexOf(ids.decision));
});
test("show_unknown_record", async () => {
  const p = await project();
  await seed(p);
  expect(await p.run("show", "d-zzzzzz")).toEqual({
    code: 2,
    out: "",
    err: "lodge: no record named d-zzzzzz\n",
  });
});
