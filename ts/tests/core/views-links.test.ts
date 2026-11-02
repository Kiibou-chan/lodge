import { expect, test } from "bun:test";
import { Action, type Action as ChangeAction, derive, level1, level3 } from "#core";
import { area, at, decision, entry, snapshotOf } from "./builders.ts";

function views(retire = false, later: ChangeAction | null = null) {
  const a = entry({ id: "s-aaaaaa", restsOn: ["s-bbbbbb"] });
  const b = entry({ id: "s-bbbbbb" });
  const own = decision({
    id: "d-aaaaaa",
    decidedBy: "author",
    changes: [{ entry: a.id, action: Action.CREATE }],
  });
  const target = decision({
    id: "d-bbbbbb",
    date: at(10),
    changes: [{ entry: b.id, action: retire ? Action.RETIRE : Action.EDIT }],
  });
  const extra =
    later === null
      ? []
      : [decision({ id: "d-cccccc", date: at(20), changes: [{ entry: a.id, action: later }] })];
  const s = snapshotOf([area(), a, b, own, target, ...extra]);
  const d = derive(s);
  return [level1(s, d, a.id, new Set()), level3(s, d, a.id), level3(s, d, b.id)] as const;
}
test("rests_on_retired_mark", () => {
  expect(views(true)[0].flags).toContain("rests on s-bbbbbb, retired");
});
test("rests_on_changed_since_mark", () => {
  expect(views()[0].flags).toContain("rests on s-bbbbbb, changed since");
});
test("same_second_change_does_not_mark_changed_since", () => {
  const a = entry({ id: "s-aaaaaa", restsOn: ["s-bbbbbb"] }),
    b = entry({ id: "s-bbbbbb" });
  const own = decision({
      id: "d-aaaaaa",
      date: at(10),
      changes: [{ entry: a.id, action: Action.EDIT }],
    }),
    target = decision({
      id: "d-bbbbbb",
      date: at(10),
      changes: [{ entry: b.id, action: Action.EDIT }],
    });
  const s = snapshotOf([area(), a, b, own, target]);
  expect(level1(s, derive(s), a.id, new Set()).flags).not.toContain(
    "rests on s-bbbbbb, changed since",
  );
});
test("edit_with_unchanged_text_clears_changed_since", () => {
  expect(views(false, Action.EDIT)[0].flags).not.toContain("rests on s-bbbbbb, changed since");
});
test("link_after_the_change_keeps_changed_since", () => {
  expect(views(false, Action.LINK)[0].flags).toContain("rests on s-bbbbbb, changed since");
});
test("entry_level1_keeps_the_author_after_a_link", () => {
  expect(views(false, Action.LINK)[0].decidedBy).toBe("author");
});
test("level3_lists_rests_on_supports_and_linked_by", () => {
  const [, own, target] = views(false, Action.LINK);
  expect(own.links).toEqual([
    ["changed by", "d-aaaaaa", "current"],
    ["rests on", "s-bbbbbb", "current"],
    ["linked by", "d-cccccc", "current"],
  ]);
  expect(target.links).toContainEqual(["supports", "s-aaaaaa", "current"]);
});
