import { expect, test } from "bun:test";
import { Action, type Decision, Scope } from "#core";
import { area, at, decision } from "./builders.ts";
import {
  check,
  creates,
  type Item,
  LATER,
  NOTES,
  OLD,
  oldDecision,
  published,
  REMEDY_CHECK_5,
  REMEDY_CHECK_5_REASONING,
  SPEC,
  state,
  verdict,
} from "./checks.ts";

const FIELD_NAMES: Readonly<Record<string, string>> = {
  decided_by: "decidedBy",
  work_item: "workItem",
  imported_from: "importedFrom",
};
const HEADER_EDITS = {
  title: "Another title",
  scope: Scope.PROCESS,
  decided_by: "coordinator",
  date: at(99),
  code: "NEW-1",
  changes: [
    { entry: SPEC, action: Action.CREATE },
    { entry: SPEC, action: Action.EDIT },
  ],
  replaces: ["d-bbbbbb"],
  narrows: ["d-bbbbbb"],
  confirms: ["d-bbbbbb"],
  work_item: "plans/x.md",
  quote: { text: "Other.", where: "a session", when: "2026-10-28 10:00" },
  numbers: [{ value: "3", handle: "a command" }],
  attachments: ["d-aaaaaa/run.log"],
  imported_from: NOTES,
};

test.each((Object.keys(HEADER_EDITS) as (keyof typeof HEADER_EDITS)[]).map((c) => [c] as const))(
  "check_5_header_key_of_a_published_decision_changed %p",
  (field) => {
    const key = FIELD_NAMES[field] ?? field;
    const edited = { ...oldDecision(), [key]: HEADER_EDITS[field] };
    const found = verdict(published(), state([edited]));
    expect(found).toContainEqual([
      5,
      `d-aaaaaa: ${field} of a published decision was changed${REMEDY_CHECK_5}`,
    ]);
  },
);

test("check_5_statement_changed", () => {
  const edited = { ...oldDecision(), statement: "Another statement." };
  expect(verdict(published(), state([edited]))).toContainEqual([
    5,
    `d-aaaaaa: statement of a published decision was changed${REMEDY_CHECK_5}`,
  ]);
});

test("author_reasoning_edit_fails", () => {
  const before = state([{ ...oldDecision(), reasoning: "Because it is so." }]);
  const after = state([{ ...oldDecision(), reasoning: "Because it was so." }]);
  expect(verdict(before, after)).toEqual([
    [
      5,
      `d-aaaaaa: reasoning of a published author decision was changed${REMEDY_CHECK_5_REASONING}`,
    ],
  ]);
});

function agent(reasoning: string): Decision {
  return creates(SPEC, { id: OLD, date: at(0), reasoning: reasoning });
}

test.each([
  ["Two words", "Now three words"],
  ["Now three words", "Two words"],
  ["one two three four five six", "six five four three two one"],
  ["Two\nwords", "Two   words"],
])("check_5_agent_reasoning_changed_in_any_way_fails %p %p", (before, after) => {
  expect(verdict(state([agent(before)]), state([agent(after)]))).toEqual([
    [5, `d-aaaaaa: reasoning of a published agent decision was changed${REMEDY_CHECK_5_REASONING}`],
  ]);
});

test("check_5_agent_reasoning_unchanged_passes", () => {
  const result = check(state([agent("Two words")]), state([agent("Two words")]));
  expect(result.ok).toBe(true);
  expect(result.notes).toEqual([]);
});

test("check_5_author_reasoning_reflowed_fails", () => {
  const before = state([{ ...oldDecision(), reasoning: "Two\nwords" }]);
  const after = state([{ ...oldDecision(), reasoning: "Two words" }]);
  expect(verdict(before, after)).toEqual([
    [
      5,
      `d-aaaaaa: reasoning of a published author decision was changed${REMEDY_CHECK_5_REASONING}`,
    ],
  ]);
});

test("check_5_new_decisions_are_not_compared", () => {
  const added = decision({
    id: "d-bbbbbb",
    date: LATER,
    reasoning: "Long enough to be a few words.",
  });
  expect(verdict(published(), state([added]))).toEqual([]);
});

function retiredAndReplaced(): Item[] {
  const retire = decision({
    id: "d-cccccc",
    date: at(2),
    changes: [{ entry: SPEC, action: Action.RETIRE }],
  });
  const newer = decision({ id: "d-bbbbbb", date: at(1), replaces: [OLD] });
  return [newer, retire, area({ order: [] })];
}

test.each(["narrows", "confirms"].map((c) => [c] as const))(
  "check_6_new_decision_links_to_a_replaced_decision %p",
  (verb) => {
    const before = state([...retiredAndReplaced()]);
    const added = decision({
      id: "d-dddddd",
      date: LATER,
      decidedBy: "author",
      ...{ [verb]: [OLD] },
    });
    const found = verdict(before, state([...retiredAndReplaced(), added]));
    expect(found).toEqual([[6, `d-dddddd: ${verb} ${OLD}, which is replaced`]]);
  },
);

test("replacing_a_decision_passes_check_6", () => {
  const before = state([...retiredAndReplaced()]);
  const added = decision({ id: "d-dddddd", date: LATER, replaces: [OLD] });
  expect(verdict(before, state([...retiredAndReplaced(), added]))).toEqual([]);
});

test("check_6_new_decision_changes_a_retired_entry", () => {
  const before = state([...retiredAndReplaced()]);
  const added = decision({
    id: "d-dddddd",
    date: LATER,
    changes: [{ entry: SPEC, action: Action.EDIT }],
  });
  const found = verdict(before, state([...retiredAndReplaced(), added]));
  expect(found).toContainEqual([
    6,
    "d-dddddd: changes s-aaaaaa with action edit, but the entry is retired",
  ]);
});

test("check_6_retiring_a_retired_entry_passes", () => {
  const before = state([...retiredAndReplaced()]);
  const added = decision({
    id: "d-dddddd",
    date: LATER,
    changes: [{ entry: SPEC, action: Action.RETIRE }],
  });
  expect(verdict(before, state([...retiredAndReplaced(), added]))).toEqual([]);
});

test("check_6_older_records_keep_their_links", () => {
  const oldLink = decision({ id: "d-eeeeee", date: at(3), narrows: [OLD] });
  const before = state([...retiredAndReplaced(), oldLink]);
  expect(verdict(before, before)).toEqual([]);
});
