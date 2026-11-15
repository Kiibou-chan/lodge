import { expect, test } from "bun:test";
import { Action, type Decision } from "#core";
import { area, at, decision, entry } from "./builders.ts";
import {
  check,
  creates,
  LATER,
  NOTES,
  NOW,
  OLD,
  published,
  REMEDY_CHECK_3,
  SPEC,
  state,
  verdict,
} from "./checks.ts";

test("clean_change_passes", () => {
  const added = entry({ id: "s-bbbbbb", title: "Another" });
  const after = state([
    area({ order: [SPEC, "s-bbbbbb"] }),
    added,
    creates("s-bbbbbb", { id: "d-bbbbbb", date: LATER }),
  ]);
  const result = check(published(), after);
  expect(result.ok).toBe(true);
  expect(result.notes).toEqual(["area storage: order changed"]);
});

test("nothing_changed_is_clean", () => {
  const result = check(published(), state([]));
  expect(result.ok).toBe(true);
  expect(result.notes).toEqual([]);
});

test("published_problem_is_note_not_failure", () => {
  const bad = decision({ id: "d-bbbbbb", decidedBy: "author", quote: null, date: at(1) });
  const before = state([bad]);
  const same = check(before, state([bad]));
  expect(same.ok).toBe(true);
  expect(same.notes.length).toEqual(1);
  expect(same.notes[0]).toContain(
    `d-bbbbbb: decided_by is author, but there is no quote${REMEDY_CHECK_3}`,
  );
  const worse = state([bad, decision({ id: "d-cccccc", replaces: ["d-zzzzzz"], date: LATER })]);
  expect(verdict(before, worse)).toEqual([
    [2, "d-cccccc: replaces d-zzzzzz, which does not exist"],
  ]);
});

test("new_state_problem_fails", () => {
  const after = state([decision({ id: "d-bbbbbb", replaces: ["d-zzzzzz"], date: LATER })]);
  expect(verdict(published(), after)).toEqual([
    [2, "d-bbbbbb: replaces d-zzzzzz, which does not exist"],
  ]);
});

test("check_2_published_record_missing_from_after", () => {
  const problems = check(published(), state([], [OLD])).problems;
  expect(problems.map((p) => [p.check, p.message])).toEqual([
    [2, "d-aaaaaa: was published and is missing from this state"],
  ]);
  expect(problems[0]?.path).toEqual(published().paths.get(OLD));
});

test.each(["replaces", "narrows", "confirms"].map((c) => [c] as const))(
  "check_1_new_decision_dated_no_later_than_its_target %p",
  (verb) => {
    for (const date of [at(0), "2026-10-28T09:00:00+00:00"]) {
      const added = decision({
        id: "d-bbbbbb",
        date: date,
        decidedBy: "author",
        ...{ [verb]: [OLD] },
      });
      const found = verdict(published(), state([added]));
      expect(found).toEqual([
        [1, `d-bbbbbb: dated ${date}, no later than ${OLD}, which it ${verb}`],
      ]);
    }
    const later = decision({
      id: "d-bbbbbb",
      date: LATER,
      decidedBy: "author",
      ...{ [verb]: [OLD] },
    });
    expect(verdict(published(), state([later]))).toEqual([]);
  },
);

test("check_1_dates_compare_as_instants", () => {
  const added = decision({ id: "d-bbbbbb", date: "2026-10-28T09:30:00+00:00", replaces: [OLD] });
  expect(verdict(published(), state([added]))).toEqual([]);
});

test("check_1_new_decision_sharing_an_entry_with_a_later_one", () => {
  const added = decision({
    id: "d-bbbbbb",
    date: at(0),
    changes: [{ entry: SPEC, action: Action.EDIT }],
  });
  const changed = entry({ id: SPEC, statement: "Now this." });
  expect(verdict(published(), state([added, changed]))).toEqual([
    [1, `d-bbbbbb: dated ${at(0)}, no later than ${OLD}, which shares ${SPEC} with it`],
  ]);
});

test("check_1_imported_decision_is_exempt_from_the_date_rule", () => {
  const added = decision({
    id: "d-bbbbbb",
    date: "2026-01-01T00:00:00+00:00",
    replaces: [OLD],
    importedFrom: NOTES,
  });
  expect(verdict(published(), state([added]))).toEqual([]);
});

test("check_1_published_decisions_are_not_dated_again", () => {
  const before = state([decision({ id: "d-bbbbbb", date: at(0), replaces: [OLD] })]);
  expect(
    verdict(before, state([decision({ id: "d-bbbbbb", date: at(0), replaces: [OLD] })])),
  ).toEqual([]);
});

function liveEdit(): Decision {
  return decision({ id: "d-bbbbbb", date: at(5), changes: [{ entry: SPEC, action: Action.EDIT }] });
}

test("check_1_import_changes_entry_changed_live", () => {
  const importedDecision = decision({
    id: "d-cccccc",
    date: at(1),
    changes: [{ entry: SPEC, action: Action.EDIT }],
    importedFrom: NOTES,
  });
  const found = verdict(state([liveEdit()]), state([liveEdit(), importedDecision]));
  expect(found).toEqual([
    [1, "d-cccccc: imported, changes s-aaaaaa, which a live decision already changed"],
  ]);
});

test("check_1_import_changes_entry_only_imports_changed", () => {
  const spec = entry({ id: "s-bbbbbb", importedFrom: NOTES });
  const first = decision({
    id: "d-bbbbbb",
    date: at(5),
    changes: [{ entry: spec.id, action: Action.CREATE }],
    importedFrom: NOTES,
  });
  const second = decision({
    id: "d-cccccc",
    date: at(1),
    changes: [{ entry: spec.id, action: Action.EDIT }],
    importedFrom: NOTES,
  });
  const placed = area({ order: [SPEC, spec.id] });
  expect(verdict(state([placed, spec, first]), state([placed, spec, first, second]))).toEqual([]);
});

test("area_title_change_is_note", () => {
  const result = check(published(), state([area({ order: [SPEC], title: "Renamed" })]));
  expect(result.ok).toBe(true);
  expect(result.notes).toEqual(["area storage: title changed"]);
});

test("area_intro_change_is_note", () => {
  const result = check(published(), state([area({ order: [SPEC], intro: "Words." })]));
  expect(result.ok).toBe(true);
  expect(result.notes).toEqual(["area storage: intro changed"]);
});

test("area_order_change_is_note", () => {
  const retire = decision({
    id: "d-bbbbbb",
    date: LATER,
    changes: [{ entry: SPEC, action: Action.RETIRE }],
  });
  const result = check(published(), state([area({ order: [] }), retire]));
  expect(result.ok).toBe(true);
  expect(result.notes).toEqual(["area storage: order changed"]);
});

test("check_1_new_decision_dated_after_the_time_of_the_change", () => {
  const future = "2027-10-28T11:00:00+01:00";
  const message = `d-bbbbbb: dated ${future}, which is after the time of this change`;
  const live = decision({
    id: "d-bbbbbb",
    date: future,
    changes: [{ entry: SPEC, action: Action.EDIT }],
  });
  expect(
    verdict(published(), state([live, entry({ id: SPEC, statement: "Now." })])),
  ).toContainEqual([1, message]);
  const importedDecision = decision({ id: "d-bbbbbb", date: future, importedFrom: NOTES });
  expect(verdict(published(), state([importedDecision]))).toEqual([[1, message]]);
});

test("check_1_a_decision_dated_exactly_now_passes", () => {
  const now = decision({ id: "d-bbbbbb", date: NOW });
  expect(verdict(published(), state([now]))).toEqual([]);
  const elsewhere = decision({ id: "d-cccccc", date: "2026-10-29T11:00:00+00:00" });
  expect(verdict(published(), state([elsewhere]))).toEqual([]);
});

test("published_future_dated_decision_is_not_dated_again", () => {
  const future = decision({ id: "d-bbbbbb", date: "2027-10-28T11:00:00+01:00" });
  expect(verdict(state([future]), state([future]))).toEqual([]);
});

test("area_added_and_removed_are_notes", () => {
  const other = area({ name: "other" });
  const added = check(published(), state([other]));
  expect(added.ok).toBe(true);
  expect(added.notes).toEqual(["area other: added"]);
  expect(check(state([other]), published()).notes).toEqual(["area other: removed"]);
});

test("area_rank_change_is_note", () => {
  const result = check(published(), state([area({ order: [SPEC], rank: 1 })]));
  expect(result.ok).toBe(true);
  expect(result.notes).toContain("area storage: rank changed");
});
