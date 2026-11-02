import { expect, test } from "bun:test";
import { derive, filters, search } from "#core";
import { at, decision, entry, snapshotOf } from "./builders.ts";

// TypeScript additions for the brief's text and undated ordering edges.
test("undated_entries_follow_dated_decisions_and_underscore_splits_words", () => {
  const e = entry({ id: "s-aaaaaa", title: "x_y" });
  const d = decision({ id: "d-bbbbbb", title: "x", date: at(1) });
  const s = snapshotOf([e, d]);
  expect(search(s, derive(s), "x", filters())).toEqual([d.id, e.id]);
});
