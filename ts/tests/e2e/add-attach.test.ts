import { expect, test } from "bun:test";
import { writeFileSync } from "node:fs";
import { splitLines } from "#core";
import { type Project, project } from "./project.ts";
import { areaText, decisionText, entryText, firstDecision, initialise } from "./support.ts";

const LOG = "step one\r\nstep two: café\n";
async function drafts(p: Project, ...extra: string[]) {
  const entry = (await p.run("id", "s")).out.trim();
  return [
    p.draft(
      "decision.md",
      decisionText("Keep logs", ["changes:", `  - {entry: ${entry}, action: create}`, ...extra]),
    ),
    p.draft("entry.md", entryText(entry)),
    p.draft("area.md", areaText(entry)),
  ];
}
function attachment(p: Project, name = "run.log", data?: Uint8Array) {
  const path = p.draft(name, LOG);
  if (data) writeFileSync(path, data);
  return path;
}
test("attachment_lands_beside_the_decision_in_checkout_mode", async () => {
  const p = await project();
  await initialise(p);
  const files = await drafts(p, "attachments: [run.log]");
  const r = await p.run("add", "--attach", attachment(p), ...files);
  expect([r.code, r.err]).toEqual([0, ""]);
  const decision = firstDecision(r.out);
  const path = `lodge/attachments/${decision}/run.log`;
  expect(await p.stored(path)).toBe(LOG);
  expect(await p.paths()).toContain(path);
  expect((await p.run("show", decision, "--provenance")).out).toContain("attachments: run.log");
  expect((await p.run("check")).out).toBe("ok\n");
});
test("several_attachments_and_a_dry_run", async () => {
  const p = await project();
  await initialise(p);
  const files = await drafts(p, "attachments: [run.log, notes.txt]");
  const both = ["--attach", attachment(p), "--attach", attachment(p, "notes.txt")];
  const dry = await p.run("add", "--dry-run", ...both, ...files);
  expect(dry.code).toBe(0);
  expect(splitLines(dry.out).at(-1)).toBe("dry run: nothing published");
  expect((await p.paths()).filter((path) => path.startsWith("lodge/attachments/"))).toEqual([]);
  const done = await p.run("add", ...both, ...files);
  expect(done.code).toBe(0);
  const decision = firstDecision(done.out),
    prefix = `lodge/attachments/${decision}/`;
  expect(
    (await p.paths())
      .filter((path) => path.startsWith(prefix))
      .map((path) => path.slice(prefix.length))
      .sort(),
  ).toEqual(["notes.txt", "run.log"]);
});
test("attachment_that_is_not_utf8_is_refused", async () => {
  const p = await project();
  await initialise(p);
  const files = await drafts(p, "attachments: [run.log]");
  const path = attachment(p, "run.log", new Uint8Array([255, 254, ...Buffer.from(" binary")]));
  const r = await p.run("add", "--attach", path, ...files);
  expect([r.code, r.out]).toEqual([2, ""]);
  expect(r.err).toBe(`lodge: ${path}: not UTF-8 text; attachments are text in this version\n`);
  expect((await p.paths()).filter((path) => path.startsWith("lodge/attachments/"))).toEqual([]);
});
test("attach_with_two_new_decisions_is_refused", async () => {
  const p = await project();
  await initialise(p);
  const files = await drafts(p, "attachments: [run.log]");
  const r = await p.run(
    "add",
    "--attach",
    attachment(p),
    ...files,
    p.draft("other.md", decisionText("Another")),
  );
  expect([r.code, r.out]).toEqual([2, ""]);
  expect(r.err).toBe("lodge: --attach needs the add to create one decision, not 2\n");
});
test("attach_with_a_missing_file_is_refused", async () => {
  const p = await project();
  await initialise(p);
  const files = await drafts(p, "attachments: [run.log]"),
    missing = `${p.root}/nowhere.log`;
  const r = await p.run("add", "--attach", missing, ...files);
  expect([r.code, r.out]).toEqual([2, ""]);
  expect(r.err.startsWith(`lodge: ${missing}: cannot be read`)).toBe(true);
  expect(r.err.split("\n").length - 1).toBe(1);
});
test("decision_that_does_not_list_the_attachment_is_refused", async () => {
  const p = await project();
  await initialise(p);
  const files = await drafts(p);
  const r = await p.run("add", "--attach", attachment(p), ...files);
  expect([r.code, r.out]).toEqual([2, ""]);
  expect(r.err.startsWith("lodge: the new decision lists [] in attachments")).toBe(true);
  expect((await p.run("search", "logs")).out).toBe("no matches\n");
});

test("paths_lists_records_and_attachments_sorted", async () => {
  const p = await project();
  await initialise(p);
  const files = await drafts(p, "attachments: [run.log]");
  const r = await p.run("add", "--attach", attachment(p), ...files);
  expect([r.code, r.err]).toEqual([0, ""]);
  const decision = firstDecision(r.out);
  const paths = await p.paths();
  expect(paths).toHaveLength(4);
  expect(paths).toEqual([...paths].sort());
  expect(paths).toContain(`lodge/attachments/${decision}/run.log`);
  expect(paths.filter((path) => path.startsWith("lodge/decisions/"))).toHaveLength(1);
  expect(paths.filter((path) => path.startsWith("lodge/spec/storage/"))).toHaveLength(2);
});
