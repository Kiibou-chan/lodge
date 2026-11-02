import { expect, test } from "bun:test";
import { Action, derive } from "#core";
import { area, at, decision, entry, snapshotOf } from "./builders.ts";

test("link_is_not_a_change", () => {
  const e = entry();
  const link = decision({ changes: [{ entry: e.id, action: Action.LINK }] });
  const d = derive(snapshotOf([area(), e, link]));
  expect(d.changedBy.has(e.id)).toBe(false);
  expect(d.linkedBy.get(e.id)).toEqual([link.id]);
});
test("link_raises_no_flag", () => {
  const e = entry();
  const author = decision({
    decidedBy: "author",
    changes: [{ entry: e.id, action: Action.CREATE }],
  });
  const link = decision({ date: at(30), changes: [{ entry: e.id, action: Action.LINK }] });
  const d = derive(snapshotOf([area(), e, author, link]));
  expect(d.awaitingAuthor.has(link.id)).toBe(false);
  expect(d.touchedByFlagged.has(e.id)).toBe(false);
});
test("supports_is_the_reverse_of_rests_on", () => {
  const a = entry({ id: "s-aaaaaa" });
  const b = entry({ id: "s-bbbbbb", restsOn: [a.id, "s-zzzzzz"] });
  const c = entry({ id: "s-cccccc", restsOn: [a.id] });
  const d = derive(snapshotOf([area(), c, b, a]));
  expect(d.supports).toEqual(new Map([[a.id, [b.id, c.id]]]));
});
