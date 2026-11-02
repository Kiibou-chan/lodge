import { expect, test } from "bun:test";
import { Action, type SpecEntry } from "#core";
import { area, at, decision, entry } from "./builders.ts";
import {
  creates,
  LATER,
  NOTES,
  OLD,
  published,
  REMEDY_CHECK_4,
  SPEC,
  state,
  verdict,
} from "./checks.ts";

const NEW = "s-bbbbbb";
const NEW_AREA = area({ order: [SPEC, NEW] });
const wanted = (id: string, verb: string, action: string): [[number, string]] => [
  [
    4,
    `${id}: ${verb}, but no new decision in this change lists it with action ${action}${REMEDY_CHECK_4}`,
  ],
];
const importedEntryState = () => [entry({ id: NEW, importedFrom: NOTES }), NEW_AREA];

test("check_4_new_entry_without_a_decision", () => {
  expect(verdict(published(), state([entry({ id: NEW }), NEW_AREA]))).toEqual(
    wanted(NEW, "created", "create"),
  );
});
test("check_4_new_entry_listed_with_the_wrong_action", () => {
  const wrong = decision({
    id: "d-bbbbbb",
    date: LATER,
    changes: [{ entry: NEW, action: Action.EDIT }],
  });
  expect(
    verdict(published(), state([entry({ id: NEW }), NEW_AREA, wrong])).map(([c]) => c),
  ).toEqual([4]);
});
test("check_4_published_decision_does_not_count", () => {
  const early = creates(NEW, { id: "d-bbbbbb", date: at(1) });
  expect(
    verdict(state([early]), state([early, entry({ id: NEW }), NEW_AREA])).map(([c]) => c),
  ).toEqual([4]);
});
test.each((["title", "statement", "code"] as const).map((c) => [c]))(
  "check_4_edited_entry_without_a_decision %p",
  (field) => {
    const changed = { ...entry({ id: SPEC }), [field]: "Something else" };
    expect(verdict(published(), state([changed]))).toEqual(wanted(SPEC, "edited", "edit"));
  },
);
test("check_4_edited_entry_with_a_decision_passes", () => {
  const edit = decision({
    id: "d-bbbbbb",
    date: LATER,
    changes: [{ entry: SPEC, action: Action.EDIT }],
  });
  expect(verdict(published(), state([entry({ id: SPEC, statement: "Now this." }), edit]))).toEqual(
    [],
  );
});
test("check_4_retired_entry_without_a_retiring_decision", () => {
  const both = decision({
    id: OLD,
    date: at(0),
    decidedBy: "author",
    changes: [
      { entry: SPEC, action: Action.CREATE },
      { entry: SPEC, action: Action.RETIRE },
    ],
  });
  expect(verdict(published(), state([both, area({ order: [] })]))).toContainEqual(
    wanted(SPEC, "retired", "retire")[0],
  );
});
test("check_4_retired_entry_with_a_decision_passes", () => {
  const retire = decision({
    id: "d-bbbbbb",
    date: LATER,
    changes: [{ entry: SPEC, action: Action.RETIRE }],
  });
  expect(verdict(published(), state([retire, area({ order: [] })]))).toEqual([]);
});
test("check_4_new_imported_entry_needs_no_decision", () => {
  expect(verdict(published(), state(importedEntryState()))).toEqual([]);
});
test("check_4_imported_entry_edit_needs_a_decision", () => {
  const edited = entry({ id: NEW, importedFrom: NOTES, statement: "Rewritten by hand." });
  expect(verdict(state(importedEntryState()), state([edited, NEW_AREA]))).toEqual(
    wanted(NEW, "edited", "edit"),
  );
});
test("check_4_imported_entry_edit_through_an_import_passes", () => {
  const edit = decision({
    id: "d-cccccc",
    date: LATER,
    changes: [{ entry: NEW, action: Action.EDIT }],
    importedFrom: NOTES,
  });
  const edited = entry({ id: NEW, importedFrom: NOTES, statement: "Re-imported." });
  expect(verdict(state(importedEntryState()), state([edited, NEW_AREA, edit]))).toEqual([]);
});
test("check_4_imported_from_added_to_a_live_entry_is_an_edit", () => {
  expect(verdict(published(), state([entry({ id: SPEC, importedFrom: NOTES })]))).toEqual(
    wanted(SPEC, "edited", "edit"),
  );
});
test("check_4_laundering_over_two_changes_fails_at_each_step", () => {
  const one = state([entry({ id: SPEC, importedFrom: NOTES })]);
  const two = state([entry({ id: SPEC, importedFrom: NOTES, statement: "Rewritten." })]);
  expect(verdict(published(), one)).toEqual(wanted(SPEC, "edited", "edit"));
  expect(verdict(one, two)).toEqual(wanted(SPEC, "edited", "edit"));
});
test("check_4_imported_from_removed_is_an_edit", () => {
  expect(verdict(state(importedEntryState()), state([entry({ id: NEW }), NEW_AREA]))).toEqual(
    wanted(NEW, "edited", "edit"),
  );
});
test("check_4_entry_moved_to_another_area_is_an_edit", () => {
  const moved: SpecEntry = entry({ id: SPEC, area: "other" });
  expect(
    verdict(
      published(),
      state([moved, area({ order: [] }), area({ name: "other", order: [SPEC] })]),
    ),
  ).toEqual(wanted(SPEC, "edited", "edit"));
});
test("check_4_create_for_an_entry_that_exists", () => {
  expect(verdict(published(), state([creates(SPEC, { id: "d-bbbbbb", date: LATER })]))).toEqual([
    [4, "d-bbbbbb: lists create for s-aaaaaa, which already exists"],
  ]);
});
test("check_4_import_from_an_unlisted_file", () => {
  const other = { file: "elsewhere.md", heading: "H" };
  expect(verdict(published(), state([entry({ id: NEW, importedFrom: other }), NEW_AREA]))).toEqual([
    [4, "s-bbbbbb: imported from elsewhere.md, which is not listed in [import] sources"],
  ]);
  expect(
    verdict(published(), state([decision({ id: "d-bbbbbb", date: LATER, importedFrom: other })])),
  ).toEqual([[4, "d-bbbbbb: imported from elsewhere.md, which is not listed in [import] sources"]]);
});
test("check_4_published_import_from_an_unlisted_file_is_left_alone", () => {
  const items = () => [
    entry({ id: NEW, importedFrom: { file: "elsewhere.md", heading: "H" } }),
    NEW_AREA,
  ];
  expect(verdict(state(items()), state(items()))).toEqual([]);
});
