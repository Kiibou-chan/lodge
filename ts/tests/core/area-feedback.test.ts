import { expect, test } from "bun:test";
import { areaFeedback, areaPath } from "#core";
import { area, snapshotOf } from "./builders.ts";

test("shared_rank_feedback", () => {
  const s = snapshotOf(["storage", "a", "b", "c"].map((n) => area({ name: n, rank: 2 })));
  expect(areaFeedback(s, [areaPath("storage")])).toEqual([
    {
      recordId: "area:storage",
      message:
        "rank 2 is shared with area a, b, and c; areas that share a rank are ordered by name",
    },
  ]);
  for (const [names, expected] of [
    [["a"], "a"],
    [["a", "b"], "a and b"],
  ] as const) {
    const s = snapshotOf([area({ rank: 0 }), ...names.map((n) => area({ name: n, rank: 0 }))]);
    expect(areaFeedback(s, [areaPath("storage")])[0]?.message).toEqual(
      `rank 0 is shared with area ${expected}; areas that share a rank are ordered by name`,
    );
  }
});
test("unshared_rank_no_feedback", () => {
  const s = snapshotOf([
    area({ rank: 1 }),
    area({ name: "other", rank: 2 }),
    area({ name: "plain" }),
  ]);
  expect(
    areaFeedback(
      s,
      [...s.areas.keys()].map((n) => areaPath(n)),
    ),
  ).toEqual([]);
});
test("unwritten_area_no_feedback", () => {
  const s = snapshotOf([area({ rank: 1 }), area({ name: "other", rank: 1 })]);
  expect(areaFeedback(s, [])).toEqual([]);
});
