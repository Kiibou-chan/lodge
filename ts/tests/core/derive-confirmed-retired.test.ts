import { expect, test } from "bun:test";
import { Action, type Change, derive } from "#core";
import { at, decision, entry } from "./builders.ts";
import { IMPORTED, snapshotOf } from "./derivation.ts";

test("agent_rewrites_an_edit_she_confirmed", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: change });
  const first = decision({ id: "d-bbbbbb", date: at(1), changes: change });
  const confirm = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    confirms: ["d-bbbbbb"],
  });
  const second = decision({ id: "d-dddddd", date: at(3), changes: change });
  const got = derive(snapshotOf(spec, author, first, confirm, second));
  expect(got.awaitingAuthor).toEqual(new Set(["d-dddddd"]));
});
test("agent_replaces_a_decision_she_confirmed", () => {
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const first = decision({ id: "d-bbbbbb", date: at(1), narrows: ["d-aaaaaa"] });
  const confirm = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    confirms: ["d-bbbbbb"],
  });
  const second = decision({ id: "d-dddddd", date: at(3), replaces: ["d-bbbbbb"] });
  expect(derive(snapshotOf(author, first, confirm, second)).awaitingAuthor).toEqual(
    new Set(["d-dddddd"]),
  );
});
test("confirmation_dated_after_the_later_agent_change_still_counts", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: change });
  const first = decision({ id: "d-bbbbbb", date: at(1), changes: change });
  const second = decision({ id: "d-cccccc", date: at(2), changes: change });
  const confirm = decision({
    id: "d-dddddd",
    decidedBy: "author",
    date: at(9),
    confirms: ["d-bbbbbb"],
  });
  const got = derive(snapshotOf(spec, author, first, second, confirm));
  expect(got.awaitingAuthor).toEqual(new Set(["d-cccccc"]));
});
test("imported_confirmation_does_not_make_a_decision_hers", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: change });
  const first = decision({ id: "d-bbbbbb", date: at(1), changes: change });
  const confirm = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: "2026-11-01T00:00:00+00:00",
    confirms: ["d-bbbbbb"],
    importedFrom: IMPORTED,
  });
  const second = decision({ id: "d-dddddd", date: at(3), changes: change });
  const got = derive(snapshotOf(spec, author, first, confirm, second));
  expect(got.awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
function retiredByAnAgent() {
  const create: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.CREATE }];
  return [
    entry({ id: "s-aaaaaa" }),
    decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: create }),
    decision({
      id: "d-bbbbbb",
      date: at(1),
      changes: [{ entry: "s-aaaaaa", action: Action.RETIRE }],
    }),
  ];
}
test("replacing_the_retirement_makes_the_entry_current", () => {
  const rejected = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
  });
  const kept = derive(snapshotOf(...retiredByAnAgent()));
  const back = derive(snapshotOf(...retiredByAnAgent(), rejected));
  expect(kept.status.get("s-aaaaaa")).toEqual("retired");
  expect([back.status.get("s-aaaaaa"), back.status.get("d-bbbbbb")]).toEqual([
    "current",
    "replaced",
  ]);
  expect(back.awaitingAuthor).toEqual(new Set());
});
test("entry_stays_retired_while_another_retirement_stands", () => {
  const again = decision({
    id: "d-cccccc",
    date: at(2),
    changes: [{ entry: "s-aaaaaa", action: Action.RETIRE }],
  });
  const rejected = decision({
    id: "d-dddddd",
    decidedBy: "author",
    date: at(3),
    replaces: ["d-bbbbbb"],
  });
  const got = derive(snapshotOf(...retiredByAnAgent(), again, rejected));
  expect(got.status.get("s-aaaaaa")).toEqual("retired");
});
test("agent_edit_after_she_replaced_an_agent_retirement_flagged", () => {
  const rejected = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
  });
  const edit = decision({
    id: "d-dddddd",
    date: at(3),
    changes: [{ entry: "s-aaaaaa", action: Action.EDIT }],
  });
  const got = derive(snapshotOf(...retiredByAnAgent(), rejected, edit));
  expect(got.awaitingAuthor).toEqual(new Set(["d-dddddd"]));
});
test("agent_edit_after_she_replaced_an_agent_edit_flagged", () => {
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const first = decision({ id: "d-bbbbbb", date: at(1), changes: change });
  const rejected = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
  });
  const second = decision({ id: "d-dddddd", date: at(3), changes: change });
  const items = [...retiredByAnAgent().slice(0, 2), first, rejected, second];
  expect(derive(snapshotOf(...items)).awaitingAuthor).toEqual(new Set(["d-dddddd"]));
});
test("agent_edit_after_an_agent_replaced_by_an_agent_is_as_before", () => {
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const first = decision({ id: "d-bbbbbb", date: at(1), changes: change });
  const second = decision({ id: "d-cccccc", date: at(2), replaces: ["d-bbbbbb"], changes: change });
  const third = decision({ id: "d-dddddd", date: at(3), changes: change });
  const items = [...retiredByAnAgent().slice(0, 2), first, second, third];
  expect(derive(snapshotOf(...items)).awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
test("agent_edit_after_she_corrected_her_own_decision_flagged", () => {
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const created = [...retiredByAnAgent().slice(0, 2)];
  const correction = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-aaaaaa"],
  });
  const edit = decision({ id: "d-dddddd", date: at(3), changes: change });
  expect(derive(snapshotOf(...created, correction, edit)).awaitingAuthor).toEqual(
    new Set(["d-dddddd"]),
  );
});
test("agent_edit_after_she_corrected_her_own_edit_flagged", () => {
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const start = decision({
    id: "d-aaaaaa",
    date: at(0),
    changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
  });
  const hers = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: change });
  const correction = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
  });
  const edit = decision({ id: "d-dddddd", date: at(3), changes: change });
  const got = derive(snapshotOf(entry({ id: "s-aaaaaa" }), start, hers, correction, edit));
  expect(got.awaitingAuthor).toEqual(new Set(["d-dddddd"]));
});
function retiredByHer() {
  const kill: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.RETIRE }];
  const author = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: kill });
  return [...retiredByAnAgent().slice(0, 2), author];
}
test("agent_reviving_her_retired_entry_flags_the_entry", () => {
  const revive = decision({ id: "d-cccccc", date: at(2), replaces: ["d-bbbbbb"] });
  const got = derive(snapshotOf(...retiredByHer(), revive));
  expect(got.status.get("s-aaaaaa")).toEqual("current");
  expect(got.awaitingAuthor).toEqual(new Set(["d-cccccc"]));
  expect(got.touchedByFlagged.get("s-aaaaaa")).toEqual(["d-cccccc"]);
  expect(got.changedBy.get("s-aaaaaa")?.[0]).toEqual("d-cccccc");
});
test("agent_reviving_an_entry_an_agent_retired_is_not_flagged", () => {
  const revive = decision({ id: "d-cccccc", date: at(2), replaces: ["d-bbbbbb"] });
  const got = derive(snapshotOf(...retiredByAnAgent(), revive));
  expect(got.awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
  expect(got.touchedByFlagged.get("s-aaaaaa")).toEqual(["d-bbbbbb"]);
});
