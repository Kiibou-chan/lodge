import { Action, decision, Scope } from "#core";
export const DECISION_PATH = "lodge/decisions/d-3m8qk2-whole-transcripts-are-kept-before-a.md";

export const SPEC_PATH = "lodge/spec/storage/s-4kq1zm-transcripts-are-kept.md";

export const TITLE = "Whole transcripts are kept before a session is archived";

export const EXAMPLE = decision({
  id: "d-3m8qk2",
  title: TITLE,
  scope: Scope.PROCESS,
  decidedBy: "author",
  date: "2026-10-28T23:48:10+01:00",
  statement: "One to three sentences stating the decision.",
  reasoning: "Why, in a few hundred words at most.",
  code: "ITEM-1",
  changes: [{ entry: "s-4kq1zm", action: Action.EDIT }],
  replaces: ["d-8rw0te"],
  quote: { text: "Record it.", where: "first session", when: "2026-10-28 23:48" },
});

export const EXAMPLE_TEXT = `---
id: d-3m8qk2
kind: decision
code: ITEM-1
title: "${TITLE}"
scope: process
decided_by: author
date: 2026-10-28T23:48:10+01:00
changes:
  - {entry: s-4kq1zm, action: edit}
replaces: [d-8rw0te]
quote: {text: "Record it.", where: "first session", when: "2026-10-28 23:48"}
---

One to three sentences stating the decision.

## Reasoning

Why, in a few hundred words at most.
`;

export const BASE_HEADER = [
  "id: d-3m8qk2",
  "kind: decision",
  'title: "A title"',
  "scope: product",
  "decided_by: coordinator",
  "date: 2026-10-28T23:48:10+01:00",
];

export function document(header: readonly string[], body: string = "A statement.") {
  return `---\n${header.join("\n")}\n---\n\n${body}\n`;
}

export function replaced(key: string, line: string | null) {
  const kept = BASE_HEADER.filter((row) => !row.startsWith(`${key}:`));
  return line === null ? kept : [...kept, line];
}
