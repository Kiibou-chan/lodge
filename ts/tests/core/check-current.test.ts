import { expect, test } from "bun:test";
import { Action, checkChange, type Decision } from "#core";
import { at, decision } from "./builders.ts";
import { NOW, published, SETTINGS, SPEC, state } from "./checks.ts";

function edits(kw: Partial<Decision> = {}): Decision {
  return decision({ changes: [{ entry: SPEC, action: Action.EDIT }], ...kw });
}

test("new_decision_must_be_after_an_unpublished_one_it_shares_an_entry_with", () => {
  const unpublished = edits({ id: "d-bbbbbb", date: at(10) });
  const current = state([unpublished]);
  const tie = edits({ id: "d-cccccc", date: at(10) });
  const result = checkChange(published(), state([unpublished, tie]), SETTINGS, NOW, current);
  expect(result.problems.map((p) => [p.check, p.message])).toEqual([
    [1, `d-cccccc: dated ${at(10)}, no later than d-bbbbbb, which shares ${SPEC} with it`],
  ]);
});

test("new_decision_after_an_unpublished_one_passes", () => {
  const unpublished = edits({ id: "d-bbbbbb", date: at(10) });
  const later = edits({ id: "d-cccccc", date: at(11) });
  const after = state([unpublished, later]);
  expect(checkChange(published(), after, SETTINGS, NOW, state([unpublished])).ok).toBe(true);
});

test("without_the_current_state_only_published_decisions_count", () => {
  const unpublished = edits({ id: "d-bbbbbb", date: at(10) });
  const tie = edits({ id: "d-cccccc", date: at(10) });
  expect(checkChange(published(), state([unpublished, tie]), SETTINGS, NOW).ok).toBe(true);
});

test("an_unpublished_decision_is_not_held_to_a_newer_one", () => {
  const older = edits({ id: "d-bbbbbb", date: at(10) });
  const newer = edits({ id: "d-cccccc", date: at(11) });
  const third = edits({ id: "d-dddddd", date: at(12) });
  const current = state([older, newer]);
  expect(checkChange(published(), state([older, newer, third]), SETTINGS, NOW, current).ok).toBe(
    true,
  );
});
