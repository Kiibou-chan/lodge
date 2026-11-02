import { expect, test } from "bun:test";
import {
  type Decision,
  decision as makeDecision,
  newRecordPath,
  parseRecord,
  Scope,
  slug,
  ValueError,
  writeRecord,
} from "#core";
import { refused } from "./refused.ts";
import { BASE_HEADER, DECISION_PATH, document, replaced, SPEC_PATH } from "./samples.ts";

const STAMP = "2026-10-28T23:48:10+01:00";
function decision(fields: Partial<Decision> = {}): Decision {
  return makeDecision({
    id: "d-3m8qk2",
    title: "T",
    scope: Scope.PRODUCT,
    decidedBy: "x",
    date: STAMP,
    statement: "S.",
    ...fields,
  });
}
test("deep_nesting_is_problem_1", () => {
  const result = parseRecord(
    DECISION_PATH,
    document([...BASE_HEADER, `work_item: ${"[".repeat(1000)}${"]".repeat(1000)}`]),
  );
  expect(result.kind).toBe("problem");
  if (result.kind === "problem") {
    expect(result.check).toBe(1);
    expect(result.message).toContain("nested");
  }
});
test("indentation_of_the_first_line_is_kept", () => {
  const body = "    code first\n    more\n\n## Reasoning\n\n  - a\n  - b";
  const result = parseRecord(DECISION_PATH, document(BASE_HEADER, body));
  expect(result.kind).toBe("decision");
  if (result.kind === "decision") {
    expect(result.statement).toBe("    code first\n    more");
    expect(result.reasoning).toBe("  - a\n  - b");
    expect(writeRecord(result)).toBe(document(BASE_HEADER, body));
  }
  const spec = parseRecord(
    SPEC_PATH,
    document(["id: s-4kq1zm", "kind: spec", 'title: "T"'], "  x"),
  );
  expect(spec.kind).toBe("spec");
  if (spec.kind === "spec") expect(spec.statement).toBe("  x");
});
test("blank_lines_around_a_block_are_dropped", () => {
  const result = parseRecord(DECISION_PATH, document(BASE_HEADER, "\n \n  S.  \n\n"));
  expect(result.kind).toBe("decision");
  if (result.kind === "decision") expect(result.statement).toBe("  S.");
});
test.each(["title", "decided_by"].map((c) => [c] as const))(
  "blank_required_string_is_problem_1 %p",
  (key) => {
    const result = parseRecord(DECISION_PATH, document(replaced(key, `${key}: "   "`)));
    expect(result.kind).toBe("problem");
    if (result.kind === "problem") expect(result.message).toContain(key);
  },
);
test("quote_text_keeps_line_breaks_and_tabs", () => {
  const record = decision({
    quote: { text: "one\ntwo\r\n\tthree", where: "a session", when: "then" },
  });
  const text = writeRecord(record);
  expect(text).toContain('"one\\ntwo\\r\\n\\tthree"');
  expect(parseRecord(DECISION_PATH, text)).toEqual(record);
  expect(writeRecord(record)).toBe(text);
});
test.each(["where", "when"].map((c) => [c] as const))(
  "other_quote_parts_keep_the_control_character_ban %p",
  (field) => {
    const parts = { text: "t", where: "w", when: "n", [field]: "a\nb" };
    const run = () => writeRecord(decision({ quote: parts }));
    refused(run, ValueError, new RegExp(`quote.${field}`, "u"));
  },
);
test("quote_text_still_refuses_other_control_characters", () => {
  for (const text of ["a\x01b", "a\u2028b"]) {
    const run = () => writeRecord(decision({ quote: { text, where: "w", when: "n" } }));
    refused(run, ValueError, /quote\.text/u);
  }
});
test("json_dumps_default_escapes_read_back_as_emoji", () => {
  const quote = "Ship it 😀";
  const escaped = JSON.stringify(quote)
    .split("")
    .map((unit) =>
      unit.charCodeAt(0) > 127 ? `\\u${unit.charCodeAt(0).toString(16).padStart(4, "0")}` : unit,
    )
    .join("");
  expect(escaped).toContain("\\ud83d");
  const result = parseRecord(
    DECISION_PATH,
    document([...BASE_HEADER, `quote: {text: ${escaped}, where: "w", when: "n"}`]),
  );
  expect(result.kind).toBe("decision");
  if (result.kind === "decision")
    expect(result.quote).toEqual({ text: quote, where: "w", when: "n" });
});
test("lone_surrogate_escape_is_problem_1", () => {
  const result = parseRecord(DECISION_PATH, document(replaced("title", 'title: "a\\ud83d"')));
  expect(result.kind).toBe("problem");
  if (result.kind === "problem") expect(result.message).toContain("title");
});
test("write_names_the_field_that_would_read_back_differently", () => {
  for (const [record, field] of [
    [decision({ date: "2026-10-28", importedFrom: { file: "a.md", heading: "H" } }), "date"],
    [decision({ statement: "a\r\nb" }), "statement"],
    [decision({ statement: "a\n \n" }), "statement"],
  ] as const) {
    const run = () => writeRecord(record);
    refused(run, ValueError, new RegExp(field, "u"));
  }
});
test("slug_is_capped_at_a_word_boundary", () => {
  expect(slug("a".repeat(300))).toBe("a".repeat(60));
  expect(slug(Array(6).fill("abcdefghijklmno").join(" "))).toBe(
    Array(3).fill("abcdefghijklmno").join("-"),
  );
  expect(slug("one two three four five six seven")).toBe("one-two-three-four-five-six");
});
test("slug_cut_never_splits_a_word_unless_one_word_is_too_long", () => {
  expect(slug(`${"x".repeat(59)} yz`)).toBe("x".repeat(59));
  expect(slug(`${"x".repeat(57)} yz`)).toBe(`${"x".repeat(57)}-yz`);
  expect(slug(`${"x".repeat(58)} yz`)).toBe("x".repeat(58));
  expect(slug(`${"x".repeat(60)} yz`)).toBe("x".repeat(60));
  expect(slug(`${"x".repeat(61)} yz`)).toBe("x".repeat(60));
});
test("new_record_path_stays_short_for_long_titles", () => {
  expect(newRecordPath(decision({ title: "a".repeat(300) }))).toBe(
    `lodge/decisions/d-3m8qk2-${"a".repeat(60)}.md`,
  );
});
