import { expect, test } from "bun:test";
import assert from "node:assert/strict";
import { contentHash, newRecordPath, parseRecord, Scope, ValueError } from "#core";
import {
  applied,
  apply,
  areaText,
  decisionText,
  isStale,
  present,
  problems,
  specText,
  state,
} from "./applying.ts";
import { decision, entry, area as makeArea } from "./builders.ts";

test("id_count_must_match_new_decisions", () => {
  const [s, tree] = state();
  expect(() => apply(s, tree, decisionText(), decisionText(), { ids: ["d-aaaaaa"] })).toThrow(
    ValueError,
  );
  expect(() => apply(s, tree, decisionText(), decisionText(), { ids: ["d-aaaaaa"] })).toThrow(
    /2 new decision drafts but 1 IDs/u,
  );
});

test("stale_base_is_problem_naming_both", () => {
  const old = entry({ id: "s-aaaaaa" });
  const [s, tree] = state(old, makeArea({ order: ["s-aaaaaa"] }));
  const actual = contentHash(present(tree.files.get(newRecordPath(old))));
  const found = problems(apply(s, tree, specText("id: s-aaaaaa", "base: 0123456789ab")));
  expect(found.length).toEqual(1);
  assert(isStale(present(found[0])));
  expect(found[0]?.path).toEqual("draft0.md");
  assert(found[0]?.message.includes("0123456789ab"));
  assert(found[0]?.message.includes(actual));
});

test("edit_without_base_is_problem", () => {
  const old = entry({ id: "s-aaaaaa" });
  const [s, tree] = state(old, makeArea({ order: ["s-aaaaaa"] }));
  const found = problems(apply(s, tree, specText("id: s-aaaaaa")));
  expect(found[0]?.path).toEqual("draft0.md");
  assert(found[0]?.message.includes("base"));
  assert(!isStale(present(found[0])));
});

test("import_needs_flag", () => {
  const [s, tree] = state();
  const text = decisionText("imported_from: {file: notes.md, heading: Old}", "date: 2026-01-02");
  const found = problems(apply(s, tree, text, { ids: ["d-aaaaaa"] }));
  expect(found.map((p) => p.path)).toEqual(["draft0.md"]);
  assert(found[0]?.message.includes("--import"));
  const result = applied(apply(s, tree, text, { ids: ["d-aaaaaa"], importing: true }));
  const d = parseRecord(
    "x",
    present(result.files.get("lodge/decisions/d-aaaaaa-keep-transcripts.md")),
  );
  assert(d.kind === "decision");
  expect(d.date).toEqual("2026-01-02T00:00:00+00:00");
});

test("imported_entry_needs_flag", () => {
  const [s, tree] = state(makeArea());
  const text = specText(
    "id: s-aaaaaa",
    "area: storage",
    "imported_from: {file: notes.md, heading: H}",
  );
  assert(problems(apply(s, tree, text))[0]?.message.includes("--import"));
});

test("date_in_new_draft_refused", () => {
  const [s, tree] = state();
  const found = problems(
    apply(s, tree, decisionText("date: 2026-10-29T10:00:00+01:00"), { ids: ["d-aaaaaa"] }),
  );
  expect(found.map((p) => p.path)).toEqual(["draft0.md"]);
  assert(found[0]?.message.includes("date"));
});

test("decision_with_unknown_id_refused", () => {
  const [s, tree] = state();
  const found = problems(apply(s, tree, decisionText("id: d-zzzzzz")));
  expect(found[0]?.path).toEqual("draft0.md");
  assert(found[0]?.message.includes("d-zzzzzz"));
});

test("entry_statement_with_reasoning_heading_refused", () => {
  const [s, tree] = state(makeArea());
  const found = problems(
    apply(
      s,
      tree,
      specText("id: s-aaaaaa", "area: storage", { body: "Text.\n\n## Reasoning\n\nWhy." }),
    ),
  );
  expect(found[0]?.path).toEqual("draft0.md");
  assert(found[0]?.message.includes("Reasoning"));
});

test("entry_without_area_refused", () => {
  const [s, tree] = state();
  const found = problems(apply(s, tree, specText("id: s-aaaaaa")));
  expect(found[0]?.path).toEqual("draft0.md");
  assert(found[0]?.message.includes("area"));
});

test("entry_without_id_refused", () => {
  const [s, tree] = state(makeArea());
  const found = problems(apply(s, tree, specText("area: storage")));
  expect(found[0]?.path).toEqual("draft0.md");
  assert(found[0]?.message.includes("lodge id s"));
});

test("entry_in_unknown_area_refused", () => {
  const [s, tree] = state();
  const found = problems(apply(s, tree, specText("id: s-aaaaaa", "area: storage")));
  expect(found[0]?.path).toEqual("draft0.md");
  assert(found[0]?.message.includes("storage"));
});

test("area_change_refused", () => {
  const old = entry({ id: "s-aaaaaa" });
  const [s, tree] = state(
    old,
    makeArea({ order: ["s-aaaaaa"] }),
    makeArea({ name: "other", title: "O" }),
  );
  const base = contentHash(present(tree.files.get(newRecordPath(old))));
  const found = problems(apply(s, tree, specText("id: s-aaaaaa", "area: other", `base: ${base}`)));
  expect(found[0]?.path).toEqual("draft0.md");
  assert(found[0]?.message.includes("storage"));
});

test("two_drafts_for_one_record_refused", () => {
  const [s, tree] = state(makeArea());
  const found = problems(
    apply(
      s,
      tree,
      specText("id: s-aaaaaa", "area: storage"),
      specText("id: s-aaaaaa", "area: storage"),
    ),
  );
  expect(found.map((p) => p.path)).toEqual(["draft1.md"]);
});

test("every_problem_names_its_draft", () => {
  const [s, tree] = state();
  const found = problems(apply(s, tree, specText("id: s-aaaaaa"), decisionText("id: d-zzzzzz")));
  expect(found.map((p) => p.path)).toEqual(["draft0.md", "draft1.md"]);
});

test("area_name_not_a_string_is_problem", () => {
  const [s, tree] = state();
  for (const value of ["[storage]", "{a: b}"]) {
    const found = problems(apply(s, tree, areaText(`name: ${value}`)));
    expect(found.map((p) => p.path)).toEqual(["draft0.md"]);
    assert(found[0]?.message.includes("name"));
  }
});

test("entry_created_and_retired_in_one_add_not_in_order", () => {
  const [s, tree] = state(makeArea());
  const result = applied(
    apply(
      s,
      tree,
      decisionText("changes:", "  - {entry: s-aaaaaa, action: retire}"),
      specText("id: s-aaaaaa", "area: storage"),
      { ids: ["d-bbbbbb"] },
    ),
  );
  assert(!result.files.has("lodge/spec/storage/_area.md"));
});

test("base_on_new_decision_refused", () => {
  const [s, tree] = state();
  const found = problems(apply(s, tree, decisionText("base: 0123456789ab"), { ids: ["d-aaaaaa"] }));
  expect(found[0]?.path).toEqual("draft0.md");
  expect(found[0]?.message).toEqual(
    "base is for edits, but this draft has no id and would add a new decision; keep the id that lodge draft printed to edit one",
  );
});

test("base_on_entry_that_does_not_exist_refused", () => {
  const [s, tree] = state(makeArea());
  const found = problems(
    apply(s, tree, specText("id: s-aaaaaa", "area: storage", "base: 0123456789ab")),
  );
  expect(found[0]?.message).toEqual("base is for edits, but no entry s-aaaaaa exists to edit");
});

test("base_on_new_area_refused", () => {
  const [s, tree] = state();
  const found = problems(apply(s, tree, areaText("name: storage", "base: 0123456789ab")));
  expect(found[0]?.message).toEqual("base is for edits, but no area storage exists to edit");
});

test("stale_base_message_says_to_redo_the_change", () => {
  const old = entry({ id: "s-aaaaaa" });
  const [s, tree] = state(old, makeArea({ order: ["s-aaaaaa"] }));
  const actual = contentHash(present(tree.files.get(newRecordPath(old))));
  const found = problems(apply(s, tree, specText("id: s-aaaaaa", "base: 0123456789ab")));
  expect(found[0]?.message).toEqual(
    `the base 0123456789ab differs from ${actual}, the hash of ${newRecordPath(old)} now; it changed since the draft was made, so print it again with lodge draft s-aaaaaa, make the change on that print, and add it`,
  );
});

test("edit_changing_imported_from_has_its_own_message", () => {
  const old = entry({ id: "s-aaaaaa", importedFrom: { file: "notes.md", heading: "H" } });
  const [s, tree] = state(old, makeArea({ order: ["s-aaaaaa"] }));
  const base = contentHash(present(tree.files.get(newRecordPath(old))));
  for (const line of ["imported_from: {file: other.md, heading: H}", null]) {
    const header = ["id: s-aaaaaa", `base: ${base}`, ...(line ? [line] : [])] as const;
    const found = problems(apply(s, tree, specText(...header)));
    expect(found[0]?.message).toEqual(
      "this draft changes imported_from of s-aaaaaa; keep it as lodge draft printed it",
    );
  }
});

test("edit_of_decision_changing_imported_from_has_its_own_message", () => {
  const old = decision({ id: "d-aaaaaa", title: "Keep transcripts", scope: Scope.PROCESS });
  const [s, tree] = state(old);
  const base = contentHash(present(tree.files.get(newRecordPath(old))));
  const text = decisionText(
    "id: d-aaaaaa",
    `date: ${old.date}`,
    `base: ${base}`,
    "imported_from: {file: a.md, heading: H}",
  );
  const found = problems(apply(s, tree, text));
  expect(found[0]?.message).toEqual(
    "this draft changes imported_from of d-aaaaaa; keep it as lodge draft printed it",
  );
});

test("id_of_the_wrong_shape_says_so", () => {
  const [s, tree] = state(makeArea(), entry({ id: "s-bbbbbb" }));
  const entryIds = "a specification entry ID; ";
  const decisionIds = "a decision ID; ";
  const cases = [
    [specText("id: S-BBBBBB", "base: 0123456789ab"), "'S-BBBBBB'", entryIds],
    [specText("id: d-aaaaaa", "area: storage"), "'d-aaaaaa'", entryIds],
    [specText("id: s-bbbbbi", "area: storage"), "'s-bbbbbi'", entryIds],
    [decisionText("id:"), "''", decisionIds],
    [decisionText("id: D-AAAAAA"), "'D-AAAAAA'", decisionIds],
    [decisionText("id: s-bbbbbb"), "'s-bbbbbb'", decisionIds],
  ] as const;
  const expected = [
    "IDs are lower case, like s-4kq1zm",
    "an entry ID starts with s-, like s-4kq1zm",
    "an ID is s- and six characters from 0-9 and a-z without i, l, o, and u, like s-4kq1zm",
    "an ID is d- and six characters from 0-9 and a-z without i, l, o, and u, like d-3m8qk2",
    "IDs are lower case, like d-3m8qk2",
    "a decision ID starts with d-, like d-3m8qk2",
  ] as const;
  for (const [index, [text, given, kind]] of cases.entries()) {
    const rest = present(expected[index]);
    const found = problems(apply(s, tree, text));
    expect(found[0]?.message).toEqual(`id ${given} is not ${kind}${rest}`);
  }
});

test("area_of_the_wrong_shape_says_so", () => {
  const [s, tree] = state(makeArea());
  const found = problems(apply(s, tree, specText("id: s-aaaaaa", "area: [storage]")));
  expect(found[0]?.message).toEqual("area must be one name, not ['storage']");
});

test("existing_entry_area_problem_uses_python_value_text", () => {
  const [s, tree] = state(entry({ id: "s-aaaaaa" }), makeArea());
  const found = problems(apply(s, tree, specText("id: s-aaaaaa", "area: [storage]")));
  expect(found[0]?.message).toBe(
    "area ['storage'] differs from storage; entries do not move areas",
  );
});

test("stale_base_problem_uses_python_value_text", () => {
  const old = entry({ id: "s-aaaaaa" });
  const [s, tree] = state(old, makeArea());
  const found = problems(apply(s, tree, specText("id: s-aaaaaa", "base: {x: [a]}")));
  expect(found[0]?.message).toContain("the base {'x': ['a']} differs from");
});
