---
id: d-a3h9f3
kind: decision
title: "Advisor ruling on three plan-review findings: closing without text, dependency indent, thread scope"
scope: process
decided_by: advisor
date: 2026-10-31T01:41:20+01:00
work_item: "docs/superpowers/plans/2026-10-31-lodge-viewer.md"
numbers:
  - {value: "85", handle: "sed -n 85p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "2", handle: "must-not 2 of the design: sed -n 45p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "45", handle: "sed -n 45p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "81", handle: "sed -n 81p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "1", handle: "check 1: uv run lodge show s-qzk2yb"}
  - {value: "5", handle: "check 5: uv run lodge show s-ms14fq"}
  - {value: "15", handle: "sed -n 15p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "118", handle: "sed -n 118p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "120", handle: "sed -n 120p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "4", handle: "sed -n 4p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "13", handle: "sed -n 13p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "46", handle: "sed -n 46p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md; and sed -n 46p docs/superpowers/specs/2026-10-29-lodge-design.md"}
  - {value: "96", handle: "sed -n 96p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
  - {value: "90", handle: "sed -n 90p docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"}
---

A thread closed without text gets a closing message with an empty text, shown as "closed by" its writer, never as words of the author's.
The dependency view places each entry's dependants directly after it, so an indented entry always sits under one it rests on.
A thread is not a kind of knowledge that s-7ah5n7 puts out of scope; the build adds that sentence to the entry and does not wait.
Nothing goes to the author.

## Reasoning

The findings are I13, I14, and the s-7ah5n7 part of I11 in `docs/superpowers/plans/2026-10-31-lodge-viewer/plan-review-correctness.md`; the exact plan changes are in `docs/superpowers/plans/2026-10-31-lodge-viewer/advisor-ruling-2.md`.
"Design N" is a line of `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`.

Closing without text (I13):
The default text "Closed." was the advisor's own addition (design 85, d-7w5aq0), so it yields to her decisions.
LODGE-8 (d-9vxkjw) says only her quotes are her text, and must-not 2 (design 45) and design 81 say the viewer never records words she did not type; a `by: author` message reading "Closed." breaks both.
Who closed the thread and when, the point of design 85, survives in the closing message's `by`, `when`, and `where`.
Check 1 allows an empty text only on the last message of a closed thread, and check 5 refuses a thread closed without a new message, since reads take that last message as the close and would otherwise credit it wrongly (s-q4s548).
Cost if wrong: the thread file format, before any thread exists.

Dependency indent (I14):
Her words on the arrangement are "Easily see and understand dependencies between points." (design 15); an indent that reads as resting on the wrong entry defeats that and shows wrong information (s-q4s548).
The tie rule is the design's own agent call (design 118, marked as such) and so is the indent rule (design 120, agent text by design 4), so the advisor may choose between them.
A depth-first order keeps both visible promises, every entry after what it rests on and each indented under an entry it rests on, and changes only ties into siblings in the area's order.
An entry resting on two entries of its area gets a line naming the one the indent does not show.
Cost if wrong: one function in `core`, one test file, and a different valid order.

Threads and s-7ah5n7 (I11):
She asked for threads herself, "A chat on it would be ideal that can then directly interact with it" (design 13, 2026-10-30), a day after the non-goal (`docs/superpowers/specs/2026-10-29-lodge-design.md:46`).
That non-goal's reason is that a new kind of knowledge must first be evaluated; a thread holds no claim that holds now, and what it settles enters lodge only as a decision (design 46 and 96), while search and the timeline leave threads out (design 90).
"Conversation logs as provenance" means session transcripts, kept out because they are not always available (d-pf8xm9); a thread lives in the repository and is named as a handle, as a file is.
The entry's decision d-cg3nn3 is a coordinator's, already narrowed by d-dyrpc6, so editing the entry narrows no author decision and keeps it from reading against s-a67fqm's three record kinds.
Cost if wrong: one decision undoes the sentence; threads exist because she asked for them, so nothing is rebuilt.

It replaces and narrows nothing: d-7w5aq0 said closing appends a message from the closer, which stays, and fixed no default text in its own record; d-z727gh and d-18terz concern author records and levels, which this leaves as they are.
