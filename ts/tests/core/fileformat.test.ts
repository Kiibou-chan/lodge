import { expect, test } from "bun:test";
import { createHash } from "node:crypto";
import {
  Action,
  area,
  areaPath,
  contentHash,
  decision,
  newRecordPath,
  parseArea,
  parseRecord,
  Scope,
  slug,
  specEntry,
  writeArea,
  writeRecord,
} from "#core";
import { DECISION_PATH, document, EXAMPLE, EXAMPLE_TEXT, SPEC_PATH, TITLE } from "./samples.ts";

const FULL = decision({
  id: "d-3m8qk2",
  title: TITLE,
  scope: Scope.PROCESS,
  decidedBy: "author",
  date: "2026-10-28T23:48:10+01:00",
  statement: "One to three sentences.\n\nA second paragraph.",
  reasoning: "Why.\n\n- a list\n- of reasons",
  code: "ITEM-1",
  changes: [
    { entry: "s-4kq1zm", action: Action.CREATE },
    { entry: "s-0abcde", action: Action.RETIRE },
  ],
  replaces: ["d-8rw0te", "d-1abcde"],
  narrows: ["d-2abcde"],
  confirms: ["d-3abcde"],
  workItem: "docs/plans/ship.md",
  quote: { text: "Record it.", where: "first session", when: "2026-10-28 23:48" },
  numbers: [
    { value: "42", handle: "lodge show d-1abcde" },
    { value: "3.5 s", handle: "d-2abcde:time" },
  ],
  attachments: ["lodge/attachments/log.txt"],
  importedFrom: { file: "docs/old.md", heading: "ITEM-1" },
});

const REQUIRED = decision({
  id: "d-3m8qk2",
  title: "A title",
  scope: Scope.PRODUCT,
  decidedBy: "coordinator",
  date: "2026-10-28T23:48:10+01:00",
  statement: "A statement.",
});

const SPEC = specEntry({
  id: "s-4kq1zm",
  area: "storage",
  title: "Transcripts",
  statement: "They are kept.",
});

function parsed(path: string, text: string) {
  const result = parseRecord(path, text);
  if (result.kind === "problem") throw new Error(result.message);
  return result;
}

test.each([FULL, REQUIRED].map((c) => [c] as const))(
  "decision_round_trips_both_ways %p",
  (record) => {
    const text = writeRecord(record);
    expect(parsed(DECISION_PATH, text)).toEqual(record);
    expect(writeRecord(parsed(DECISION_PATH, text))).toEqual(text);
  },
);

test("written_text_matches_example", () => {
  expect(writeRecord(EXAMPLE)).toEqual(EXAMPLE_TEXT);
  expect(parsed(DECISION_PATH, EXAMPLE_TEXT)).toEqual(EXAMPLE);
});

test("written_text_of_every_field", () => {
  const lines = writeRecord(FULL).split("\n");
  expect(lines).toContain("  - {entry: s-0abcde, action: retire}");
  expect(lines).toContain("replaces: [d-8rw0te, d-1abcde]");
  expect(lines).toContain("narrows: [d-2abcde]");
  expect(lines).toContain("confirms: [d-3abcde]");
  expect(lines).toContain('work_item: "docs/plans/ship.md"');
  expect(lines).toContain('  - {value: "42", handle: "lodge show d-1abcde"}');
  expect(lines).toContain('attachments: ["lodge/attachments/log.txt"]');
  expect(lines).toContain('imported_from: {file: "docs/old.md", heading: "ITEM-1"}');
  const keys = lines
    .slice(1, lines.indexOf("---", 1))
    .filter((line) => line[0] !== " ")
    .map((line) => line.split(":")[0]);
  expect(keys).toEqual([
    ...["id", "kind", "code", "title", "scope", "decided_by", "date", "changes", "replaces"],
    ...["narrows", "confirms", "work_item", "quote", "numbers", "attachments", "imported_from"],
  ]);
});

const HOSTILE = [
  "No",
  "null",
  "a: b",
  "# x",
  '"',
  "\\",
  "- a",
  "{a}",
  "[a]",
  "a, b",
  "'q'",
  "\u00e9\ud83d\ude00",
  "&a *b",
];

test.each(HOSTILE.map((c) => [c] as const))("round_trip_survives_hostile_strings %p", (text) => {
  const record = decision({
    id: "d-3m8qk2",
    title: text,
    scope: Scope.PRODUCT,
    decidedBy: text,
    date: "2026-10-28T23:48:10+01:00",
    statement: "S.",
    workItem: text,
    quote: { text: text, where: text, when: text },
    numbers: [{ value: text, handle: text }],
    attachments: [text],
    importedFrom: { file: text, heading: text },
  });
  const written = writeRecord(record);
  expect(parsed(DECISION_PATH, written)).toEqual(record);
  expect(writeRecord(parsed(DECISION_PATH, written))).toEqual(written);
});

test("round_trip_survives_every_readable_character", () => {
  let every = "";
  for (let n = 0x20; n < 0xd800; n++)
    if (![0x7f, 0x2028, 0x2029].includes(n) && !(n >= 0x80 && n <= 0x9f))
      every += String.fromCodePoint(n);
  every += "😀�";
  const record = decision({
    id: "d-3m8qk2",
    title: every,
    scope: Scope.PRODUCT,
    decidedBy: "a",
    date: "2026-10-28T23:48:10+01:00",
    statement: "S.",
  });
  expect(parsed(DECISION_PATH, writeRecord(record))).toEqual(record);
});

test.each(["", "-a", ".a", "a b", "a:b", "a\n", "\u00e9"].map((c) => [c] as const))(
  "bad_code_is_problem_1 %p",
  (code) => {
    const header = [
      "id: d-3m8qk2",
      "kind: decision",
      `code: ${JSON.stringify(code)}`,
      'title: "T"',
      "scope: product",
    ];
    header.push(...["decided_by: coordinator", "date: 2026-10-28T23:48:10+01:00"]);
    const result = parseRecord(DECISION_PATH, document(header));
    expect(result.kind).toBe("problem");
    if (result.kind !== "problem") throw new Error("unexpected kind");
    expect(result.check).toEqual(1);
    expect(result.message).toContain("code");
  },
);

test.each(["\u0001", "\u007f", "\u0085", "\u2028", "\ufffe", "\t", "\n"].map((c) => [c] as const))(
  "control_character_is_problem_1 %p",
  (char) => {
    const forms = new Map([
      ["\u0001", "\\x01"],
      ["\u007f", "\\x7f"],
      ["\u0085", "\\x85"],
      ["\u2028", "\\u2028"],
      ["\ufffe", "\\ufffe"],
      ["\t", "\\t"],
      ["\n", "\\n"],
    ]);
    const escaped = `"a${forms.get(char)}b"`;
    const header = ["id: d-3m8qk2", "kind: decision", `title: ${escaped}`, "scope: product"];
    header.push(...["decided_by: coordinator", "date: 2026-10-28T23:48:10+01:00"]);
    const result = parseRecord(DECISION_PATH, document(header));
    expect(result.kind).toBe("problem");
    if (result.kind !== "problem") throw new Error("unexpected kind");
    expect(result.check).toEqual(1);
    expect(result.message).toContain("title");
  },
);

test("statement_with_a_lookalike_heading_is_kept", () => {
  const record = decision({
    id: "d-3m8qk2",
    title: "T",
    scope: Scope.PRODUCT,
    decidedBy: "x",
    date: "2026-10-28T23:48:10+01:00",
    statement: "A\n### Reasoning\n  ## Reasoning",
  });
  expect(parsed(DECISION_PATH, writeRecord(record))).toEqual(record);
});

test("crlf_text_parses_and_hashes_as_lf", () => {
  const crlf = EXAMPLE_TEXT.replaceAll("\n", "\r\n");
  expect(parsed(DECISION_PATH, crlf)).toEqual(EXAMPLE);
  expect(contentHash(crlf)).toEqual(contentHash(EXAMPLE_TEXT));
  const digest = createHash("sha256").update(EXAMPLE_TEXT).digest("hex");
  expect(contentHash(EXAMPLE_TEXT)).toEqual(digest.slice(0, 12));
  expect(contentHash("").length).toEqual(12);
});

test("hash_covers_undecodable_bytes", () => {
  expect(contentHash("a\udcffb")).toBe(
    createHash("sha256").update("a�b").digest("hex").slice(0, 12),
  );
});

test("spec_entry_takes_area_from_folder", () => {
  const text = writeRecord(SPEC);
  expect(text).toEqual(
    '---\nid: s-4kq1zm\nkind: spec\ntitle: "Transcripts"\n---\n\nThey are kept.\n',
  );
  expect(parsed(SPEC_PATH, text)).toEqual(SPEC);
  const other = parsed("lodge/spec/other-area/s-4kq1zm-x.md", text);
  expect(other.kind).toBe("spec");
  if (other.kind !== "spec") throw new Error("unexpected kind");
  expect(other.area).toEqual("other-area");
});

test("spec_entry_with_code_and_import_round_trips", () => {
  const entry = specEntry({
    id: "s-4kq1zm",
    area: "storage",
    title: "T",
    statement: "S.",
    code: "ITEM-1",
    importedFrom: { file: "a.md", heading: "H" },
  });
  const text = writeRecord(entry);
  expect(text.split("\n").slice(1, 6)).toEqual([
    "id: s-4kq1zm",
    "kind: spec",
    "code: ITEM-1",
    'title: "T"',
    'imported_from: {file: "a.md", heading: "H"}',
  ]);
  expect(parsed(SPEC_PATH, text)).toEqual(entry);
});

test("area_file_round_trips", () => {
  const value = area({
    name: "storage",
    title: "Storage",
    intro: "How records are kept.",
    order: ["s-4kq1zm", "s-0abcde"],
  });
  const text = writeArea(value);
  const header = '---\nkind: area\ntitle: "Storage"\norder: [s-4kq1zm, s-0abcde]\n---\n';
  expect(text).toEqual(`${header}\nHow records are kept.\n`);
  const path = areaPath("storage");
  expect(path).toEqual("lodge/spec/storage/_area.md");
  const back = parseArea(path, text);
  expect(back).toEqual(value);
  expect(back.kind).toBe("area");
  if (back.kind !== "area") throw new Error("unexpected kind");
  expect(writeArea(back)).toEqual(text);
});

test("area_without_entries_or_intro", () => {
  const value = area({ name: "storage", title: "Storage", intro: "", order: [] });
  const text = writeArea(value);
  expect(text).toEqual('---\nkind: area\ntitle: "Storage"\n---\n');
  expect(parseArea(areaPath("storage"), text)).toEqual(value);
});

test("paths_and_slugs", () => {
  expect(newRecordPath(EXAMPLE)).toEqual(
    "lodge/decisions/d-3m8qk2-whole-transcripts-are-kept-before-a.md",
  );
  expect(newRecordPath(SPEC)).toEqual("lodge/spec/storage/s-4kq1zm-transcripts.md");
  expect(slug("Whole transcripts, kept: before a session is archived!")).toEqual(
    "whole-transcripts-kept-before-a-session",
  );
  expect(slug("  \u00dcn\u00ef--code & 42 ")).toEqual("n-code-42");
  expect(slug("***")).toEqual("");
  const bare = decision({
    id: "d-3m8qk2",
    title: "***",
    scope: Scope.PRODUCT,
    decidedBy: "x",
    date: "2026-10-28T23:48:10+01:00",
    statement: "S.",
  });
  expect(newRecordPath(bare)).toEqual("lodge/decisions/d-3m8qk2.md");
});
