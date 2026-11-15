import { expect, test } from "bun:test";
import { type Problem, parseArea, parseRecord, writeArea, writeRecord } from "#core";
import { area, entry } from "./builders.ts";

test("rests_on_round_trips", () => {
  const e = entry({ id: "s-aaaaaa", restsOn: ["s-bbbbbb", "s-cccccc"] }),
    text = writeRecord(e);
  expect(text).toContain('title: "An entry"\nrests_on: [s-bbbbbb, s-cccccc]');
  expect(parseRecord("lodge/spec/storage/a.md", text)).toEqual(e);
});
test("rank_round_trips", () => {
  const a = area({ rank: 0 });
  expect(writeArea(a)).toContain('title: "Storage"\nrank: 0');
  expect(parseArea("lodge/spec/storage/_area.md", writeArea(a))).toEqual(a);
});
test.each(["2", '"2"'].map((c) => [c]))("rank_reads_quoted_and_plain_alike %p", (value) =>
  expect(
    parseArea(
      "lodge/spec/storage/_area.md",
      `---\nkind: area\ntitle: Storage\nrank: ${value}\n---\n`,
    ),
  ).toEqual(area({ rank: 2 })),
);
test.each(["-1", "1.5", "true", "two", "01", '""'].map((c) => [c]))(
  "rank_must_be_a_whole_number %p",
  (value) => {
    const p = parseArea(
      "lodge/spec/storage/_area.md",
      `---\nkind: area\ntitle: Storage\nrank: ${value}\n---\n`,
    ) as Problem;
    expect(p.kind).toBe("problem");
    expect(p.check).toBe(1);
    expect(p.line).toBe(4);
    expect(p.message).toContain("rank");
    expect(p.message).not.toContain("unknown key");
  },
);
test("rests_on_holds_entry_ids_only", () => {
  const p = parseRecord(
    "lodge/spec/storage/a.md",
    "---\nid: s-aaaaaa\nkind: spec\ntitle: Entry\nrests_on: [d-3m8qk2]\n---\n\nHeld.\n",
  ) as Problem;
  expect(p.kind).toBe("problem");
  expect(p.check).toBe(1);
  expect(p.message).toContain("rests_on");
  expect(p.message).toContain("not a specification entry id");
});
test("area_without_rank_writes_as_before", () =>
  expect(writeArea(area())).toBe('---\nkind: area\ntitle: "Storage"\n---\n'));
