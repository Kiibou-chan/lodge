import { expect, test } from "bun:test";
import assert from "node:assert/strict";
import {
  Action,
  contentHash,
  area as makeCoreArea,
  newRecordPath,
  parseArea,
  parseRecord,
} from "#core";
import {
  applied,
  apply,
  areaText,
  decisionText,
  NOW,
  present,
  problems,
  specText,
  state,
} from "./applying.ts";
import { at, decision, entry, area as makeArea } from "./builders.ts";

test("new_decision_and_entry_and_area", () => {
  // After the checking lane merges, also assert checkChange accepts the written tree.
  const [s, tree] = state();
  const result = applied(
    apply(
      s,
      tree,
      decisionText("changes:", "  - {entry: s-aaaaaa, action: create}"),
      specText("id: s-aaaaaa", "area: storage"),
      areaText("name: storage"),
      { ids: ["d-bbbbbb"] },
    ),
  );
  expect(result.ids).toEqual(["d-bbbbbb", "s-aaaaaa"]);
  expect([...result.files.keys()].sort()).toEqual([
    "lodge/decisions/d-bbbbbb-keep-transcripts.md",
    "lodge/spec/storage/_area.md",
    "lodge/spec/storage/s-aaaaaa-transcripts.md",
  ]);
  const d = parseRecord(
    "x",
    present(result.files.get("lodge/decisions/d-bbbbbb-keep-transcripts.md")),
  );
  assert(d.kind === "decision");
  expect([d.id, d.date]).toEqual(["d-bbbbbb", NOW]);
  const area = parseArea(
    "lodge/spec/storage/_area.md",
    present(result.files.get("lodge/spec/storage/_area.md")),
  );
  expect(area).toEqual(
    makeCoreArea({ name: "storage", title: "Storage", intro: "Intro.", order: ["s-aaaaaa"] }),
  );
});

test("new_entry_appended_to_existing_area_order", () => {
  const old = entry({ id: "s-aaaaaa", title: "Old" });
  const [s, tree] = state(old, makeArea({ order: ["s-aaaaaa"] }));
  const result = applied(
    apply(
      s,
      tree,
      decisionText("changes:", "  - {entry: s-cccccc, action: create}"),
      specText("id: s-cccccc", "area: storage"),
      { ids: ["d-bbbbbb"] },
    ),
  );
  const area = parseArea(
    "lodge/spec/storage/_area.md",
    present(result.files.get("lodge/spec/storage/_area.md")),
  );
  assert(area.kind === "area");
  expect(area.order).toEqual(["s-aaaaaa", "s-cccccc"]);
  expect(area.title).toEqual("Storage");
});

test("area_draft_already_listing_entry_not_doubled", () => {
  const [s, tree] = state();
  const result = applied(
    apply(
      s,
      tree,
      specText("id: s-aaaaaa", "area: storage"),
      areaText("name: storage", "order: [s-aaaaaa]"),
    ),
  );
  const area = parseArea(
    "lodge/spec/storage/_area.md",
    present(result.files.get("lodge/spec/storage/_area.md")),
  );
  assert(area.kind === "area");
  expect(area.order).toEqual(["s-aaaaaa"]);
});

test("new_ids_ascend_in_draft_order", () => {
  const [s, tree] = state();
  const result = applied(
    apply(
      s,
      tree,
      decisionText(),
      decisionText({ body: "Second." }),
      decisionText({ body: "Third." }),
      { ids: ["d-cccccc", "d-aaaaaa", "d-bbbbbb"] },
    ),
  );
  expect(result.ids).toEqual(["d-aaaaaa", "d-bbbbbb", "d-cccccc"]);
});

test("edit_keeps_path_even_if_title_changes", () => {
  const old = entry({ id: "s-aaaaaa", title: "Old title", statement: "Old." });
  const [s, tree] = state(old, makeArea({ order: ["s-aaaaaa"] }));
  const base = contentHash(present(tree.files.get(newRecordPath(old))));
  const result = applied(
    apply(s, tree, specText("id: s-aaaaaa", `base: ${base}`, { body: "New." })),
  );
  expect([...result.files.keys()]).toEqual([newRecordPath(old)]);
  const writtenEntry = parseRecord(
    newRecordPath(old),
    present(result.files.get(newRecordPath(old))),
  );
  assert(writtenEntry.kind === "spec");
  expect(writtenEntry.statement).toEqual("New.");
  expect(writtenEntry.title).toEqual("Transcripts");
  expect(writtenEntry.area).toEqual("storage");
  expect(result.ids).toEqual(["s-aaaaaa"]);
});

test("retire_removes_from_order", () => {
  // After the checking lane merges, also assert checkChange accepts the written tree.
  const [a, b] = [
    entry({ id: "s-aaaaaa", title: "A" }),
    entry({ id: "s-bbbbbb", title: "B" }),
  ] as const;
  const [s, tree] = state(a, b, makeArea({ order: ["s-aaaaaa", "s-bbbbbb"] }));
  const result = applied(
    apply(s, tree, decisionText("changes:", "  - {entry: s-aaaaaa, action: retire}"), {
      ids: ["d-cccccc"],
    }),
  );
  const area = parseArea(
    "lodge/spec/storage/_area.md",
    present(result.files.get("lodge/spec/storage/_area.md")),
  );
  assert(area.kind === "area");
  expect(area.order).toEqual(["s-bbbbbb"]);
  assert(!result.files.has(newRecordPath(a)));
});

test("replacing_retirement_restores_order", () => {
  // After the checking lane merges, also assert checkChange accepts the written tree.
  const [a, b] = [
    entry({ id: "s-aaaaaa", title: "A" }),
    entry({ id: "s-bbbbbb", title: "B" }),
  ] as const;
  const retire = decision({
    id: "d-cccccc",
    date: at(2),
    changes: [{ entry: "s-aaaaaa", action: Action.RETIRE }],
  });
  const [s, tree] = state(a, b, retire, makeArea({ order: ["s-bbbbbb"] }));
  const result = applied(
    apply(s, tree, decisionText("replaces: [d-cccccc]"), { ids: ["d-dddddd"] }),
  );
  const area = parseArea(
    "lodge/spec/storage/_area.md",
    present(result.files.get("lodge/spec/storage/_area.md")),
  );
  assert(area.kind === "area");
  expect(area.order).toEqual(["s-bbbbbb", "s-aaaaaa"]);
});

test("replacing_one_of_two_retirements_leaves_the_order", () => {
  const a = entry({ id: "s-aaaaaa", title: "A" });
  const changes = [{ entry: "s-aaaaaa", action: Action.RETIRE }] as const;
  const first = decision({ id: "d-cccccc", date: at(2), changes: changes });
  const second = decision({ id: "d-dddddd", date: at(3), changes: changes });
  const [s, tree] = state(a, first, second, makeArea({ order: [] }));
  const result = applied(
    apply(s, tree, decisionText("replaces: [d-cccccc]"), { ids: ["d-eeeeee"] }),
  );
  expect([...result.files.keys()]).toEqual(["lodge/decisions/d-eeeeee-keep-transcripts.md"]);
});

test("untouched_area_not_written", () => {
  const [s, tree] = state(makeArea(), makeArea({ name: "other", title: "Other" }));
  const result = applied(apply(s, tree, decisionText(), { ids: ["d-aaaaaa"] }));
  expect([...result.files.keys()]).toEqual(["lodge/decisions/d-aaaaaa-keep-transcripts.md"]);
});

test("import_without_date_gets_the_add_date", () => {
  const [s, tree] = state();
  const text = decisionText("imported_from: {file: notes.md, heading: Old}");
  const result = applied(apply(s, tree, text, { ids: ["d-aaaaaa"], importing: true }));
  const d = parseRecord(
    "x",
    present(result.files.get("lodge/decisions/d-aaaaaa-keep-transcripts.md")),
  );
  assert(d.kind === "decision");
  expect(d.date).toEqual(NOW);
});

test("edit_of_imported_entry_keeping_its_origin_needs_no_flag", () => {
  const old = entry({ id: "s-aaaaaa", importedFrom: { file: "notes.md", heading: "H" } });
  const [s, tree] = state(old, makeArea({ order: ["s-aaaaaa"] }));
  const base = contentHash(present(tree.files.get(newRecordPath(old))));
  const text = specText(
    "id: s-aaaaaa",
    `base: ${base}`,
    "imported_from: {file: notes.md, heading: H}",
  );
  expect(applied(apply(s, tree, text)).ids).toEqual(["s-aaaaaa"]);
  const moved = specText(
    "id: s-aaaaaa",
    `base: ${base}`,
    "imported_from: {file: other.md, heading: H}",
  );
  assert(problems(apply(s, tree, moved))[0]?.message.includes("changes imported_from of s-aaaaaa"));
});
