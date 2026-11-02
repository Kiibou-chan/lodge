import { expect, test } from "bun:test";
import {
  checkState,
  derive,
  failingIds,
  level1,
  load,
  newRecordPath,
  tree,
  unrecordedProblems,
} from "#core";
import { area, decision, entry, filesOf } from "./builders.ts";

test("load_keeps_good_records_beside_problems", () => {
  const good = decision({ id: "d-aaaaaa" }),
    spec = entry({ id: "s-aaaaaa" }),
    boxed = area(),
    files = filesOf(good, spec, boxed),
    bad = "lodge/decisions/d-bbbbbb-broken.md";
  files.set(bad, "---\nid: d-bbbbbb\nkind: decision\n---\n\nNothing else.\n");
  const s = load(tree({ rev: "abc123", files }));
  expect(s.decisions).toEqual(new Map([["d-aaaaaa", good]]));
  expect(s.entries).toEqual(new Map([["s-aaaaaa", spec]]));
  expect(s.areas).toEqual(new Map([["storage", boxed]]));
  expect(s.paths).toEqual(
    new Map([
      ["d-aaaaaa", newRecordPath(good)],
      ["s-aaaaaa", newRecordPath(spec)],
    ]),
  );
  expect(s.problems.map((p) => [p.path, p.check])).toEqual([[bad, 1]]);
});
test("duplicate_id_is_problem_2_with_both_paths", () => {
  const first = decision({ id: "d-aaaaaa", title: "First" }),
    second = decision({ id: "d-aaaaaa", title: "Second" }),
    s = load(tree({ rev: "abc123", files: new Map([...filesOf(first), ...filesOf(second)]) })),
    kept = newRecordPath(first),
    dropped = newRecordPath(second);
  expect(s.decisions).toEqual(new Map([["d-aaaaaa", first]]));
  expect(s.paths).toEqual(new Map([["d-aaaaaa", kept]]));
  expect(s.problems.map((p) => [p.path, p.check]).sort()).toEqual(
    [
      [kept, 2],
      [dropped, 2],
    ].sort(),
  );
  expect(s.problems.every((p) => p.message.includes(kept) && p.message.includes(dropped))).toBe(
    true,
  );
});
test("stray_file_is_problem_1", () => {
  const files = new Map(
    [
      "lodge/notes.txt",
      "lodge/decisions/readme.txt",
      "lodge/spec/storage/deeper/s-aaaaaa-x.md",
      "lodge/decisions/.gitkeep",
      "lodge/spec/storage/.gitkeep",
      "lodge/attachments/log.txt",
      "README.md",
    ].map((p) => [p, "x"]),
  );
  expect(
    load(tree({ rev: "abc123", files }))
      .problems.map((p) => [p.path, p.check])
      .sort(),
  ).toEqual([
    ["lodge/decisions/readme.txt", 1],
    ["lodge/notes.txt", 1],
    ["lodge/spec/storage/deeper/s-aaaaaa-x.md", 1],
  ]);
});
test("record_in_the_wrong_folder_is_problem_1", () => {
  const e = entry({ id: "s-aaaaaa" }),
    path = "lodge/decisions/s-aaaaaa-an-entry.md",
    s = load(
      tree({ rev: "abc123", files: new Map([[path, filesOf(e).get(newRecordPath(e)) as string]]) }),
    );
  expect(s.entries).toEqual(new Map());
  expect(s.problems.map((p) => [p.path, p.check])).toEqual([[path, 1]]);
});
test("attachments_listed_not_parsed", () => {
  const files = filesOf(decision());
  files.set("lodge/attachments/other.log", "not a record");
  const s = load(
    tree({ rev: "abc123", files, attachments: new Set(["lodge/attachments/run.log"]) }),
  );
  expect(s.attachments).toEqual(
    new Set(["lodge/attachments/run.log", "lodge/attachments/other.log"]),
  );
  expect(s.problems).toEqual([]);
  expect(s.decisions.size).toBe(1);
});
test("duplicate_id_marks_kept_record_failing", () => {
  const first = decision({ id: "d-aaaaaa", title: "First", statement: "A holds." });
  const second = decision({ id: "d-aaaaaa", title: "Second", statement: "B holds." });
  const snap = load(
    tree({ rev: "abc123", files: new Map([...filesOf(first), ...filesOf(second)]) }),
  );
  const result = checkState(snap);
  expect(failingIds(snap, result)).toEqual(new Set(["d-aaaaaa"]));
  expect(unrecordedProblems(snap, result).map((p) => p.path)).toEqual([newRecordPath(second)]);
  expect(level1(snap, derive(snap), "d-aaaaaa", failingIds(snap, result)).flags).toContain(
    "fails check",
  );
});
