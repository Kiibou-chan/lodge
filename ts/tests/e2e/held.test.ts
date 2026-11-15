import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { type Project, project } from "./project.ts";
import { areaText, decisionText, entryText, initialise, QUOTE } from "./support.ts";

async function drafts(p: Project) {
  await initialise(p);
  const entry = (await p.run("id", "s")).out.trim();
  return [
    p.draft(
      "decision.md",
      decisionText(
        "Keep transcripts",
        ["code: ITEM-1", "changes:", `  - {entry: ${entry}, action: create}`, QUOTE],
        { decidedBy: "author", body: Array(81).fill("word").join(" ") },
      ),
    ),
    p.draft("entry.md", entryText(entry)),
    p.draft("area.md", areaText(entry)),
  ];
}
test("held_add_marks_its_ids_provisional", async () => {
  const p = await project(),
    files = await drafts(p),
    r = await p.run("add", ...files);
  expect([r.code, r.err]).toEqual([0, ""]);
  const lines = splitLines(r.out);
  expect(lines.at(-1)).toMatch(
    /^held for approval by author as hold \d+; nothing is current until they approve it$/u,
  );
  const naming = lines.slice(0, -1).filter((line) => /[ds]-[a-z0-9]{6}/u.test(line));
  expect(naming.length).toBeGreaterThan(0);
  for (const line of naming)
    for (const match of line.matchAll(/[ds]-[a-z0-9]{6}/gu))
      expect(line.slice((match.index ?? 0) + match[0].length).startsWith(" (provisional)")).toBe(
        true,
      );
  expect(
    naming.some((line) =>
      /^feedback: d-[a-z0-9]{6} \(provisional\): the statement is 81 words;/u.test(line),
    ),
  ).toBe(true);
});
test("dry_run_of_a_persons_decision_names_who_approves", async () => {
  const p = await project(),
    files = await drafts(p),
    r = await p.run("add", "--dry-run", ...files);
  expect([r.code, r.err]).toEqual([0, ""]);
  expect(splitLines(r.out).slice(-2)).toEqual([
    "note: author approves this add before it is current",
    "dry run: nothing published",
  ]);
});
