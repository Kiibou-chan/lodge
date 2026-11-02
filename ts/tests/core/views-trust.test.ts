import { expect, test } from "bun:test";
import { Action, derive, formatLevel1, level1, level2, level3, splitLines } from "#core";
import { at, decision, entry, snapshotOf } from "./builders.ts";
import { NOTES } from "./checks.ts";

const NONE = new Set<string>();
const CHANGE = [{ entry: "s-aaaaaa", action: Action.EDIT }];
test("level1_quote_on_decision_and_entry_when_author", () => {
  const spec = entry({ id: "s-aaaaaa", title: "Spec", statement: "Holds." });
  const quote = { text: "Do it.", where: "a session", when: "2026-10-28 10:00" };
  const author = decision({
    id: "d-aaaaaa",
    decidedBy: "author",
    date: at(0),
    changes: CHANGE,
    quote: quote,
  });
  let s = snapshotOf([spec, author]);
  const d = derive(s);
  expect(level1(s, d, "d-aaaaaa", NONE).quote).toEqual(quote);
  expect(level1(s, d, "s-aaaaaa", NONE).quote).toEqual(quote);
  expect(
    formatLevel1(level1(s, d, "s-aaaaaa", NONE)).endsWith(
      'Holds.\n\nquote: "Do it." (a session, 2026-10-28 10:00)',
    ),
  ).toBeTruthy();
  const agent = decision({ id: "d-bbbbbb", date: at(1), changes: CHANGE });
  s = snapshotOf([spec, author, agent]);
  expect(level1(s, derive(s), "s-aaaaaa", NONE).quote).toEqual(null);
  expect(level1(s, derive(s), "d-bbbbbb", NONE).quote).toEqual(null);
});
test("level2_heads_and_entry_name_a_failing_decision", () => {
  const spec = entry({ id: "s-aaaaaa", title: "Spec" });
  const bad = decision({
    id: "d-aaaaaa",
    decidedBy: "author",
    date: at(0),
    changes: CHANGE,
    title: "Bad",
  });
  const s = snapshotOf([spec, bad]);
  const d = derive(s);
  const failing = new Set<string>(["d-aaaaaa"]);
  expect(level1(s, d, "s-aaaaaa", failing).flags).toEqual(["decision fails check"]);
  expect(
    splitLines(level2(s, d, "s-aaaaaa", failing))[0]?.endsWith("· product · fails check"),
  ).toBeTruthy();
});
test("entry_whose_decision_is_replaced_or_narrowed", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const basis = decision({ id: "d-aaaaaa", date: at(0), changes: CHANGE });
  let s = snapshotOf([
    spec,
    basis,
    decision({ id: "d-bbbbbb", date: at(1), replaces: ["d-aaaaaa"] }),
  ]);
  expect(level1(s, derive(s), "s-aaaaaa", NONE).flags).toEqual([
    "its decision replaced by d-bbbbbb",
  ]);
  s = snapshotOf([spec, basis, decision({ id: "d-bbbbbb", date: at(1), narrows: ["d-aaaaaa"] })]);
  expect(level1(s, derive(s), "s-aaaaaa", NONE).flags).toEqual([
    "its decision narrowed by d-bbbbbb",
  ]);
});
test("flag_order_in_full", () => {
  const old = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), importedFrom: NOTES });
  const narrower = decision({ id: "d-bbbbbb", date: at(1), narrows: ["d-aaaaaa"] });
  const newer = decision({ id: "d-cccccc", date: at(2), replaces: ["d-aaaaaa"] });
  let s = snapshotOf([old, narrower, newer]);
  expect(level1(s, derive(s), "d-aaaaaa", new Set<string>(["d-aaaaaa"])).flags).toEqual([
    "replaced by d-cccccc",
    "narrowed by d-bbbbbb",
    "awaiting the author on d-cccccc, d-bbbbbb",
    "imported",
    "unquoted",
    "fails check",
  ]);
  const spec = entry({ id: "s-aaaaaa", importedFrom: NOTES });
  const basis = decision({
    id: "d-dddddd",
    date: at(3),
    changes: [{ entry: "s-aaaaaa", action: Action.RETIRE }],
  });
  s = snapshotOf([spec, basis, decision({ id: "d-eeeeee", date: at(4), narrows: ["d-dddddd"] })]);
  const failing = new Set<string>(["s-aaaaaa", "d-dddddd"]);
  expect(level1(s, derive(s), "s-aaaaaa", failing).flags).toEqual([
    "retired by d-dddddd",
    "its decision narrowed by d-eeeeee",
    "imported",
    "fails check",
    "decision fails check",
  ]);
});
test("entry_without_decision_says_so", () => {
  const s = snapshotOf([entry({ id: "s-dddddd", area: "storage" })]);
  const got = formatLevel1(level1(s, derive(s), "s-dddddd", NONE));
  expect(splitLines(got)[0]).toEqual("s-dddddd · current · no decision · storage");
});
test("level3_changes_carry_the_action", () => {
  const kill = decision({
    id: "d-aaaaaa",
    changes: [
      { entry: "s-aaaaaa", action: Action.CREATE },
      { entry: "s-bbbbbb", action: Action.RETIRE },
    ],
  });
  const s = snapshotOf([entry({ id: "s-aaaaaa" }), entry({ id: "s-bbbbbb" }), kill]);
  expect(level3(s, derive(s), "d-aaaaaa").links).toEqual([
    ["changes (create)", "s-aaaaaa", "current"],
    ["changes (retire)", "s-bbbbbb", "retired"],
  ]);
});
test("retired_by_names_a_standing_retirement", () => {
  const kill = [{ entry: "s-aaaaaa", action: Action.RETIRE }];
  const first = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: kill });
  const again = decision({ id: "d-cccccc", date: at(2), changes: kill });
  const undo = decision({
    id: "d-dddddd",
    decidedBy: "author",
    date: at(3),
    replaces: ["d-cccccc"],
  });
  const s = snapshotOf([entry({ id: "s-aaaaaa" }), first, again, undo]);
  expect(level1(s, derive(s), "s-aaaaaa", NONE).flags).toContain("retired by d-bbbbbb");
});
