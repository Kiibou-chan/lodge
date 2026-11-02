import { expect, test } from "bun:test";
import { decision, Scope, specEntry, ValueError, writeRecord } from "#core";

test.each(["\u0001", "\u0085", "\n", "\u2028"].map((c) => [c] as const))(
  "write_refuses_control_characters %p",
  (char) => {
    expect(() => {
      writeRecord(
        decision({
          id: "d-3m8qk2",
          title: `a${char}b`,
          scope: Scope.PRODUCT,
          decidedBy: "x",
          date: "2026-10-28T23:48:10+01:00",
          statement: "S.",
        }),
      );
    }).toThrow(ValueError);
    expect(() => {
      writeRecord(
        decision({
          id: "d-3m8qk2",
          title: `a${char}b`,
          scope: Scope.PRODUCT,
          decidedBy: "x",
          date: "2026-10-28T23:48:10+01:00",
          statement: "S.",
        }),
      );
    }).toThrow(/title/u);
  },
);

test("write_refuses_reasoning_heading_in_statement", () => {
  const record = decision({
    id: "d-3m8qk2",
    title: "T",
    scope: Scope.PRODUCT,
    decidedBy: "x",
    date: "2026-10-28T23:48:10+01:00",
    statement: "A\n## Reasoning\nB",
  });
  expect(() => {
    writeRecord(record);
  }).toThrow(ValueError);
  expect(() => {
    writeRecord(record);
  }).toThrow(/Reasoning/u);
  const longer = specEntry({
    id: "s-4kq1zm",
    area: "storage",
    title: "T",
    statement: "A\n## Reasoning\nB",
  });
  expect(() => {
    writeRecord(longer);
  }).toThrow(ValueError);
  expect(() => {
    writeRecord(longer);
  }).toThrow(/Reasoning/u);
});

test("write_refuses_a_record_parse_would_not_read_back", () => {
  const bad = decision({
    id: "d-3m8qk2",
    title: "T",
    scope: Scope.PRODUCT,
    decidedBy: "x",
    date: "yesterday",
    statement: "S.",
  });
  expect(() => {
    writeRecord(bad);
  }).toThrow(ValueError);
  expect(() => {
    writeRecord(bad);
  }).toThrow(/date/u);
  expect(() => {
    writeRecord(
      decision({
        id: "d-3m8qk2",
        title: "T",
        scope: Scope.PRODUCT,
        decidedBy: "x",
        date: "2026-10-28T23:48:10+01:00",
        statement: "S.",
        code: "a b",
      }),
    );
  }).toThrow(ValueError);
  expect(() => {
    writeRecord(
      decision({
        id: "d-3m8qk2",
        title: "T",
        scope: Scope.PRODUCT,
        decidedBy: "x",
        date: "2026-10-28T23:48:10+01:00",
        statement: "S.",
        code: "a b",
      }),
    );
  }).toThrow(/code/u);
});
