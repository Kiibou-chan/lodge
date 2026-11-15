import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { project } from "./project.ts";
import { QUOTE, seed } from "./support.ts";

test("search", async () => {
  const p = await project(),
    ids = await seed(p),
    r = await p.run("search", "transcripts");
  expect([r.code, r.err]).toEqual([0, ""]);
  const lines = splitLines(r.out);
  expect(lines[0]?.startsWith(`${ids.decision} ITEM-1 · current · coordinator`)).toBe(true);
  expect(lines.slice(1, 4)).toEqual(["Keep transcripts", "", "Transcripts are kept."]);
  expect(lines[4]).toBe("");
  expect(lines[5]?.startsWith(`${ids.entry} · current · coordinator`)).toBe(true);
  expect(lines.slice(6)).toEqual(["Transcripts are kept", "", "Held."]);
});
test("search_by_code_and_filters", async () => {
  const p = await project();
  await seed(p);
  expect((await p.run("search", "item-1")).out.startsWith("d-")).toBe(true);
  const spec = (await p.run("search", "transcripts", "--kind", "spec")).out;
  expect(spec.startsWith("s-")).toBe(true);
  expect(spec.split("\n")[0]).not.toContain("d-");
  expect((await p.run("search", "transcripts", "--scope", "process")).out).toBe("no matches\n");
  expect((await p.run("search", "--by", "coordinator", "--kind", "decision")).out).toContain("d-");
  expect((await p.run("search", "transcripts", "--area", "storage", "--status", "any")).code).toBe(
    0,
  );
});
test("search_without_hits", async () => {
  const p = await project();
  await seed(p);
  const r = await p.run("search", "zebra");
  expect([r.code, r.out]).toEqual([0, "no matches\n"]);
});
test("search_bad_filter_is_a_usage_error", async () => {
  const p = await project();
  await seed(p);
  const r = await p.run("search", "x", "--status", "gone");
  expect(r.code).toBe(2);
  expect(r.err).toContain("invalid choice");
});
test("search_shows_quote_of_author_decision", async () => {
  const p = await project();
  await seed(p, [QUOTE], { decidedBy: "author" });
  expect((await p.run("search", "keep")).out).toContain(
    'quote: "Keep them." (chat, 2026-10-29 10:00)',
  );
});
