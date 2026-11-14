import { expect, test } from "bun:test";
import { Action, type Change, derive } from "#core";
import { at, decision, entry } from "./builders.ts";
import { IMPORTED, snapshotOf } from "./derivation.ts";

test("imported_touching_only_imported_not_flagged", () => {
  const old = decision({
    id: "d-aaaaaa",
    decidedBy: "author",
    date: "2026-01-01T00:00:00+00:00",
    importedFrom: IMPORTED,
  });
  const successor = decision({
    id: "d-bbbbbb",
    date: "2026-02-01T00:00:00+00:00",
    replaces: ["d-aaaaaa"],
    importedFrom: IMPORTED,
  });
  expect(derive(snapshotOf(old, successor)).awaitingAuthor).toEqual(new Set());
});
test("imported_after_imported_author_edit_not_flagged", () => {
  const spec = entry({ id: "s-aaaaaa", importedFrom: IMPORTED });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const old = decision({
    id: "d-aaaaaa",
    decidedBy: "author",
    date: "2026-01-01T00:00:00+00:00",
    changes: change,
    importedFrom: IMPORTED,
  });
  const successor = decision({
    id: "d-bbbbbb",
    date: "2026-02-01T00:00:00+00:00",
    changes: change,
    importedFrom: IMPORTED,
  });
  expect(derive(snapshotOf(spec, old, successor)).awaitingAuthor).toEqual(new Set());
});
test("imported_replacing_live_author_decision_flagged", () => {
  const old = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const successor = decision({
    id: "d-bbbbbb",
    date: "2026-11-01T00:00:00+00:00",
    replaces: ["d-aaaaaa"],
    importedFrom: IMPORTED,
  });
  expect(derive(snapshotOf(old, successor)).awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
test("imported_author_replacing_live_author_decision_flagged", () => {
  const old = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const successor = decision({
    id: "d-bbbbbb",
    decidedBy: "author",
    date: "2026-01-01T00:00:00+00:00",
    replaces: ["d-aaaaaa"],
    importedFrom: IMPORTED,
  });
  expect(derive(snapshotOf(old, successor)).awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
test("imported_author_editing_live_author_entry_flagged", () => {
  const spec = entry({ id: "s-aaaaaa" });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const old = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: change });
  const successor = decision({
    id: "d-bbbbbb",
    decidedBy: "author",
    date: "2026-11-01T00:00:00+00:00",
    changes: change,
    importedFrom: IMPORTED,
  });
  expect(derive(snapshotOf(spec, old, successor)).awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
test("imported_author_confirm_does_not_clear", () => {
  const author = decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0) });
  const agent = decision({ id: "d-bbbbbb", date: at(1), replaces: ["d-aaaaaa"] });
  const confirm = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: "2026-11-01T00:00:00+00:00",
    confirms: ["d-bbbbbb"],
    importedFrom: IMPORTED,
  });
  expect(derive(snapshotOf(author, agent, confirm)).awaitingAuthor).toEqual(new Set(["d-bbbbbb"]));
});
test("imported_author_creation_not_flagged_by_her_later_live_edit", () => {
  const spec = entry({ id: "s-aaaaaa", importedFrom: IMPORTED });
  const created = decision({
    id: "d-aaaaaa",
    decidedBy: "author",
    date: "2026-01-01T00:00:00+00:00",
    changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
    importedFrom: IMPORTED,
  });
  const edit = decision({
    id: "d-bbbbbb",
    decidedBy: "author",
    date: at(0),
    changes: [{ entry: "s-aaaaaa", action: Action.EDIT }],
  });
  expect(derive(snapshotOf(spec, created, edit)).awaitingAuthor).toEqual(new Set());
});
test("imported_agent_edit_before_her_later_live_edit_not_flagged", () => {
  const spec = entry({ id: "s-aaaaaa", importedFrom: IMPORTED });
  const created = decision({
    id: "d-aaaaaa",
    decidedBy: "author",
    date: "2026-01-01T00:00:00+00:00",
    changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
    importedFrom: IMPORTED,
  });
  const change: readonly Change[] = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const between = decision({
    id: "d-cccccc",
    date: "2026-02-01T00:00:00+00:00",
    changes: change,
    importedFrom: IMPORTED,
  });
  const edit = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(0), changes: change });
  expect(derive(snapshotOf(spec, created, between, edit)).awaitingAuthor).toEqual(new Set());
});
