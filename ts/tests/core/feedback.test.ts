import { expect, test } from "bun:test";
import {
  Action,
  derive,
  type Feedback,
  feedback,
  type LengthGuidance,
  lengthGuidance,
  type Record,
  type Snapshot,
} from "#core";
import { at, decision, entry, snapshotOf } from "./builders.ts";

const LENGTH = lengthGuidance({
  titleChars: 20,
  decisionStatementWords: 5,
  specStatementWords: 8,
  reasoningWords: 6,
});
const ROOMY = lengthGuidance();
function given(snapshot: Snapshot, added: Record, length: LengthGuidance = ROOMY): Feedback[] {
  return feedback([added], snapshot, derive(snapshot), length);
}
test("clean_decision_no_feedback", () => {
  const d = decision({ id: "d-aaaaaa", title: "Keep transcripts", statement: "They are kept." });
  expect(given(snapshotOf([d]), d)).toEqual([]);
});
test("title_over_guidance", () => {
  const d = decision({
    id: "d-aaaaaa",
    title: "A title that is much too long",
    statement: "Short.",
  });
  expect(given(snapshotOf([d]), d, LENGTH)).toEqual([
    {
      recordId: "d-aaaaaa",
      message: "the title is 29 characters; guidance is 20 or fewer, on one line",
    },
  ]);
});
test("decision_statement_over_guidance", () => {
  const d = decision({ id: "d-aaaaaa", title: "Short", statement: "One two three four five six." });
  expect(given(snapshotOf([d]), d, LENGTH)).toEqual([
    {
      recordId: "d-aaaaaa",
      message: "the statement is 6 words; guidance is 5 or fewer for a decision",
    },
  ]);
});
test("spec_statement_over_guidance", () => {
  const e = entry({
    id: "s-aaaaaa",
    title: "Short",
    statement: "One two three four five six seven eight nine.",
  });
  expect(given(snapshotOf([e]), e, LENGTH)).toEqual([
    {
      recordId: "s-aaaaaa",
      message: "the statement is 9 words; guidance is 8 or fewer for a specification entry",
    },
  ]);
});
test("statement_at_the_limit_is_clean", () => {
  const d = decision({ id: "d-aaaaaa", title: "Short", statement: "One two three four five." });
  expect(given(snapshotOf([d]), d, LENGTH)).toEqual([]);
});
test("words_split_on_whitespace", () => {
  const d = decision({ id: "d-aaaaaa", title: "Short", statement: "a-b\tc\nd e f g" });
  expect(given(snapshotOf([d]), d, LENGTH).map((f) => f.message)).toEqual([
    "the statement is 6 words; guidance is 5 or fewer for a decision",
  ]);
});
test("reasoning_over_guidance", () => {
  const d = decision({
    id: "d-aaaaaa",
    title: "Short",
    statement: "Short.",
    reasoning: "a b c d e f g",
  });
  expect(given(snapshotOf([d]), d, LENGTH)).toEqual([
    { recordId: "d-aaaaaa", message: "the reasoning is 7 words; guidance is 6 or fewer" },
  ]);
});
test("related_decision_asks_replace_or_narrow", () => {
  const old = decision({
    id: "d-aaaaaa",
    title: "Keep transcripts",
    changes: [{ entry: "s-bbbbbb", action: Action.EDIT }],
  });
  const added = decision({
    id: "d-cccccc",
    title: "Archive transcripts",
    date: at(5),
    changes: [{ entry: "s-bbbbbb", action: Action.EDIT }],
  });
  const s = snapshotOf([old, added, entry({ id: "s-bbbbbb" })]);
  expect(given(s, added)).toEqual([
    {
      recordId: "d-cccccc",
      message:
        "it replaces and narrows nothing, but this current decision looks related: d-aaaaaa (Keep transcripts); does d-cccccc replace or narrow d-aaaaaa? If so, set replaces or narrows in the draft before adding it",
    },
  ]);
});
test("related_lists_each_with_its_title", () => {
  const first = decision({
    id: "d-aaaaaa",
    title: "First one",
    changes: [{ entry: "s-bbbbbb", action: Action.EDIT }],
  });
  const second = decision({
    id: "d-dddddd",
    title: "Second one",
    date: at(3),
    changes: [{ entry: "s-bbbbbb", action: Action.EDIT }],
  });
  const added = decision({
    id: "d-cccccc",
    title: "Third",
    date: at(5),
    changes: [{ entry: "s-bbbbbb", action: Action.EDIT }],
  });
  const s = snapshotOf([first, second, added, entry({ id: "s-bbbbbb" })]);
  expect(given(s, added).map((f) => f.message)).toEqual([
    "it replaces and narrows nothing, but these current decisions look related: d-dddddd (Second one), d-aaaaaa (First one); does d-cccccc replace or narrow any of them? If so, set replaces or narrows in the draft before adding it",
  ]);
});
test("related_silent_when_it_replaces_or_narrows", () => {
  const old = decision({
    id: "d-aaaaaa",
    title: "Keep transcripts",
    changes: [{ entry: "s-bbbbbb", action: Action.EDIT }],
  });
  for (const link of [{ replaces: ["d-aaaaaa"] }, { narrows: ["d-aaaaaa"] }]) {
    const added = decision({
      id: "d-cccccc",
      title: "Archive transcripts",
      date: at(5),
      changes: [{ entry: "s-bbbbbb", action: Action.EDIT }],
      ...link,
    });
    expect(given(snapshotOf([old, added, entry({ id: "s-bbbbbb" })]), added)).toEqual([]);
  }
});
test("number_without_handle", () => {
  const d = decision({
    id: "d-aaaaaa",
    title: "Retries",
    statement: "Retry 3 times, or 20% of calls.",
  });
  expect(given(snapshotOf([d]), d)).toEqual([
    {
      recordId: "d-aaaaaa",
      message:
        'the text holds the numbers 3, 20% without a numbers handle; before adding the draft, give each one as `numbers: [{value: "…", handle: "…"}]`, the handle a record and key or a runnable command',
    },
  ]);
});
test("number_in_reasoning_counts", () => {
  const d = decision({
    id: "d-aaaaaa",
    title: "Retries",
    statement: "Retry.",
    reasoning: "It took 1.5 s.",
  });
  expect(
    given(snapshotOf([d]), d)
      .map((f) => f.message)[0]
      ?.startsWith("the text holds the number 1.5 "),
  ).toBe(true);
});
test("numbers_in_backticks_ignored", () => {
  const d = decision({
    id: "d-aaaaaa",
    title: "Retries",
    statement: "Run `pytest -n 4` first.",
    reasoning: "```\nseq 1 10\n```\nThen stop.",
  });
  expect(given(snapshotOf([d]), d)).toEqual([]);
});
test("numbers_ignore_ids_codes_and_dates", () => {
  const other = decision({ id: "d-bbbbbb", code: "ITEM-1", date: at(9) });
  const d = decision({
    id: "d-aaaaaa",
    title: "Retries",
    statement: "As d-3m8qk2 and s-4kq1zm say in item-1, since 2026-10-28.",
    reasoning: "Written 2026-10-28T10:00:00+01:00.",
  });
  expect(given(snapshotOf([d, other]), d)).toEqual([]);
});
test("number_in_a_word_that_is_not_a_code_is_flagged", () => {
  const other = decision({ id: "d-bbbbbb", code: "ITEM-1", date: at(9) });
  const d = decision({
    id: "d-aaaaaa",
    title: "Hits",
    statement: "Show the top-10 hits and Python-3.",
  });
  const message = given(snapshotOf([d, other]), d).map((f) => f.message)[0];
  expect(message?.startsWith("the text holds the numbers 10, 3 without")).toBe(true);
});
test("numbers_with_handle_are_clean", () => {
  const d = decision({
    id: "d-aaaaaa",
    title: "Retries",
    statement: "Retry 3 times.",
    numbers: [{ value: "3", handle: "uv run pytest" }],
  });
  expect(given(snapshotOf([d]), d)).toEqual([]);
});
test("decision_derive_flags_waits_for_author", () => {
  const mine = decision({ id: "d-aaaaaa", title: "Mine", decidedBy: "author" });
  const flagged = decision({
    id: "d-bbbbbb",
    title: "Theirs",
    date: at(5),
    replaces: ["d-aaaaaa"],
  });
  const s = snapshotOf([mine, flagged]);
  expect(derive(s).awaitingAuthor.has("d-bbbbbb")).toBe(true);
  expect(given(s, flagged)).toEqual([
    {
      recordId: "d-bbbbbb",
      message:
        "this decision will wait for the author: it takes effect at once, and a later author decision that confirms or replaces it clears the flag",
    },
  ]);
});
test("feedback_on_decision_with_changes_and_related", () => {
  const old = decision({
    id: "d-aaaaaa",
    title: "Keep transcripts",
    decidedBy: "author",
    changes: [{ entry: "s-bbbbbb", action: Action.EDIT }],
  });
  const added = decision({
    id: "d-cccccc",
    title: "Archive transcripts after 30 days",
    date: at(5),
    changes: [{ entry: "s-bbbbbb", action: Action.EDIT }],
    statement: "One two three four five six.",
  });
  const s = snapshotOf([old, added, entry({ id: "s-bbbbbb" })]);
  const messages = given(s, added, LENGTH).map((f) => f.message);
  expect(messages.length).toEqual(4);
  expect(messages[0]?.startsWith("the title is")).toBe(true);
  expect(messages[1]?.startsWith("the statement is 6 words")).toBe(true);
  expect(messages[2]?.startsWith("it replaces and narrows nothing")).toBe(true);
  expect(messages[3]?.startsWith("this decision will wait")).toBe(true);
});
test("one_call_covers_every_added_record", () => {
  const d = decision({ id: "d-aaaaaa", title: "A title that is much too long" });
  const e = entry({ id: "s-bbbbbb", title: "Another title that is far too long" });
  const s = snapshotOf([d, e]);
  const found = feedback([d, e], s, derive(s), LENGTH);
  expect(found.map((f) => f.recordId)).toEqual(["d-aaaaaa", "s-bbbbbb"]);
});
