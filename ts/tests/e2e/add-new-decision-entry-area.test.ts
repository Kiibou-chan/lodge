import { expect, test } from "bun:test";
import { writeFileSync } from "node:fs";
import { splitLines } from "#core";
import { project } from "./project.ts";
import { areaText, decisionText, entryText, firstDecision, initialise, seed } from "./support.ts";

test("add_new_decision_entry_area", async () => {
  const p = await project();
  await initialise(p);
  const entry = (await p.run("id", "s")).out.trim();
  const r = await p.run(
    "add",
    p.draft("area.md", areaText(entry)),
    p.draft("entry.md", entryText(entry)),
    p.draft(
      "decision.md",
      decisionText("Keep transcripts", ["changes:", `  - {entry: ${entry}, action: create}`]),
    ),
  );
  expect([r.code, r.err]).toEqual([0, ""]);
  const lines = splitLines(r.out),
    last = lines.at(-1) ?? "";
  expect(last.startsWith("published ")).toBe(true);
  expect(last.split(" ")).toContain(entry);
  expect(lines.some((line) => line.startsWith("note: area storage"))).toBe(true);
  const decision = firstDecision(r.out);
  expect((await p.paths()).filter((path) => path.startsWith("lodge/"))).toHaveLength(3);
  expect((await p.run("show", decision)).code).toBe(0);
  expect((await p.run("check")).out).toBe("ok\n");
});
test("add_prints_feedback_before_the_outcome", async () => {
  const p = await project();
  await initialise(p);
  const entry = (await p.run("id", "s")).out.trim(),
    title = `Keep ${"very ".repeat(30)}long titles`;
  const r = await p.run(
    "add",
    p.draft("area.md", areaText(entry)),
    p.draft("entry.md", entryText(entry, title)),
    p.draft(
      "decision.md",
      decisionText("Keep", ["changes:", `  - {entry: ${entry}, action: create}`]),
    ),
  );
  const lines = splitLines(r.out),
    feedback = lines.filter((line) => line.startsWith("feedback: "));
  expect(feedback.length).toBeGreaterThan(0);
  expect(feedback[0]?.startsWith(`feedback: ${entry}: the title is `)).toBe(true);
  expect(lines).toContain(feedback[0] ?? "");
  expect(lines.indexOf(feedback[0] ?? "")).toBeLessThan(lines.length - 1);
});
test("add_without_a_file_is_a_usage_error", async () => {
  const p = await project();
  await initialise(p);
  const r = await p.run("add");
  expect(r.code).toBe(2);
  expect(r.err).toContain("usage:");
});
test("add_missing_file", async () => {
  const p = await project();
  await initialise(p);
  const r = await p.run("add", `${p.root}/nowhere.md`);
  expect([r.code, r.out]).toEqual([2, ""]);
  expect(r.err.startsWith("lodge: ")).toBe(true);
  expect(r.err).toContain("nowhere.md");
  expect(r.err.split("\n").length - 1).toBe(1);
});
test("add_file_that_is_not_utf8", async () => {
  const p = await project();
  await initialise(p);
  const path = p.draft("bad.md", "");
  writeFileSync(
    path,
    Buffer.from([...Buffer.from("---\ntitle: "), 255, ...Buffer.from("\n---\n")]),
  );
  const r = await p.run("add", path);
  expect(r.code).toBe(2);
  expect(r.err).toBe(`lodge: ${path}: not UTF-8 text\n`);
});
test("add_nothing_changed", async () => {
  const p = await project();
  await seed(p);
  const unchanged = (await p.run("draft", "area:storage")).out;
  const r = await p.run("add", p.draft("area.md", unchanged));
  expect(r.code).toBe(0);
  expect(splitLines(r.out).at(-1)).toBe("nothing changed");
  expect(r.out).not.toContain("note: nothing changed");
});
