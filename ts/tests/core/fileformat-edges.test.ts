import { expect, test } from "bun:test";
import { Action, parseArea, parseRecord, ValueError, writeRecord } from "#core";
import { DECISION_PATH, document, EXAMPLE, replaced } from "./samples.ts";

for (const [name, statement] of [
  ["feff_after_reasoning_heading_round_trips", "A\n## Reasoning\ufeff\nB"],
  ["trailing_feff_round_trips", "S.\ufeff"],
  ["opening_feff_line_round_trips", "\ufeff\nS."],
] as const) {
  test(name, () => {
    const record = { ...EXAMPLE, statement };
    expect(parseRecord(DECISION_PATH, writeRecord(record))).toEqual(record);
  });
}
test("python_whitespace_title_is_empty", () => {
  const result = parseRecord(DECISION_PATH, document(replaced("title", 'title: "\\x1c"')));
  expect(result.kind).toBe("problem");
  if (result.kind !== "problem") throw new Error("expected problem");
  expect(result.message).toContain("non-empty");
});
test("rank_safe_integer_boundary", () => {
  const result = parseArea(
    "lodge/spec/storage/_area.md",
    document(["kind: area", "title: Storage", "rank: 9007199254740991"]),
  );
  expect(result.kind).toBe("area");
  if (result.kind !== "area") throw new Error("expected area");
  expect(result.rank).toBe(2 ** 53 - 1);
});
test.each(["12345678901234567890", "9007199254740992"])("unsafe_rank_is_problem %p", (rank) => {
  const result = parseArea(
    "lodge/spec/storage/_area.md",
    document(["kind: area", "title: Storage", `rank: ${rank}`]),
  );
  expect(result.kind).toBe("problem");
  if (result.kind !== "problem") throw new Error("expected problem");
  expect(result.message).toContain("rank");
  expect(result.line).toBe(4);
});
test("nested_change_read_back_repr", () => {
  expect(() =>
    writeRecord({ ...EXAMPLE, changes: [{ entry: "s-4kq1zm ", action: Action.EDIT }] }),
  ).toThrow(
    new ValueError(
      "the record would not read back unchanged: changes reads back as (Change(entry='s-4kq1zm', action=<Action.EDIT: 'edit'>),)",
    ),
  );
});
