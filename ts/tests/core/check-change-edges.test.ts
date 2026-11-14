import { expect, test } from "bun:test";
import { Action, checkChange, coreSettings } from "#core";
import { area, at, decision, entry, snapshotOf } from "./builders.ts";

const NOW = at(10);
// TypeScript additions cover mutation gaps shared by Python.
test("new_replacement_and_narrowing_use_published_status", () => {
  const old = decision({ id: "d-aaaaaa" });
  const before = snapshotOf([old]);
  const after = snapshotOf([
    old,
    decision({ id: "d-bbbbbb", date: at(1), replaces: [old.id] }),
    decision({ id: "d-cccccc", date: at(2), narrows: [old.id] }),
  ]);
  expect(checkChange(before, after, coreSettings(), NOW).problems).toEqual([]);
});
test("change_problems_are_sorted_and_duplicate_changes_report_once", () => {
  const e = entry({ id: "s-aaaaaa" });
  const retire = decision({ id: "d-aaaaaa", changes: [{ entry: e.id, action: Action.RETIRE }] });
  const before = snapshotOf([area(), e, retire]);
  const change = { entry: e.id, action: Action.EDIT };
  const d = decision({ id: "d-bbbbbb", date: at(1), changes: [change, change] });
  const after = snapshotOf([
    area({ order: ["s-bbbbbb"] }),
    e,
    entry({ id: "s-bbbbbb" }),
    retire,
    d,
  ]);
  const result = checkChange(before, after, coreSettings(), NOW);
  expect(result.problems.map((p) => [p.path, p.check, p.message])).toEqual([
    [
      after.paths.get(d.id) as string,
      6,
      "d-bbbbbb: changes s-aaaaaa with action edit, but the entry is retired",
    ],
    [
      after.paths.get("s-bbbbbb") as string,
      4,
      "s-bbbbbb: created, but no new decision in this change lists it with action create; list it in the decision's changes",
    ],
  ]);
});
