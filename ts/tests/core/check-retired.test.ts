import { expect, test } from "bun:test";
import { Action } from "#core";
import { area, at, decision, entry } from "./builders.ts";
import { type Item, LATER, SPEC, state, verdict } from "./checks.ts";

function retired(): Item[] {
  const retire = decision({
    id: "d-cccccc",
    date: at(2),
    changes: [{ entry: SPEC, action: Action.RETIRE }],
  });
  return [retire, area({ order: [] })];
}

test("check_6_replacing_the_retirement_lets_the_decision_edit_the_entry_again", () => {
  const before = state([...retired()]);
  const back = decision({
    id: "d-dddddd",
    date: LATER,
    replaces: ["d-cccccc"],
    changes: [{ entry: SPEC, action: Action.EDIT }],
  });
  const restored = entry({ id: SPEC, statement: "Restored." });
  const after = state([...retired(), back, restored, area({ order: [SPEC] })]);
  expect(verdict(before, after)).toEqual([]);
});

test("check_6_a_later_decision_may_edit_an_entry_whose_retirement_was_replaced", () => {
  const back = decision({ id: "d-dddddd", date: at(5), replaces: ["d-cccccc"] });
  const items = [...retired(), back, area({ order: [SPEC] })];
  const added = decision({
    id: "d-eeeeee",
    date: LATER,
    changes: [{ entry: SPEC, action: Action.EDIT }],
  });
  const after = state([...items, added, entry({ id: SPEC, statement: "Edited." })]);
  expect(verdict(state([...items]), after)).toEqual([]);
});
