import { expect, test } from "bun:test";
import { checkState, unrecordedProblems } from "#core";
import { snapshotOf, thread } from "./builders.ts";

test.each([false, true].map((c) => [c]))("thread_problems_are_visible_in_reads %p", (wrongName) => {
  const t = thread();
  const s = snapshotOf(
    [t],
    wrongName ? { paths: new Map([[t.id, "lodge/threads/wrong.md"]]) } : {},
  );
  const result = checkState(s);
  expect(result.problems.length).toBeGreaterThan(0);
  expect(unrecordedProblems(s, result)).toEqual(result.problems);
});
