import { expect, test } from "bun:test";
import { Action, type CheckResult, checkState } from "#core";
import { area, at, decision, entry, snapshotOf } from "./builders.ts";
import { check } from "./checks.ts";

const A = entry({ id: "s-aaaaaa" }),
  B = entry({ id: "s-bbbbbb" });
function trial(action: Action | null, statement = A.statement, isNew = false): CheckResult {
  const before = snapshotOf([area(), B, ...(isNew ? [] : [A])]);
  const changed = { ...A, restsOn: [B.id], statement };
  const decisions =
    action === null
      ? []
      : [decision({ id: "d-cccccc", date: at(30), changes: [{ entry: A.id, action }] })];
  return check(before, snapshotOf([area(), B, changed, ...decisions]));
}
test("link_changing_rests_on_only_passes", () => expect(trial(Action.LINK).ok).toBe(true));
test("rests_on_change_without_decision_fails_check_4", () => {
  expect(trial(null).problems.map((p) => [p.check, p.message])).toEqual([
    [
      4,
      "s-aaaaaa: edited, but no new decision in this change lists it with action edit or link; list it in the decision's changes",
    ],
  ]);
});
test("edit_may_change_rests_on", () => expect(trial(Action.EDIT).ok).toBe(true));
const textProblem =
  "d-cccccc: lists link for s-aaaaaa, which changes more than rests_on; list it with action edit in another decision of this change";
test("link_changing_the_statement_fails_check_4", () => {
  expect(
    trial(Action.LINK, "Changed.").problems.some((p) => p.check === 4 && p.message === textProblem),
  ).toBe(true);
});
test("link_for_a_new_entry_fails_check_4", () => {
  expect(
    trial(Action.LINK, A.statement, true).problems.some(
      (p) =>
        p.check === 4 &&
        p.message ===
          "d-cccccc: lists link for s-aaaaaa, which is new; list it with action create in another decision of this change",
    ),
  ).toBe(true);
});
test("unknown_rests_on_fails_check_2", () => {
  expect(
    checkState(snapshotOf([area(), { ...A, restsOn: [B.id] }])).problems.some(
      (p) => p.check === 2 && p.message === "s-aaaaaa: rests_on s-bbbbbb, which does not exist",
    ),
  ).toBe(true);
});
test("rests_on_itself_fails_check_2", () => {
  const found = checkState(snapshotOf([area(), { ...A, restsOn: [A.id] }])).problems;
  expect(found.some((p) => p.check === 2 && p.message === "s-aaaaaa: rests_on itself")).toBe(true);
  expect(found.some((p) => p.check === 8)).toBe(false);
});
test("two_entry_cycle_fails_check_8_on_both", () => {
  const s = snapshotOf([area(), { ...A, restsOn: [B.id] }, { ...B, restsOn: [A.id] }]);
  expect(
    checkState(s)
      .problems.filter((p) => p.check === 8)
      .map((p) => [p.path, p.message]),
  ).toEqual([
    [s.paths.get(A.id) as string, "s-aaaaaa: is in a cycle of rests_on links with s-bbbbbb"],
    [s.paths.get(B.id) as string, "s-bbbbbb: is in a cycle of rests_on links with s-aaaaaa"],
  ]);
});
test("three_entry_cycle_names_the_other_two", () => {
  const c = entry({ id: "s-cccccc", restsOn: [A.id] }),
    d = entry({ id: "s-dddddd", restsOn: [A.id] }),
    e = entry({ id: "s-eeeeee" });
  const s = snapshotOf([
    area(),
    { ...A, restsOn: [B.id, e.id] },
    { ...B, restsOn: [c.id] },
    c,
    d,
    e,
  ]);
  expect(
    checkState(s)
      .problems.filter((p) => p.check === 8)
      .map((p) => p.message),
  ).toEqual(
    [A.id, B.id, c.id].map(
      (id) =>
        `${id}: is in a cycle of rests_on links with ${[A.id, B.id, c.id].filter((t) => t !== id).join(", ")}`,
    ),
  );
});
test("new_rest_on_retired_entry_fails_check_6", () => {
  const retired = decision({ changes: [{ entry: B.id, action: Action.RETIRE }] });
  expect(
    check(
      snapshotOf([area(), A, B, retired]),
      snapshotOf([area(), { ...A, restsOn: [B.id] }, B, retired]),
    ).problems.some(
      (p) => p.check === 6 && p.message === "s-aaaaaa: rests on s-bbbbbb, which is retired",
    ),
  ).toBe(true);
});
test("kept_rest_on_retired_entry_passes_check_6", () => {
  const retired = decision({ changes: [{ entry: B.id, action: Action.RETIRE }] });
  const before = snapshotOf([area(), { ...A, restsOn: [B.id] }, B, retired]);
  expect(check(before, before).problems.some((p) => p.check === 6)).toBe(false);
});
test.each([
  [false, Action.EDIT],
  [true, Action.CREATE],
] as const)("link_with_another_decision_accounting_for_text_passes %p %p", (isNew, action) => {
  const before = snapshotOf([
    area({ order: isNew ? [B.id] : [B.id, A.id] }),
    B,
    ...(isNew ? [] : [A]),
  ]);
  const changed = { ...A, statement: "Changed.", restsOn: [B.id] };
  const link = decision({
    id: "d-cccccc",
    date: at(30),
    changes: [{ entry: A.id, action: Action.LINK }],
  });
  const edit = decision({ id: "d-dddddd", date: at(31), changes: [{ entry: A.id, action }] });
  expect(
    check(before, snapshotOf([area({ order: [B.id, A.id] }), B, changed, link, edit])).ok,
  ).toBe(true);
});
test.each(["statement", "title"].map((c) => [c]))(
  "link_without_another_decision_accounting_for_text_fails %p",
  (field) => {
    const changed = { ...A, restsOn: [B.id], [field]: "Changed." };
    const link = decision({
      id: "d-cccccc",
      date: at(30),
      changes: [{ entry: A.id, action: Action.LINK }],
    });
    const unrelated = decision({
      id: "d-dddddd",
      date: at(31),
      changes: [{ entry: B.id, action: Action.EDIT }],
    });
    expect(
      check(
        snapshotOf([area(), A, B]),
        snapshotOf([area(), changed, B, link, unrelated]),
      ).problems.some((p) => p.check === 4 && p.message === textProblem),
    ).toBe(true);
  },
);
