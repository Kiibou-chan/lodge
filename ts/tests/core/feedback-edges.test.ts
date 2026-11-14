import { expect, test } from "bun:test";
import {
  Action,
  areaFeedback,
  areaPath,
  derive,
  feedback,
  lengthGuidance,
  type Record,
} from "#core";
import { area, at, decision, entry, snapshotOf } from "./builders.ts";

// TypeScript additions pin gaps shared with the Python feedback tests.
function messages(added: Record, items: readonly Record[] = []) {
  const s = snapshotOf([...items, added]);
  return feedback([added], s, derive(s), lengthGuidance()).map((f) => f.message);
}
const numberMessage = (values: string) =>
  `the text holds ${values.includes(", ") ? "the numbers" : "the number"} ${values} without a numbers handle; before adding the draft, give each one as \`numbers: [{value: "…", handle: "…"}]\`, the handle a record and key or a runnable command`;
test.each([
  ["x3 item-1 4\u00a0% 5 5", "4\u00a0%, 5"],
  ["xitem-1 item-1x d-123456x xs-123456 7", "1, 123456, 7"],
  ["2026-10-28 `2026-10-28 8` d-123456 9 9", "9"],
  ["4\u001c% 5\u0085%", "4\u001c%, 5\u0085%"],
])("number_scan_edges %p", (statement, values) => {
  const other = decision({ code: "ITEM-1" });
  expect(messages(decision({ statement }), [other])).toEqual([numberMessage(values)]);
});
test("astral_title_counts_code_points", () => {
  const d = decision({ title: "𐐀".repeat(21) });
  const s = snapshotOf([d]);
  expect(feedback([d], s, derive(s), lengthGuidance({ titleChars: 20 }))).toEqual([
    { recordId: d.id, message: "the title is 21 characters; guidance is 20 or fewer, on one line" },
  ]);
});
test("spec_at_word_limit_is_clean", () => {
  const e = entry({ statement: "one two" });
  const s = snapshotOf([e]);
  expect(feedback([e], s, derive(s), lengthGuidance({ specStatementWords: 2 }))).toEqual([]);
});
function editScenario(replacedBy = "coordinator", addedBy = "author") {
  const e = entry({ id: "s-aaaaaa" });
  const edit = decision({
    id: "d-bbbbbb",
    decidedBy: replacedBy,
    date: at(1),
    changes: [{ entry: e.id, action: Action.EDIT }],
  });
  const added = decision({ id: "d-cccccc", decidedBy: addedBy, date: at(2), replaces: [edit.id] });
  return { e, edit, added };
}
test.each([
  ["coordinator", "coordinator"],
  ["author", "author"],
])("edit_back_is_only_author_rejecting_agent %p %p", (oldBy, newBy) => {
  const { e, edit, added } = editScenario(oldBy, newBy);
  expect(messages(added, [e, edit])).toEqual([]);
});
test("own_change_suppresses_edit_back_and_revival", () => {
  const { e, edit, added } = editScenario();
  const retire = decision({
    id: "d-dddddd",
    decidedBy: "author",
    date: at(1),
    changes: [{ entry: e.id, action: Action.RETIRE }],
  });
  expect(
    messages(
      { ...added, replaces: [edit.id, retire.id], changes: [{ entry: e.id, action: Action.LINK }] },
      [e, edit, retire],
    ),
  ).toEqual([]);
});
test("edit_back_entries_are_sorted", () => {
  const { e, edit, added } = editScenario();
  const other = entry({ id: "s-bbbbbb" });
  const changes = [other, e].map((v) => ({ entry: v.id, action: Action.EDIT }));
  expect(
    messages(added, [e, other, { ...edit, changes }]).map(
      (m) => m.match(/whose edit of (s-\w+)/u)?.[1],
    ),
  ).toEqual([e.id, other.id]);
});
test.each([Action.CREATE, Action.LINK])(
  "newest_text_change_checks_action_and_entry %p",
  (action) => {
    const { e, edit, added } = editScenario();
    const later = decision({
      id: "d-dddddd",
      date: at(3),
      changes: [
        { entry: "s-bbbbbb", action: Action.EDIT },
        { entry: e.id, action },
      ],
    });
    const found = messages(added, [e, edit, later]);
    if (action === Action.CREATE) expect(found).toEqual([]);
    else
      expect(found).toEqual([
        `it replaces ${edit.id}, whose edit of ${e.id} is still the latest edit of that entry; does ${added.id} edit ${e.id} back? If so, add an edit draft of ${e.id} and list it in changes with action edit`,
      ]);
  },
);
test("area_rank_feedback_skips_unranked_and_sorts_both_lists", () => {
  const areas = ["z", "c", "b", "a"].map((name) => area({ name, rank: 1 }));
  const unranked = [area({ name: "plain" }), area({ name: "other" })];
  const s = snapshotOf([...areas, ...unranked]);
  expect(
    areaFeedback(
      s,
      [...areas, ...unranked].map((a) => areaPath(a.name)),
    ),
  ).toEqual([
    {
      recordId: "area:a",
      message:
        "rank 1 is shared with area b, c, and z; areas that share a rank are ordered by name",
    },
    {
      recordId: "area:b",
      message:
        "rank 1 is shared with area a, c, and z; areas that share a rank are ordered by name",
    },
    {
      recordId: "area:c",
      message:
        "rank 1 is shared with area a, b, and z; areas that share a rank are ordered by name",
    },
    {
      recordId: "area:z",
      message:
        "rank 1 is shared with area a, b, and c; areas that share a rank are ordered by name",
    },
  ]);
});

test("entry_id_start_boundary", () => {
  const other = entry({ id: "s-123456" });
  expect(messages(entry({ statement: "xs-123456" }), [other])).toEqual([]);
});
test("dates_are_hidden_before_known_codes", () => {
  const other = decision({ code: "X-2026" });
  expect(messages(decision({ statement: "X-2026-10-28" }), [other])).toEqual([]);
});
test.each([
  ["item-1x 7", "1, 7"],
  ["xitem-1 7", "1, 7"],
  ["3ITEM-1 7", "3, 1, 7"],
  ["d-123456x 7", "123456, 7"],
  ["ITEM-1 7 8", "7, 8"],
])("individual_number_boundaries %p", (statement, values) => {
  expect(messages(decision({ statement }), [decision({ code: "ITEM-1" })])).toEqual([
    numberMessage(values),
  ]);
});
test("newest_text_change_does_not_borrow_another_entry_action", () => {
  const { e, edit, added } = editScenario();
  const other = entry({ id: "s-bbbbbb" });
  const later = decision({
    id: "d-dddddd",
    date: at(3),
    changes: [
      { entry: other.id, action: Action.EDIT },
      { entry: e.id, action: Action.RETIRE },
    ],
  });
  expect(messages(added, [e, other, edit, later])).toEqual([
    `it replaces ${edit.id}, whose edit of ${e.id} is still the latest edit of that entry; does ${added.id} edit ${e.id} back? If so, add an edit draft of ${e.id} and list it in changes with action edit`,
  ]);
});
