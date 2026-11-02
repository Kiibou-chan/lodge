import { expect, test } from "bun:test";
import {
  Action,
  checkState,
  type Decision,
  load,
  newRecordPath,
  problem,
  type Snapshot,
  tree,
} from "#core";
import { area, at, decision, entry, filesOf, snapshotOf } from "./builders.ts";
import { REMEDY_ATTACH, REMEDY_CHECK_3 } from "./checks.ts";

const SPEC = "s-aaaaaa";
const OLD = decision({
  id: "d-aaaaaa",
  date: at(0),
  changes: [{ entry: SPEC, action: Action.CREATE }],
});
function world(...extra: Parameters<typeof snapshotOf>[0]) {
  return snapshotOf([area({ order: [SPEC] }), entry({ id: SPEC }), OLD, ...extra]);
}
function lines(s: Snapshot) {
  return checkState(s).problems.map((p) => [p.check, p.message]);
}
test("clean_state_passes", () => {
  const r = checkState(world());
  expect(r.ok).toBe(true);
  expect(r.problems).toEqual([]);
  expect(r.notes).toEqual([]);
});
test("check_1_parse_problem_is_reported", () => {
  const bad = problem({
    path: "lodge/decisions/d-bbbbbb-x.md",
    check: 1,
    message: "the header is not closed",
    line: 3,
  });
  expect(checkState(world()).ok).toBe(true);
  expect(checkState(snapshotOf([], { problems: [bad] })).problems).toEqual([bad]);
});
test("check_1_file_name_without_the_id", () => {
  const paths = new Map([["d-bbbbbb", "lodge/decisions/d-cccccc-misnamed.md"]]);
  const s = snapshotOf([area(), decision({ id: "d-bbbbbb" })], { paths });
  expect(lines(s)).toEqual([
    [1, "d-bbbbbb: the file name d-cccccc-misnamed.md does not start with the ID"],
  ]);
  expect(checkState(s).problems[0]?.path).toBe(paths.get("d-bbbbbb") as string);
});
test("check_1_file_name_of_the_bare_id_passes", () => {
  expect(
    checkState(
      snapshotOf([decision({ id: "d-bbbbbb" })], {
        paths: new Map([["d-bbbbbb", "lodge/decisions/d-bbbbbb.md"]]),
      }),
    ).ok,
  ).toBe(true);
});
test("check_1_file_name_that_only_begins_like_the_id", () => {
  expect(
    checkState(
      snapshotOf([decision({ id: "d-bbbbbb" })], {
        paths: new Map([["d-bbbbbb", "lodge/decisions/d-bbbbbbx-title.md"]]),
      }),
    ).ok,
  ).toBe(false);
});
test.each<[string, Partial<Decision>]>([
  ["changes", { changes: [{ entry: "s-zzzzzz", action: Action.EDIT }] }],
  ["replaces", { replaces: ["d-zzzzzz"] }],
  ["narrows", { narrows: ["d-zzzzzz"] }],
  ["confirms", { confirms: ["d-zzzzzz"] }],
])("check_2_unresolved_link %p %p", (field, kw) => {
  expect(lines(world(decision({ id: "d-bbbbbb", decidedBy: "author", ...kw })))).toEqual([
    [2, `d-bbbbbb: ${field} ${field === "changes" ? "s" : "d"}-zzzzzz, which does not exist`],
  ]);
});
test("check_2_links_that_resolve_pass", () => {
  expect(
    checkState(
      world(
        decision({
          id: "d-bbbbbb",
          decidedBy: "author",
          changes: [{ entry: SPEC, action: Action.EDIT }],
          replaces: ["d-aaaaaa"],
          narrows: ["d-aaaaaa"],
          confirms: ["d-aaaaaa"],
        }),
      ),
    ).ok,
  ).toBe(true);
});
test("check_2_one_problem_per_unresolved_link", () => {
  expect(
    lines(world(decision({ id: "d-bbbbbb", replaces: ["d-yyyyyy", "d-zzzzzz", "d-zzzzzz"] }))).map(
      ([, m]) => m,
    ),
  ).toEqual([
    "d-bbbbbb: replaces d-yyyyyy, which does not exist",
    "d-bbbbbb: replaces d-zzzzzz, which does not exist",
  ]);
});
test("check_2_duplicate_id_from_load_is_reported", () => {
  const first = decision({ id: "d-aaaaaa", title: "First" }),
    second = decision({ id: "d-aaaaaa", title: "Second" });
  expect(
    checkState(
      load(tree({ rev: null, files: new Map([...filesOf(first), ...filesOf(second)]) })),
    ).problems.map((p) => p.check),
  ).toEqual([2, 2]);
});
test("check_2_codes_compared_without_case", () => {
  const s = world(
    decision({ id: "d-bbbbbb", code: "ITEM-1" }),
    entry({ id: "s-bbbbbb", code: "item-1" }),
  );
  expect(
    lines({ ...s, areas: new Map([["storage", area({ order: [SPEC, "s-bbbbbb"] })]]) }).map(
      ([, m]) => m,
    ),
  ).toEqual([
    "d-bbbbbb: code ITEM-1 is shared with another record, compared without regard to case",
    "s-bbbbbb: code item-1 is shared with another record, compared without regard to case",
  ]);
});
test("check_2_distinct_codes_pass", () => {
  expect(
    checkState(
      world(
        decision({ id: "d-bbbbbb", code: "ITEM-1" }),
        decision({ id: "d-cccccc", code: "ITEM-2" }),
      ),
    ).ok,
  ).toBe(true);
});
test("check_2_listed_attachment_missing", () => {
  expect(lines(world(decision({ id: "d-bbbbbb", attachments: ["run.log"] })))).toEqual([
    [2, `d-bbbbbb: lists attachment run.log, which does not exist${REMEDY_ATTACH}`],
  ]);
});
test("check_2_listed_attachment_resolves_below_the_decision_folder", () => {
  expect(
    checkState({
      ...world(decision({ id: "d-bbbbbb", attachments: ["run.log"] })),
      attachments: new Set(["lodge/attachments/d-bbbbbb/run.log"]),
    }).ok,
  ).toBe(true);
});
test.each(
  ["lodge/attachments/run.log", "lodge/attachments/d-cccccc/run.log", "d-bbbbbb/run.log"].map(
    (c) => [c],
  ),
)("check_2_listed_attachment_elsewhere_does_not_count %p", (held) => {
  expect(
    checkState({
      ...world(decision({ id: "d-bbbbbb", attachments: ["run.log"] })),
      attachments: new Set([held]),
    }).ok,
  ).toBe(false);
});
test.each(["replaces", "narrows", "confirms"].map((c) => [c]))(
  "check_2_decision_linking_to_itself %p",
  (field) => {
    expect(
      lines(world(decision({ id: "d-bbbbbb", decidedBy: "author", [field]: ["d-bbbbbb"] }))),
    ).toEqual([[2, `d-bbbbbb: ${field} itself`]]);
  },
);
test("check_3_author_decision_without_quote", () => {
  expect(lines(world(decision({ id: "d-bbbbbb", decidedBy: "author", quote: null })))).toEqual([
    [3, `d-bbbbbb: decided_by is author, but there is no quote${REMEDY_CHECK_3}`],
  ]);
});
test.each(["where", "when"].map((c) => [c]))("check_3_empty_where_or_when %p", (key) => {
  expect(
    lines(
      world(
        decision({
          id: "d-bbbbbb",
          decidedBy: "author",
          quote: { text: "Do it.", where: "a session", when: "2026-10-28 10:00", [key]: " " },
        }),
      ),
    ),
  ).toEqual([[3, `d-bbbbbb: quote.${key} is empty`]]);
});
test("check_3_imported_author_decision_needs_no_quote", () => {
  const d = decision({
    id: "d-bbbbbb",
    decidedBy: "author",
    importedFrom: { file: "n.md", heading: "H" },
  });
  expect(d.quote).toBeNull();
  expect(checkState(world(d)).ok).toBe(true);
});
test.each(["Author", "the author", " author", "author (relayed)", "AUTHOR"].map((c) => [c]))(
  "check_3_author_lookalike %p",
  (value) => {
    expect(lines(world(decision({ id: "d-bbbbbb", decidedBy: value, quote: null })))).toEqual([
      [
        3,
        `d-bbbbbb: decided_by is ${value}; write author exactly, with a quote, or use your own role`,
      ],
    ]);
  },
);
test("check_3_confirms_on_a_non_author_decision", () => {
  expect(
    lines(world(decision({ id: "d-bbbbbb", decidedBy: "coordinator", confirms: ["d-aaaaaa"] }))),
  ).toEqual([[3, "d-bbbbbb: confirms is for author decisions, but decided_by is coordinator"]]);
});
test("check_7_entry_missing_from_the_order", () => {
  const extra = entry({ id: "s-bbbbbb" });
  expect(lines(world(extra))).toEqual([
    [7, "s-bbbbbb: is not listed in the order of area storage"],
  ]);
  expect(checkState(world(extra)).problems[0]?.path).toBe(newRecordPath(extra));
});
test("check_7_order_lists_an_entry_that_is_not_there", () => {
  expect(lines(world(area({ order: [SPEC, "s-zzzzzz"] })))).toEqual([
    [7, "area storage: order lists s-zzzzzz, which is not a current entry of the area"],
  ]);
});
test("check_7_order_lists_an_entry_of_another_area", () => {
  const s = world(
    entry({ id: "s-bbbbbb", area: "other" }),
    area({ name: "other", order: ["s-bbbbbb"] }),
  );
  expect(
    lines({ ...s, areas: new Map([...s.areas, ["storage", area({ order: [SPEC, "s-bbbbbb"] })]]) }),
  ).toEqual([[7, "area storage: order lists s-bbbbbb, which is not a current entry of the area"]]);
});
test("check_7_order_lists_a_retired_entry", () => {
  const retire = decision({
    id: "d-bbbbbb",
    date: at(1),
    changes: [{ entry: SPEC, action: Action.RETIRE }],
  });
  expect(lines(world(retire))).toEqual([
    [7, "area storage: order lists s-aaaaaa, which is not a current entry of the area"],
  ]);
  expect(checkState(world(retire, area({ order: [] }))).ok).toBe(true);
});
test("check_7_order_lists_an_entry_twice", () => {
  expect(lines(world(area({ order: [SPEC, SPEC] })))).toEqual([
    [7, "area storage: order lists s-aaaaaa more than once"],
  ]);
});
test("check_7_folder_with_entries_has_no_area_file", () => {
  const s = snapshotOf([entry({ id: SPEC })]);
  expect(lines(s)).toEqual([[7, "area storage: has entries but no _area.md"]]);
  expect(checkState(s).problems[0]?.path).toBe("lodge/spec/storage/_area.md");
});
test("check_7_empty_area_needs_no_entries", () => {
  expect(checkState(snapshotOf([area()])).ok).toBe(true);
});
test("check_2_codes_use_unicode_casefold", () => {
  const s = world(
    decision({ id: "d-bbbbbb", code: "Straße" }),
    decision({ id: "d-cccccc", code: "STRASSE" }),
  );
  expect(lines(s)).toEqual([
    [2, "d-bbbbbb: code Straße is shared with another record, compared without regard to case"],
    [2, "d-cccccc: code STRASSE is shared with another record, compared without regard to case"],
  ]);
});
