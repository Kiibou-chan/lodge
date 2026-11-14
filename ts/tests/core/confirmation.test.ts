import { expect, test } from "bun:test";
import {
  Action,
  behindArea,
  confirmableIds,
  confirmationDraft,
  derive,
  LookupError,
  parseDraft,
  recordFromDraft,
  Scope,
  ValueError,
} from "#core";
import { at, decision, entry, snapshotOf } from "./builders.ts";

test("confirmable_ids_skip_author_confirmed_and_replaced", () => {
  const s = snapshotOf([
    decision({ id: "d-aaaaaa" }),
    decision({ id: "d-bbbbbb" }),
    decision({ id: "d-cccccc" }),
    decision({ id: "d-dddddd", decidedBy: "author", confirms: ["d-aaaaaa"] }),
    decision({ id: "d-eeeeee", replaces: ["d-bbbbbb"] }),
  ]);
  expect(confirmableIds(s, derive(s))).toEqual(new Set(["d-cccccc", "d-eeeeee"]));
});
test("behind_area_lists_creators_and_last_changers_oldest_first", () => {
  const s = snapshotOf([
    entry({ id: "s-aaaaaa" }),
    decision({
      id: "d-aaaaaa",
      date: at(2),
      changes: [{ entry: "s-aaaaaa", action: Action.EDIT }],
    }),
    decision({
      id: "d-cccccc",
      date: at(0),
      changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
    }),
    decision({
      id: "d-bbbbbb",
      date: at(1),
      changes: [{ entry: "s-aaaaaa", action: Action.EDIT }],
    }),
  ]);
  expect(behindArea(s, derive(s), "storage")).toEqual(["d-cccccc", "d-aaaaaa"]);
});
test("behind_area_includes_the_retirer_of_a_retired_entry", () => {
  const s = snapshotOf([
    entry({ id: "s-aaaaaa" }),
    decision({ id: "d-aaaaaa", changes: [{ entry: "s-aaaaaa", action: Action.RETIRE }] }),
  ]);
  expect(behindArea(s, derive(s), "storage")).toEqual(["d-aaaaaa"]);
});
test("confirmation_draft_single", () => {
  const words = 'Read: "yes".\nStill a caveat.';
  const draft = parseDraft(
    "viewer",
    confirmationDraft(["d-aaaaaa"], Scope.PRODUCT, words, "2026-10-29 09:30", null),
  );
  expect(draft.kind).not.toBe("problem");
  if (draft.kind === "problem") throw new Error("expected Draft");
  const made = recordFromDraft(draft, "d-bbbbbb", at(1), null);
  expect(made.kind).toBe("decision");
  if (made.kind !== "decision") throw new Error("expected Decision");
  expect(made.title).toBe("Confirms d-aaaaaa");
  expect(made.statement).toBe("The author confirms d-aaaaaa.");
  expect(made.reasoning).toBe(words);
  expect(made.quote?.where).toBe("lodge viewer");
});
test("confirmation_draft_area_lists_with_the_oxford_comma", () => {
  const draft = parseDraft(
    "viewer",
    confirmationDraft(
      ["d-aaaaaa", "d-bbbbbb", "d-cccccc"],
      Scope.PROCESS,
      "Read.",
      "now",
      "storage",
    ),
  );
  expect(draft.kind).not.toBe("problem");
  if (draft.kind === "problem") throw new Error("expected Draft");
  const made = recordFromDraft(draft, "d-dddddd", at(1), null);
  expect(made.kind).toBe("decision");
  if (made.kind !== "decision") throw new Error("expected Decision");
  expect(made.title).toBe("Confirms the decisions behind area storage");
  expect(made.statement).toBe("The author confirms d-aaaaaa, d-bbbbbb, and d-cccccc.");
});
test("behind_area_same_date_uses_id_tie_break", () => {
  const s = snapshotOf([
    entry({ id: "s-aaaaaa" }),
    decision({
      id: "d-cccccc",
      date: at(0),
      changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
    }),
    decision({
      id: "d-aaaaaa",
      date: at(0),
      changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
    }),
  ]);
  expect(behindArea(s, derive(s), "storage")).toEqual(["d-aaaaaa", "d-cccccc"]);
});
test("confirmation_draft_two_uses_and", () => {
  const draft = parseDraft(
    "viewer",
    confirmationDraft(["d-aaaaaa", "d-bbbbbb"], Scope.PRODUCT, "Read.", "now", "storage"),
  );
  expect(draft.kind).not.toBe("problem");
  if (draft.kind === "problem") throw new Error("expected Draft");
  const made = recordFromDraft(draft, "d-cccccc", at(1), null);
  expect(made.kind).toBe("decision");
  if (made.kind !== "decision") throw new Error("expected Decision");
  expect(made.statement).toBe("The author confirms d-aaaaaa and d-bbbbbb.");
});
test.each([[], ["d-aaaaaa", "d-bbbbbb"]].map((c) => [c]))(
  "confirmation_draft_without_area_requires_one_id %p",
  (ids) => {
    const call = () => confirmationDraft(ids, Scope.PRODUCT, "Read.", "now", null);
    expect(call).toThrow(ValueError);
    expect(call).toThrow(/one decision/u);
  },
);
test("confirmation_draft_empty_area_list_keeps_python_index_error", () => {
  const call = () => confirmationDraft([], Scope.PRODUCT, "Read.", "now", "storage");
  expect(call).toThrow(LookupError);
  expect(call).toThrow("list index out of range");
});
