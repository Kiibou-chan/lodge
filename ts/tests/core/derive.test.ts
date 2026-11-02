import { expect, test } from "bun:test";
import { Action, type Change, derive, isAuthor, load, tree } from "#core";
import { at, decision, entry, filesOf } from "./builders.ts";
import { snapshotOf } from "./derivation.ts";

test("is_author", () => {
  expect(isAuthor(decision({ decidedBy: "author" }))).toBe(true);
  expect(isAuthor(decision({ decidedBy: "coordinator" }))).toBe(false);
});
test("replaced_and_successor", () => {
  const old = decision({ id: "d-aaaaaa", date: at(0) });
  const successor = decision({ id: "d-bbbbbb", date: at(1), replaces: ["d-aaaaaa"] });
  const got = derive(snapshotOf(old, successor));
  expect(got.status).toEqual(
    new Map([
      ["d-aaaaaa", "replaced"],
      ["d-bbbbbb", "current"],
    ]),
  );
  expect(got.replacedBy).toEqual(new Map([["d-aaaaaa", ["d-bbbbbb"]]]));
});
test("narrowed_stays_current", () => {
  const old = decision({ id: "d-aaaaaa", date: at(0) });
  const successor = decision({ id: "d-bbbbbb", date: at(1), narrows: ["d-aaaaaa"] });
  const got = derive(snapshotOf(old, successor));
  expect(got.status.get("d-aaaaaa")).toEqual("current");
  expect(got.narrowedBy).toEqual(new Map([["d-aaaaaa", ["d-bbbbbb"]]]));
  expect(got.replacedBy).toEqual(new Map([]));
});
test("retired_entry", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const make = decision({
    id: "d-aaaaaa",
    date: at(0),
    changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
  });
  const kill = decision({
    id: "d-bbbbbb",
    date: at(1),
    changes: [{ entry: "s-aaaaaa", action: Action.RETIRE }],
  });
  expect(derive(snapshotOf(spec, make)).status.get("s-aaaaaa")).toEqual("current");
  expect(derive(snapshotOf(spec, make, kill)).status.get("s-aaaaaa")).toEqual("retired");
});
test("changed_by_newest_first", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const ds = [
    decision({ id: "d-aaaaaa", date: at(5), changes: change }),
    decision({ id: "d-bbbbbb", date: at(9), changes: change }),
    decision({ id: "d-cccccc", date: at(1), changes: change }),
    decision({ id: "d-dddddd", date: at(9), changes: change }),
  ];
  const got = derive(snapshotOf(spec, ...ds));
  expect(got.changedBy).toEqual(
    new Map([["s-aaaaaa", ["d-dddddd", "d-bbbbbb", "d-aaaaaa", "d-cccccc"]]]),
  );
});
test("agent_replacing_author_flagged", () => {
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const agent = decision({ id: "d-bbbbbb", date: at(1), replaces: ["d-aaaaaa"] });
  expect(derive(snapshotOf(author, agent)).awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
test("agent_narrowing_author_flagged", () => {
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const agent = decision({ id: "d-bbbbbb", date: at(1), narrows: ["d-aaaaaa"] });
  expect(derive(snapshotOf(author, agent)).awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
test("author_decisions_are_never_flagged", () => {
  const first = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const second = decision({
    id: "d-bbbbbb",
    decidedBy: "author",
    date: at(1),
    replaces: ["d-aaaaaa"],
  });
  expect(derive(snapshotOf(first, second)).awaitingAuthor).toEqual(new Set());
});
test("agent_after_author_edit_flagged", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: change });
  const agent = decision({ id: "d-bbbbbb", date: at(1), changes: change });
  expect(derive(snapshotOf(spec, author, agent)).awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
test("agent_after_agent_edit_not_flagged", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: change });
  const first = decision({ id: "d-bbbbbb", date: at(1), changes: change });
  const second = decision({ id: "d-cccccc", date: at(2), changes: change });
  expect(derive(snapshotOf(spec, author, first, second)).awaitingAuthor).toEqual(
    new Set(["d-bbbbbb"]),
  );
});
test("author_edit_dated_after_the_agent_does_not_flag_it", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const agent = decision({ id: "d-aaaaaa", date: at(0), changes: change });
  const author = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: change });
  expect(derive(snapshotOf(spec, agent, author)).awaitingAuthor).toEqual(new Set());
});
test("flag_clears_on_confirm", () => {
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const agent = decision({ id: "d-bbbbbb", date: at(1), replaces: ["d-aaaaaa"] });
  const confirm = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    confirms: ["d-bbbbbb"],
  });
  const got = derive(snapshotOf(author, agent, confirm));
  expect(got.awaitingAuthor).toEqual(new Set());
  expect(got.confirmedBy).toEqual(new Map([["d-bbbbbb", ["d-cccccc"]]]));
});
test("confirm_by_an_agent_does_not_clear", () => {
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const agent = decision({ id: "d-bbbbbb", date: at(1), replaces: ["d-aaaaaa"] });
  const other = decision({ id: "d-cccccc", date: at(2), confirms: ["d-bbbbbb"] });
  const got = derive(snapshotOf(author, agent, other));
  expect(got.awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
  expect(got.confirmedBy).toEqual(new Map([]));
});
test("flag_clears_on_author_replace", () => {
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const agent = decision({ id: "d-bbbbbb", date: at(1), replaces: ["d-aaaaaa"] });
  const again = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
  });
  expect(derive(snapshotOf(author, agent, again)).awaitingAuthor).toEqual(new Set());
});
test("flag_shows_on_targets", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: change });
  const agent = decision({ id: "d-bbbbbb", date: at(1), changes: change, narrows: ["d-aaaaaa"] });
  const got = derive(snapshotOf(spec, author, agent));
  expect(got.touchedByFlagged).toEqual(
    new Map([
      ["s-aaaaaa", ["d-bbbbbb"]],
      ["d-aaaaaa", ["d-bbbbbb"]],
    ]),
  );
  const cleared = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    confirms: ["d-bbbbbb"],
  });
  expect(derive(snapshotOf(spec, author, agent, cleared)).touchedByFlagged).toEqual(new Map([]));
});
test("agent_change_to_missing_entry_does_not_crash", () => {
  const change: readonly Change[] = [{ entry: "s-zzzzzz", action: Action.EDIT }];
  const agent = decision({ id: "d-aaaaaa", date: at(0), changes: change });
  const got = derive(load(tree({ rev: null, files: filesOf(agent), attachments: new Set() })));
  expect(got.awaitingAuthor).toEqual(new Set());
  expect(got.changedBy).toEqual(new Map([]));
  expect(got.touchedByFlagged).toEqual(new Map([]));
});
test("agent_after_author_edit_of_unparsable_entry_flagged", () => {
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: change });
  const agent = decision({ id: "d-bbbbbb", date: at(1), changes: change });
  const files = filesOf(author, agent);
  files.set(
    "lodge/spec/storage/s-aaaaaa-broken.md",
    "---\nid: s-aaaaaa\nkind: spec\n---\n\nText.\n",
  );
  const snap = load(tree({ rev: null, files: files, attachments: new Set() }));
  expect(snap.problems.length).toEqual(1);
  const got = derive(snap);
  expect(got.awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
  expect(got.changedBy).toEqual(new Map([]));
});
test("confirm_dated_before_does_not_clear", () => {
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const agent = decision({ id: "d-bbbbbb", date: at(5), replaces: ["d-aaaaaa"] });
  const early = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    confirms: ["d-bbbbbb"],
  });
  expect(derive(snapshotOf(author, agent, early)).awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
