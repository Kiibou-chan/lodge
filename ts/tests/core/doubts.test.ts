import { expect, test } from "bun:test";
import {
  Action,
  type Decision,
  derive,
  Raises,
  type SpecEntry,
  type Thread,
  ThreadState,
} from "#core";
import { at, decision, entry, thread } from "./builders.ts";
import { snapshotOf } from "./derivation.ts";

function marks(...items: (Decision | SpecEntry | Thread)[]) {
  return derive(snapshotOf(...items)).doubts;
}
test("open_doubt_marks_its_record", () => {
  const e = entry();
  expect(marks(e, thread({ about: e.id })).get(e.id)).toEqual(["in doubt"]);
});
test("closed_doubt_marks_nothing", () => {
  const e = entry();
  expect(marks(e, thread({ about: e.id, state: ThreadState.CLOSED })).size).toBe(0);
});
test("question_open_mark_and_no_propagation", () => {
  const a = entry();
  const b = entry({ restsOn: [a.id] });
  expect(marks(a, b, thread({ about: a.id, raises: Raises.QUESTION }))).toEqual(
    new Map([[a.id, ["question open"]]]),
  );
});
function chain() {
  const a = entry();
  const b = entry({ restsOn: [a.id] });
  const c = entry({ restsOn: [b.id] });
  return [a, b, c] as const;
}
test("doubt_reaches_entries_resting_on_it_further_down", () => {
  const [a, b, c] = chain();
  const m = marks(a, b, c, thread({ about: a.id }));
  expect(m.get(b.id)).toEqual(m.get(c.id));
  expect(m.get(c.id)).toEqual([`rests on ${a.id}, in doubt`]);
});
test("doubt_on_decision_marks_entries_it_created_and_last_changed", () => {
  const [a, b, c] = chain();
  let d = decision({
    changes: [
      { entry: a.id, action: Action.CREATE },
      { entry: b.id, action: Action.EDIT },
    ],
  });
  const old = entry({ restsOn: [] });
  d = decision({
    id: d.id,
    changes: [...d.changes, { entry: old.id, action: Action.EDIT }],
    date: at(0),
  });
  const later = decision({ changes: [{ entry: old.id, action: Action.EDIT }], date: at(1) });
  const m = marks(a, b, c, old, d, later, thread({ about: d.id }));
  expect(m.has(old.id)).toBe(false);
  expect(m.get(a.id)?.includes(`changed by ${d.id}, in doubt`)).toBe(true);
  expect(m.get(b.id)?.includes(`changed by ${d.id}, in doubt`)).toBe(true);
});
test("doubt_on_decision_reaches_what_rests_on_its_entries", () => {
  const [a, b, c] = chain();
  const d = decision({ changes: [{ entry: a.id, action: Action.CREATE }] });
  expect(marks(a, b, c, d, thread({ about: d.id })).get(c.id)).toEqual([
    `rests on ${a.id}, in doubt`,
  ]);
});
test("cycle_of_rests_on_does_not_hang", () => {
  const a = entry({ id: "s-aaaaaa", restsOn: ["s-bbbbbb"] });
  const b = entry({ id: "s-bbbbbb", restsOn: [a.id] });
  const m = marks(a, b, thread({ about: a.id }));
  expect(m.get(b.id)).toEqual([`rests on ${a.id}, in doubt`]);
});
test.todo("confirmed_decision_shows_confirmation_and_keeps_decided_by");
test.todo("flag_order");
