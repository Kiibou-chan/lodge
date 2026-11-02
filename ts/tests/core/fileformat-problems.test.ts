import { expect, test } from "bun:test";
import { parseArea, parseRecord } from "#core";
import { BASE_HEADER, DECISION_PATH, document, replaced, SPEC_PATH } from "./samples.ts";

function problem(text: string, path: string = DECISION_PATH) {
  const result = parseRecord(path, text);
  expect(result.kind).toBe("problem");
  if (result.kind !== "problem") throw new Error("expected problem");
  expect(result.check).toEqual(1);
  expect(result.path).toEqual(path);
  return result;
}

test("missing_fence", () => {
  expect(problem("title: x\n\nBody.\n").message).toContain("---");
  expect(problem("---\ntitle: x\n\nBody.\n").message).toContain("closed");
  expect(problem("").message).toContain("---");
});

test("bad_yaml_with_line", () => {
  const found = problem(document(replaced("title", "title: a: b")));
  expect(found.line).toEqual(7);
  expect(found.message).toContain("YAML");
});

test("header_that_is_not_a_mapping", () => {
  expect(problem(document(["- a", "- b"])).message).toContain("mapping");
  expect(problem(document([])).message).toContain("mapping");
});

test("unknown_key_named", () => {
  const found = problem(document([...BASE_HEADER, "replace: [d-8rw0te]"]));
  expect(found.message).toContain("replace");
  expect(found.line).toEqual(8);
});

test("unknown_kind", () => {
  expect(problem(document(replaced("kind", "kind: note"))).message).toContain("kind");
  expect(problem(document(replaced("kind", null))).message).toContain("kind");
});

test.each(["id", "title", "scope", "decided_by", "date"].map((c) => [c] as const))(
  "missing_required_field %p",
  (key) => {
    const found = problem(document(replaced(key, null)));
    expect(found.message).toContain(key);
    expect(found.message).toContain("missing");
  },
);

test("empty_statement_is_missing", () => {
  expect(problem(document(BASE_HEADER, "")).message).toContain("statement");
  expect(problem(document(BASE_HEADER, "## Reasoning\n\nWhy.")).message).toContain("statement");
});

test("empty_title_is_missing", () => {
  expect(problem(document(replaced("title", 'title: ""'))).message).toContain("title");
});

test.each([
  [["scope: private"], "scope"],
  [["changes:", "  - {entry: s-4kq1zm, action: rewrite}"], "action"],
  [["changes:", "  - {entry: s-4kq1zm}"], "action"],
  [["changes:", "  - {entry: s-4kq1zm, action: edit, why: x}"], "why"],
  [["changes: s-4kq1zm"], "changes"],
  [["changes:", "  - s-4kq1zm"], "changes"],
] as const)("bad_scope_or_action %p %p", (extra, word) => {
  const header = extra[0]?.startsWith("scope") ? replaced("scope", null) : BASE_HEADER;
  expect(problem(document([...header, ...extra])).message).toContain(word);
});

test.each(
  ["title: [a, b]", "title: {a: b}", "decided_by: [a]", "date: [2026-10-28T23:48:10+01:00]"].map(
    (c) => [c] as const,
  ),
)("non_string_where_string_expected %p", (line) => {
  const key = line.split(":")[0]!;
  const found = problem(document(replaced(key, line)));
  expect(found.message).toContain(key);
});

test.each(
  [
    "replaces: d-8rw0te",
    "replaces: [{a: b}]",
    "replaces: [s-4kq1zm]",
    "narrows: [d-8rw0tI]",
    "confirms: [x]",
    "attachments: log.txt",
    "quote: Record it.",
    'quote: {text: "x", where: "y"}',
    'quote: {text: "x", where: "y", when: "z", by: "w"}',
    "numbers: [1]",
    'numbers: [{value: "1"}]',
    "imported_from: a.md",
    'imported_from: {file: "a.md"}',
    "work_item: [a]",
    "code: [a]",
  ].map((c) => [c] as const),
)("wrong_shapes_name_their_key %p", (line) => {
  const found = problem(document([...BASE_HEADER, line]));
  expect(found.message).toContain(line.split(":")[0] ?? "");
});

test("bad_id_shapes", () => {
  expect(problem(document(replaced("id", "id: d-3m8qkI"))).message).toContain("id");
  expect(problem(document(replaced("id", "id: s-3m8qk2"))).message).toContain("id");
});

test("change_entry_must_be_a_specification_id", () => {
  const found = problem(
    document([...BASE_HEADER, "changes:", "  - {entry: d-8rw0te, action: edit}"]),
  );
  expect(found.message).toContain("changes");
});

test.each(
  [
    "2026-10-28T23:48:10",
    "2026-10-28 23:48:10+01:00",
    "2026-10-28T23:48+01:00",
    "2026-10-28T23:48:10Z",
  ].map((c) => [c] as const),
)("date_without_offset %p", (date) => {
  const found = problem(document(replaced("date", `date: ${date}`)));
  expect(found.message).toContain("date");
  expect(found.message).toContain("offset");
});

test("date_that_is_not_a_date", () => {
  expect(problem(document(replaced("date", "date: 2026-13-28T23:48:10+01:00"))).message).toContain(
    "date",
  );
});

test("date_only_without_import", () => {
  const found = problem(document(replaced("date", "date: 2026-10-28")));
  expect(found.message).toContain("imported_from");
});

test("imported_date_only_normalised", () => {
  const header = [
    ...replaced("date", "date: 2026-10-28"),
    'imported_from: {file: "a.md", heading: "H"}',
  ];
  const result = parseRecord(DECISION_PATH, document(header));
  expect(result.kind).toBe("decision");
  if (result.kind !== "decision") throw new Error("unexpected kind");
  expect(result.date).toEqual("2026-10-28T00:00:00+00:00");
  expect(
    problem(document([...replaced("date", "date: 2026-13-45"), header.at(-1)!])).message,
  ).toContain("2026-13-45");
});

test("duplicate_key", () => {
  const found = problem(document([...BASE_HEADER, 'title: "Again"']));
  expect(found.message).toContain("title");
  expect(found.line).toEqual(8);
});

test("spec_entry_outside_an_area_folder", () => {
  const text = '---\nid: s-4kq1zm\nkind: spec\ntitle: "T"\n---\n\nS.\n';
  expect(problem(text, "s-4kq1zm-t.md").message).toContain("area");
  expect(problem(text, "lodge/spec/Bad Name/s-4kq1zm-t.md").message).toContain("area");
});

test("spec_entry_rejects_decision_keys_and_reasoning", () => {
  let header = ["id: s-4kq1zm", "kind: spec", 'title: "T"', "scope: product"];
  expect(problem(document(header), SPEC_PATH).message).toContain("scope");
  header = ["id: s-4kq1zm", "kind: spec", 'title: "T"'];
  expect(problem(document(header, "S.\n\n## Reasoning\n\nWhy."), SPEC_PATH).message).toContain(
    "Reasoning",
  );
  const result = parseRecord(SPEC_PATH, document(header));
  expect(result.kind).toBe("spec");
  if (result.kind !== "spec") throw new Error("unexpected kind");
});

test("bad_utf8_is_problem_1", () => {
  const raw = document(BASE_HEADER, "A \udcff statement.");
  expect(problem(raw).message).toContain("UTF-8");
});

test("area_problems", () => {
  const path = "lodge/spec/storage/_area.md";
  for (const text of [
    "no fence",
    document(["kind: area"]),
    document(["kind: spec", 'title: "T"']),
    document(["kind: area", 'title: "T"', "order: s-4kq1zm"]),
    document(["kind: area", 'title: "T"', "order: [d-8rw0te]"]),
    document(["kind: area", 'title: "T"', "name: x"]),
  ]) {
    const result = parseArea(path, text);
    expect(result.kind).toBe("problem");
    if (result.kind !== "problem") throw new Error("unexpected kind");
    expect(result.check).toEqual(1);
  }
  expect(parseArea("_area.md", document(["kind: area", 'title: "T"'])).kind === "problem").toBe(
    true,
  );
});
