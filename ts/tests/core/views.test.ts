import { expect, test } from "bun:test";
import {
  Action,
  checkResult,
  derive,
  failingIds,
  formatLevel1,
  formatLevel3,
  level1,
  level2,
  level2Views,
  level3,
  problem,
  Scope,
  unrecordedProblems,
} from "#core";
import { at, decision, entry, snapshotOf } from "./builders.ts";
import { NOTES } from "./checks.ts";

const NONE = new Set<string>();
const CHANGE = [{ entry: "s-aaaaaa", action: Action.EDIT }];
test("level1_status_who_flags", () => {
  const author = decision({
    id: "d-aaaaaa",
    decidedBy: "author",
    date: at(0),
    scope: Scope.PROCESS,
  });
  const agent = decision({
    id: "d-bbbbbb",
    date: at(1),
    replaces: ["d-aaaaaa"],
    title: "T",
    statement: "S",
  });
  const s = snapshotOf([author, agent]);
  const d = derive(s);
  const got = level1(s, d, "d-bbbbbb", new Set<string>(["d-bbbbbb"]));
  expect([got.kind, got.status, got.decidedBy, got.scope, got.area]).toEqual([
    "decision",
    "current",
    "coordinator",
    "product",
    null,
  ]);
  expect([got.title, got.statement, got.date]).toEqual(["T", "S", at(1)]);
  expect(got.flags).toEqual(["awaiting the author", "fails check"]);
  const old = level1(s, d, "d-aaaaaa", NONE);
  expect(old.status).toEqual("replaced");
  expect(old.flags).toEqual(["replaced by d-bbbbbb", "awaiting the author on d-bbbbbb"]);
});
test("author_decision_behind_an_agent_entry_edit_awaits_the_author", () => {
  const create = [{ entry: "s-aaaaaa", action: Action.CREATE }];
  const hers = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: create });
  const edit = decision({ id: "d-bbbbbb", date: at(1), changes: CHANGE });
  const s = snapshotOf([entry({ id: "s-aaaaaa" }), hers, edit]);
  const d = derive(s);
  expect(d.awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
  expect(level1(s, d, "d-aaaaaa", NONE).flags).toEqual(["awaiting the author on d-bbbbbb"]);
  expect(level1(s, d, "s-aaaaaa", NONE).flags).toContain("awaiting the author on d-bbbbbb");
});
test("agent_decision_behind_an_agent_entry_edit_is_not_flagged", () => {
  const create = [{ entry: "s-aaaaaa", action: Action.CREATE }];
  const first = decision({ id: "d-aaaaaa", date: at(0), changes: create });
  const edit = decision({ id: "d-bbbbbb", date: at(1), changes: CHANGE });
  const s = snapshotOf([entry({ id: "s-aaaaaa" }), first, edit]);
  expect(level1(s, derive(s), "d-aaaaaa", NONE).flags).toEqual([]);
});
test("narrowed_decision_flagged_at_level1", () => {
  const old = decision({ id: "d-aaaaaa", date: at(0) });
  const next = decision({ id: "d-bbbbbb", date: at(1), narrows: ["d-aaaaaa"] });
  const newer = decision({ id: "d-cccccc", date: at(2), narrows: ["d-aaaaaa"] });
  const s = snapshotOf([old, next, newer]);
  const got = level1(s, derive(s), "d-aaaaaa", NONE);
  expect(got.status).toEqual("current");
  expect(got.flags).toEqual(["narrowed by d-cccccc, d-bbbbbb"]);
});
test("replaced_decision_names_successor_at_level1", () => {
  const old = decision({ id: "d-aaaaaa", date: at(0) });
  const next = decision({ id: "d-bbbbbb", date: at(1), replaces: ["d-aaaaaa"] });
  const s = snapshotOf([old, next]);
  expect(level1(s, derive(s), "d-aaaaaa", NONE).flags).toEqual(["replaced by d-bbbbbb"]);
});
test("entry_level1_takes_who_from_latest_decision", () => {
  const spec = entry({ id: "s-aaaaaa", area: "storage", code: "SPEC-1" });
  const first = decision({ id: "d-aaaaaa", date: at(0), decidedBy: "reviewer", changes: CHANGE });
  const last = decision({ id: "d-bbbbbb", date: at(5), decidedBy: "advisor", changes: CHANGE });
  const kill = decision({
    id: "d-cccccc",
    date: at(9),
    changes: [{ entry: "s-aaaaaa", action: Action.RETIRE }],
  });
  let s = snapshotOf([spec, first, last]);
  let got = level1(s, derive(s), "s-aaaaaa", NONE);
  expect([got.kind, got.code, got.decidedBy, got.date, got.scope, got.area]).toEqual([
    "spec",
    "SPEC-1",
    "advisor",
    at(5),
    null,
    "storage",
  ]);
  s = snapshotOf([spec, first, last, kill]);
  got = level1(s, derive(s), "s-aaaaaa", NONE);
  expect(got.status).toEqual("retired");
  expect(got.flags).toEqual(["retired by d-cccccc"]);
  const bare = snapshotOf([entry({ id: "s-dddddd" })]);
  expect(level1(bare, derive(bare), "s-dddddd", NONE).decidedBy).toEqual(null);
});
test("unquoted_import_flags", () => {
  const unquoted = decision({ id: "d-aaaaaa", decidedBy: "author", importedFrom: NOTES });
  const quoted = decision({
    id: "d-bbbbbb",
    decidedBy: "author",
    importedFrom: NOTES,
    quote: { text: "Yes.", where: "a", when: "b" },
  });
  const agent = decision({ id: "d-cccccc", importedFrom: NOTES });
  const spec = entry({ id: "s-aaaaaa", importedFrom: NOTES });
  const s = snapshotOf([unquoted, quoted, agent, spec]);
  const d = derive(s);
  expect(level1(s, d, "d-aaaaaa", NONE).flags).toEqual(["imported", "unquoted"]);
  expect(level1(s, d, "d-bbbbbb", NONE).flags).toEqual(["imported"]);
  expect(level1(s, d, "d-cccccc", NONE).flags).toEqual(["imported"]);
  expect(level1(s, d, "s-aaaaaa", NONE).flags).toEqual(["imported"]);
});
test("awaiting_flag_on_touched_entry", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: CHANGE });
  const agent = decision({ id: "d-bbbbbb", date: at(1), changes: CHANGE });
  const s = snapshotOf([spec, author, agent]);
  expect(level1(s, derive(s), "s-aaaaaa", NONE).flags).toEqual(["awaiting the author on d-bbbbbb"]);
});
test("failing_ids_maps_paths", () => {
  const [a, b] = [decision({ id: "d-aaaaaa" }), entry({ id: "s-aaaaaa" })];
  const s = snapshotOf([a, b]);
  const result = checkResult(
    [
      problem({ path: s.paths.get("d-aaaaaa") as string, check: 3, message: "x" }),
      problem({ path: s.paths.get("d-aaaaaa") as string, check: 2, message: "y" }),
      problem({ path: s.paths.get("s-aaaaaa") as string, check: 2, message: "z" }),
      problem({ path: "lodge/spec/storage/_area.md", check: 7, message: "w" }),
    ],
    [],
  );
  expect(failingIds(s, result)).toEqual(new Set(["d-aaaaaa", "s-aaaaaa"]));
});
test("unrecorded_problem_for_unparsable_file", () => {
  const s = snapshotOf([decision({ id: "d-aaaaaa" })]);
  const broken = problem({
    path: "lodge/decisions/d-zzzzzz-broken.md",
    check: 1,
    message: "no fence",
    line: 1,
  });
  const held = problem({ path: s.paths.get("d-aaaaaa") as string, check: 3, message: "x" });
  const result = checkResult([held, broken], []);
  expect(unrecordedProblems(s, result)).toEqual([broken]);
  expect(failingIds(s, result)).toEqual(new Set(["d-aaaaaa"]));
});
test("level2_of_entry", () => {
  const spec = entry({ id: "s-aaaaaa", title: "Spec" });
  const old = decision({
    id: "d-aaaaaa",
    date: at(0),
    title: "Old",
    changes: CHANGE,
    reasoning: "Because.",
  });
  const next = decision({
    id: "d-bbbbbb",
    date: at(1),
    title: "New",
    changes: CHANGE,
    decidedBy: "author",
  });
  const s = snapshotOf([spec, old, next]);
  const d = derive(s);
  expect(level2(s, d, "d-aaaaaa", NONE)).toEqual("Because.");
  expect(level2(s, d, "s-aaaaaa", NONE)).toEqual(
    "d-bbbbbb · current · author · 2026-10-28 · product\nNew\n\nd-aaaaaa · current · coordinator · 2026-10-28 · product\nOld",
  );
  const bare = snapshotOf([entry({ id: "s-dddddd" })]);
  expect(level2(bare, derive(bare), "s-dddddd", NONE)).toEqual("");
});
test("level2_views_of_entry_are_level1_views_newest_first", () => {
  const spec = entry({ id: "s-aaaaaa", title: "Spec" });
  const old = decision({ id: "d-aaaaaa", date: at(0), changes: CHANGE });
  const next = decision({ id: "d-bbbbbb", date: at(1), changes: CHANGE, decidedBy: "author" });
  const s = snapshotOf([spec, old, next]);
  const d = derive(s);
  expect(level2Views(s, d, "s-aaaaaa", NONE).map((v) => v.id)).toEqual(["d-bbbbbb", "d-aaaaaa"]);
  expect(level2Views(s, d, "d-aaaaaa", NONE)).toEqual([]);
});
test("level3_reverse_links_with_status", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const base = decision({ id: "d-aaaaaa", date: at(0), changes: CHANGE, workItem: "plan.md" });
  const mid = decision({
    id: "d-bbbbbb",
    date: at(1),
    narrows: ["d-aaaaaa"],
    attachments: ["log.txt"],
  });
  const top = decision({
    id: "d-cccccc",
    date: at(2),
    replaces: ["d-aaaaaa"],
    changes: CHANGE,
    decidedBy: "author",
  });
  const confirm = decision({
    id: "d-dddddd",
    date: at(3),
    confirms: ["d-bbbbbb"],
    decidedBy: "author",
  });
  const s = snapshotOf([spec, base, mid, top, confirm]);
  const d = derive(s);
  let got = level3(s, d, "d-aaaaaa");
  expect(got.workItem).toEqual("plan.md");
  expect(got.links).toEqual([
    ["changes (edit)", "s-aaaaaa", "current"],
    ["replaced by", "d-cccccc", "current"],
    ["narrowed by", "d-bbbbbb", "current"],
  ]);
  got = level3(s, d, "d-bbbbbb");
  expect(got.attachments).toEqual(["log.txt"]);
  expect(got.links).toEqual([
    ["narrows", "d-aaaaaa", "replaced"],
    ["confirmed by", "d-dddddd", "current"],
  ]);
  expect(level3(s, d, "d-cccccc").links).toEqual([
    ["changes (edit)", "s-aaaaaa", "current"],
    ["replaces", "d-aaaaaa", "replaced"],
  ]);
  expect(level3(s, d, "d-cccccc").quote).toEqual(top.quote);
  expect(level3(s, d, "d-dddddd").links).toEqual([["confirms", "d-bbbbbb", "current"]]);
  expect(level3(s, d, "s-aaaaaa").links).toEqual([
    ["changed by", "d-cccccc", "current"],
    ["changed by", "d-aaaaaa", "replaced"],
  ]);
});
test("level3_unknown_target_and_provenance", () => {
  const nums = decision({ id: "d-aaaaaa", replaces: ["d-zzzzzz"], importedFrom: NOTES });
  const s = snapshotOf([nums]);
  const got = level3(s, derive(s), "d-aaaaaa");
  expect(got.links).toEqual([["replaces", "d-zzzzzz", "unknown"]]);
  expect(got.importedFrom).toEqual(NOTES);
});
test("format_level1_exact_text", () => {
  const old = decision({
    id: "d-3m8qk2",
    code: "ITEM-1",
    scope: Scope.PROCESS,
    decidedBy: "author",
    date: "2026-10-28T09:30:00+01:00",
    title: "Keep it short",
    statement: "Short and searchable.",
  });
  const next = decision({ id: "d-bbbbbb", replaces: ["d-3m8qk2"], date: at(5) });
  let s = snapshotOf([old, next]);
  const d = derive(s);
  expect(formatLevel1(level1(s, d, "d-3m8qk2", NONE))).toEqual(
    'd-3m8qk2 ITEM-1 · replaced · author · 2026-10-28 · process · replaced by d-bbbbbb · awaiting the author on d-bbbbbb\nKeep it short\n\nShort and searchable.\n\nquote: "Do it." (a session, 2026-10-28 10:00)',
  );
  const spec = entry({ id: "s-aaaaaa", title: "Spec", statement: "Holds.", area: "storage" });
  s = snapshotOf([spec]);
  expect(formatLevel1(level1(s, derive(s), "s-aaaaaa", NONE))).toEqual(
    "s-aaaaaa · current · no decision · storage\nSpec\n\nHolds.",
  );
});
test("format_level3_exact_text", () => {
  const d1 = decision({
    id: "d-aaaaaa",
    decidedBy: "author",
    quote: { text: "Do it.", where: "a session", when: "2026-10-28 10:00" },
    numbers: [{ value: "80", handle: "limits.words" }],
    workItem: "plan.md",
    attachments: ["log.txt"],
    importedFrom: NOTES,
    replaces: ["d-bbbbbb"],
    date: at(5),
  });
  const s = snapshotOf([d1, decision({ id: "d-bbbbbb" })]);
  const text = formatLevel3(level3(s, derive(s), "d-aaaaaa"));
  expect(text).toEqual(
    'quote: "Do it." (a session, 2026-10-28 10:00)\nnumbers: 80 (limits.words)\nwork item: plan.md\nattachments: log.txt\nimported from: notes.md, A heading\nreplaces: d-bbbbbb (replaced)',
  );
});
