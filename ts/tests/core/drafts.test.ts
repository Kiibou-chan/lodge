import { expect, test } from "bun:test";
import { area, type Draft, decision, parseDraft, recordFromDraft, Scope, specEntry } from "#core";
import { document } from "./samples.ts";

const DECISION_DRAFT = document(
  ["kind: decision", 'title: "Keep transcripts"', "scope: process", "decided_by: coordinator"],
  "They are kept.\n\n## Reasoning\n\nBecause.",
);
const SPEC_DRAFT = document(
  ["kind: spec", "area: storage", 'title: "Transcripts"', "base: 0123456789ab"],
  "They are kept.",
);
const AREA_DRAFT = document(
  ["kind: area", "name: storage", 'title: "Storage"', "order: [s-4kq1zm]"],
  "Intro.",
);
const DATE = "2026-10-29T09:30:00+01:00";
function drafted(text: string): Draft {
  const result = parseDraft("draft.md", text);
  expect(result.kind).not.toBe("problem");
  if (result.kind === "problem") throw new Error(result.message);
  return result;
}
test("draft_without_id_or_date", () => {
  const draft = drafted(DECISION_DRAFT);
  expect(draft.kind).toBe("decision");
  expect(draft.source).toBe("draft.md");
  expect(draft.header.has("id")).toBe(false);
  expect(draft.header.has("date")).toBe(false);
});
test("draft_keeps_header_and_body", () => {
  const draft = drafted(DECISION_DRAFT);
  expect(draft.header).toEqual(
    new Map(
      Object.entries({
        kind: "decision",
        title: "Keep transcripts",
        scope: "process",
        decided_by: "coordinator",
      }),
    ),
  );
  expect(draft.body).toBe("They are kept.\n\n## Reasoning\n\nBecause.");
});
test("record_from_draft_fills_id_date_area", () => {
  expect(recordFromDraft(drafted(DECISION_DRAFT), "d-3m8qk2", DATE, null)).toEqual(
    decision({
      id: "d-3m8qk2",
      title: "Keep transcripts",
      scope: Scope.PROCESS,
      decidedBy: "coordinator",
      date: DATE,
      statement: "They are kept.",
      reasoning: "Because.",
    }),
  );
  expect(recordFromDraft(drafted(SPEC_DRAFT), "s-4kq1zm", null, null)).toEqual(
    specEntry({
      id: "s-4kq1zm",
      area: "storage",
      title: "Transcripts",
      statement: "They are kept.",
    }),
  );
});
test("existing_entry_takes_its_area_from_the_caller", () => {
  const text = document(
    ["kind: spec", 'title: "Transcripts"', "base: 0123456789ab"],
    "They are kept.",
  );
  expect(recordFromDraft(drafted(text), "s-4kq1zm", null, "storage")).toEqual(
    specEntry({
      id: "s-4kq1zm",
      area: "storage",
      title: "Transcripts",
      statement: "They are kept.",
    }),
  );
  const moved = recordFromDraft(drafted(SPEC_DRAFT), "s-4kq1zm", null, "process");
  expect(moved.kind).toBe("problem");
  if (moved.kind === "problem") expect(moved.message).toContain("area");
});
test("draft_carries_base_and_area", () => {
  const draft = drafted(SPEC_DRAFT);
  expect(draft.header.get("base")).toBe("0123456789ab");
  expect(draft.header.get("area")).toBe("storage");
  expect(draft.kind).toBe("spec");
});
test("area_draft", () => {
  const draft = drafted(AREA_DRAFT);
  expect(draft.kind).toBe("area");
  expect(draft.header.get("name")).toBe("storage");
  expect(recordFromDraft(draft, "", null, null)).toEqual(
    area({ name: "storage", title: "Storage", intro: "Intro.", order: ["s-4kq1zm"] }),
  );
  const named = document(["kind: area", 'title: "Storage"'], "");
  expect(recordFromDraft(drafted(named), "", null, "storage")).toEqual(
    area({ name: "storage", title: "Storage", intro: "", order: [] }),
  );
  expect(recordFromDraft(drafted(named), "", null, null).kind).toBe("problem");
});
test("draft_non_utf8_is_problem", () => {
  const result = parseDraft("draft.md", "---\nkind: spec\n---\n\nbad \udcff byte\n");
  expect(result.kind).toBe("problem");
  if (result.kind === "problem") {
    expect(result.path).toBe("draft.md");
    expect(result.check).toBe(1);
    expect(result.message).toContain("UTF-8");
  }
});
test.each([
  ["no fence", "---"],
  [document(['title: "T"']), "kind"],
  [document(["kind: note"]), "kind"],
  [document(["kind: decision", "replace: [d-8rw0te]"]), "replace"],
  [document(["kind: decision", "area: storage"]), "area"],
  [document(["kind: spec", "scope: product"]), "scope"],
  [document(["kind: area", "base: 0123456789ab", "order: []", "id: s-4kq1zm"]), "id"],
  [document(["kind: decision", "title: a: b"]), "YAML"],
])("draft_syntax_problems %p %p", (text, word) => {
  const result = parseDraft("draft.md", text);
  expect(result.kind).toBe("problem");
  if (result.kind === "problem") expect(result.message).toContain(word);
});
test("draft_may_not_set_a_date_unless_imported", () => {
  const header = [
    "kind: decision",
    'title: "T"',
    "scope: product",
    "decided_by: x",
    "date: 2026-10-01T00:00:00+00:00",
  ];
  const refused = recordFromDraft(drafted(document(header)), "d-3m8qk2", DATE, null);
  expect(refused.kind).toBe("problem");
  if (refused.kind === "problem") expect(refused.message).toContain("date");
  const kept = recordFromDraft(
    drafted(document([...header, 'imported_from: {file: "a.md", heading: "H"}'])),
    "d-3m8qk2",
    DATE,
    null,
  );
  expect(kept.kind).toBe("decision");
  if (kept.kind === "decision") expect(kept.date).toBe("2026-10-01T00:00:00+00:00");
  expect(recordFromDraft(drafted(document(header)), "d-3m8qk2", null, null).kind).toBe("decision");
});
test("draft_missing_a_required_field_is_a_problem", () => {
  const result = recordFromDraft(
    drafted(document(["kind: decision", 'title: "T"', "scope: product"])),
    "d-3m8qk2",
    DATE,
    null,
  );
  expect(result.kind).toBe("problem");
  if (result.kind === "problem") {
    expect(result.path).toBe("draft.md");
    expect(result.message).toContain("decided_by");
  }
  const noDate = recordFromDraft(drafted(DECISION_DRAFT), "d-3m8qk2", null, null);
  expect(noDate.kind).toBe("problem");
  if (noDate.kind === "problem") expect(noDate.message).toContain("date");
});
test("draft_id_must_match_the_given_one", () => {
  const text = document(["kind: spec", "id: s-4kq1zm", "area: storage", 'title: "T"']);
  expect(recordFromDraft(drafted(text), "s-4kq1zm", null, null).kind).toBe("spec");
  const other = recordFromDraft(drafted(text), "s-0abcde", null, null);
  expect(other.kind).toBe("problem");
  if (other.kind === "problem") expect(other.message).toContain("id");
});
test("spec_draft_without_an_area_is_a_problem", () => {
  const result = recordFromDraft(
    drafted(document(["kind: spec", 'title: "T"'])),
    "s-4kq1zm",
    null,
    null,
  );
  expect(result.kind).toBe("problem");
  if (result.kind === "problem") expect(result.message).toContain("area");
});
test("deep_nesting_in_a_draft_is_a_problem", () => {
  const result = parseDraft(
    "draft.md",
    document(["kind: decision", `work_item: ${"[".repeat(1000)}${"]".repeat(1000)}`]),
  );
  expect(result.kind).toBe("problem");
  if (result.kind === "problem") {
    expect(result.path).toBe("draft.md");
    expect(result.message).toContain("nested");
  }
});
test("problem_from_a_draft_carries_the_key_line", () => {
  const result = recordFromDraft(
    drafted(document(["kind: decision", "title: [a, b]", "scope: product", "decided_by: x"])),
    "d-3m8qk2",
    DATE,
    null,
  );
  expect(result.kind).toBe("problem");
  if (result.kind === "problem") expect(result.line).toBe(3);
  const found = recordFromDraft(
    drafted(document(["kind: spec", 'title: "T"', "area: Bad Area"])),
    "s-4kq1zm",
    null,
    null,
  );
  expect(found.kind).toBe("problem");
  if (found.kind === "problem") expect(found.line).toBe(4);
});
test("draft_keeps_the_indentation_of_its_first_line", () => {
  const text = document(["kind: spec", "area: storage", 'title: "T"'], "  indented first line");
  const entry = recordFromDraft(drafted(text), "s-4kq1zm", null, null);
  expect(entry.kind).toBe("spec");
  if (entry.kind === "spec") expect(entry.statement).toBe("  indented first line");
  expect(drafted(text).body).toBe("  indented first line");
});
test("draft_with_a_blank_title_is_a_problem", () => {
  const result = recordFromDraft(
    drafted(document(["kind: decision", 'title: " "', "scope: product", "decided_by: x"])),
    "d-3m8qk2",
    DATE,
    null,
  );
  expect(result.kind).toBe("problem");
  if (result.kind === "problem") expect(result.message).toContain("title");
});

test.each([
  ["[]", "[]"],
  ["{x: [a]}", "{'x': ['a']}"],
])("draft_non_string_id_is_reported %p %p", (value, representation) => {
  const result = recordFromDraft(
    drafted(document(["kind: spec", `id: ${value}`, "area: storage", 'title: "T"'])),
    "s-4kq1zm",
    null,
    null,
  );
  expect(result.kind).toBe("problem");
  if (result.kind === "problem")
    expect(result.message).toBe(
      `id ${representation} differs from the id 's-4kq1zm' lodge gave this draft`,
    );
});
