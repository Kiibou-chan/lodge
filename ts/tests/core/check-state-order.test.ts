import { expect, test } from "bun:test";
import { checkResult, checkState, problem } from "#core";
import { area, decision, entry, snapshotOf } from "./builders.ts";

test("check_result_computes_ok_from_problems", () => {
  const problems = [problem({ path: "lodge/x.md", check: 2, message: "x" })];
  const notes = ["already published"];
  expect(checkResult(problems, notes)).toEqual({ problems, notes, ok: false });
  expect(checkResult([], notes)).toEqual({ problems: [], notes, ok: true });
});
test("problems_sort_by_path_check_and_message_and_deduplicate_links", () => {
  const d = decision({ id: "d-aaaaaa", attachments: ["missing.txt", "missing.txt"] });
  const e = entry({ id: "s-aaaaaa", restsOn: ["s-zzzzzz", "s-zzzzzz"] });
  const dp = "lodge/decisions/d-aaaaaa.md";
  const ep = "lodge/spec/storage/s-aaaaaa.md";
  const before = [
    problem({ path: ep, check: 3, message: "z" }),
    problem({ path: dp, check: 3, message: "z" }),
    problem({ path: dp, check: 1, message: "𝔘" }),
    problem({ path: dp, check: 1, message: "\uE000" }),
    problem({ path: "lodge/𝔘.md", check: 1, message: "x" }),
    problem({ path: "lodge/\uE000.md", check: 1, message: "x" }),
  ] as const;
  const s = snapshotOf([area({ order: [e.id] }), e, d], {
    paths: new Map([
      [d.id, dp],
      [e.id, ep],
    ]),
    problems: before,
  });
  expect(checkState(s).problems).toEqual([
    before[3],
    before[2],
    problem({
      path: dp,
      check: 2,
      message:
        "d-aaaaaa: lists attachment missing.txt, which does not exist; pass the file with --attach",
    }),
    before[1],
    problem({ path: ep, check: 2, message: "s-aaaaaa: rests_on s-zzzzzz, which does not exist" }),
    before[0],
    before[5],
    before[4],
  ]);
});
