import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { type Project, project } from "./project.ts";
import { areaText, decisionText, entryText, initialise } from "./support.ts";

async function drafts(
  p: Project,
  withDecision: boolean,
  author = false,
  body = "Transcripts are kept.",
) {
  const entry = (await p.run("id", "s")).out.trim();
  const files = [p.draft("area.md", areaText(entry)), p.draft("entry.md", entryText(entry))];
  if (withDecision)
    files.push(
      p.draft(
        "decision.md",
        decisionText("Keep", ["changes:", `  - {entry: ${entry}, action: create}`], {
          decidedBy: author ? "author" : "coordinator",
          body,
        }),
      ),
    );
  return files;
}
test("add_dry_run_publishes_nothing", async () => {
  const p = await project();
  await initialise(p);
  const before = await p.paths();
  const r = await p.run("add", "--dry-run", ...(await drafts(p, true)));
  expect([r.code, r.err]).toEqual([0, ""]);
  expect(splitLines(r.out).at(-1)).toBe("dry run: nothing published");
  expect(await p.paths()).toEqual(before);
  expect((await p.run("search", "keep")).out).toBe("no matches\n");
});
test("add_dry_run_failing_check_exits_1", async () => {
  const p = await project();
  await initialise(p);
  const r = await p.run("add", "--dry-run", ...(await drafts(p, false)));
  expect(r.code).toBe(1);
  const lines = splitLines(r.out);
  expect(lines.some((line) => line.startsWith("check 4: "))).toBe(true);
  expect(lines.slice(-2)).toEqual([
    "not published: the check failed",
    "dry run: nothing published",
  ]);
});
test("dry_run_marks_new_decision_ids_provisional", async () => {
  const p = await project();
  await initialise(p);
  const files = await drafts(p, true, false, "Transcripts are kept for 40 days.");
  const dry = await p.run("add", "--dry-run", ...files);
  const marked = dry.out.split("\n").filter((line) => line.startsWith("feedback: d-"));
  expect(marked.length).toBeGreaterThan(0);
  expect(marked.every((line) => line.includes(" (provisional): "))).toBe(true);
  expect((await p.run("add", ...files)).out).not.toContain("(provisional)");
});
test("dry_run_marks_new_decision_ids_provisional_on_check_lines", async () => {
  const p = await project();
  await initialise(p);
  const files = await drafts(p, true, true);
  const dry = await p.run("add", "--dry-run", ...files);
  const checks = dry.out.split("\n").filter((line) => line.startsWith("check 3: "));
  expect(checks.length).toBeGreaterThan(0);
  expect(checks.every((line) => line.includes("(provisional)"))).toBe(true);
  expect((await p.run("add", ...files)).out).not.toContain("(provisional)");
});
