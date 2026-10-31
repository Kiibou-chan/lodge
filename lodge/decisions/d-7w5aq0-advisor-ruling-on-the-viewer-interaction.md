---
id: d-7w5aq0
kind: decision
title: "Advisor ruling on the viewer interaction design: its calls kept, three changed, gaps filled"
scope: process
decided_by: advisor
date: 2026-10-31T01:01:12+01:00
work_item: "docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md"
numbers:
  - {value: "4", handle: "entries under lodge/spec/ whose body names another entry's ID: s-dm37qr, s-hfjr1m, s-m83kjq, s-582qav"}
  - {value: "25", handle: "decisions under lodge/decisions/ with a changes list; all scope product, none spanning two areas"}
  - {value: "17", handle: "the design's earlier count, of entries naming a record by ID or LODGE code"}
---

The viewer interaction design may be planned and built with its agent calls kept, except three, which change: a confirmation's scope, `--when` on an author message from the command line, and a shared area rank, now feedback rather than a failing check.
The advisor also filled gaps a build would trip on, each marked [advisor] in the design and listed in its ruling file.
Nothing is left to the author before planning, and every mark is hers to check.

## Reasoning

Handles are files under `src/lodge/`, record IDs, or commands; the full table is `docs/superpowers/plans/2026-10-31-lodge-viewer/advisor-ruling.md`.

Kept:
The live chat stays a non-goal: the viewer's policy forbids scripts (`viewer/server.py`, POLICY), lodge is a command for cloud sessions (d-14vk9b), and the thread format is what a chat would write, so adding one later rebuilds nothing.
The generated title and statement of a confirmation stay lodge's, in the third person, so only the quote and reasoning are her text (LODGE-8, d-9vxkjw); must-not 1 now says so, where it had claimed the record holds only her words.
Committing viewer writes by path without pushing stays, and so does not committing on the base branch or a detached HEAD: `CheckoutStore.publish` only stages (`gitstore/checkout.py`), and `main` takes only merges (CLAUDE.md, Git).
Threads as a record kind under `lodge/threads/`, append-only messages, agents opening and closing threads, and `where: "lodge viewer"` all stay; her "Me, you, both" names agents as actors.
A doubt on a decision marking the entries it changed stays, since she reads on the specification and a doubt invisible there would read as more settled than it is (s-q4s548).
Agents closing a thread only on her ask stays, as it keeps the change with a decision (must-not 3).
`rests_on` on entries only stays: her words are about points resting on points, and decisions already link to entries through `changes`.
The `link` action, exempt from the review flag and from "changed since", stays: without it the migration of the existing entries floods `lodge waiting` and clears the very warning the links exist for (builder check, question 6); the links still go to her in the task report.
The cycle check, the derived reading order, the token, the whole-`Host` match, and refusing a write without `Origin` stay; a wrong guess in any of them is a local rule change, not a rebuild.

Changed:
A confirmation's scope was that of the first listed decision, which depends on list order; it is now `product` when any listed decision is, else `process`.
An author message from the command line needs `--when` as well as `--where`, as an author quote has both (Check 3, s-yhppm5); otherwise the time of a quoted message would be the time it was typed in, which is wrong information.
Two areas sharing a rank were to fail check 7; a shared rank misleads no one, and lodge gives feedback rather than refusing where nothing is wrong (d-c6n1ng), so they are ordered by name with feedback.

Added, because a build would trip on them:
The Security section said the viewer never edits an existing record file, while replies and closing append to one; it now says the viewer never edits a decision, entry, or area file and only appends to threads.
The area form lists the entries each decision changes, in any area, and carries the IDs it listed, so she confirms exactly what she saw even if an agent adds a decision meanwhile; a confirmed decision counts as hers for the review flag (LODGE-6, d-8nkamy), so what she confirms has consequences.
A write answers with a redirect, so a reload does not write a second author record.
The commit leaves other staged files staged, uses the checkout's identity, and is skipped during a merge, rebase, or cherry-pick, where a partial commit fails.
A thread's `about` names a decision or an entry.
Check 5 extends to threads, so a hand edit of her message fails the gate as a hand edit of a decision does (s-ms14fq).
Closing appends a message from the closer, so a closed thread shows who closed it.
`lodge waiting` gets two groups, since it was the author's list (s-0s9m2d) and now agents read it too.
Search and the timeline leave threads out, as `Record` holds decisions and entries (`core/model.py`).
A decision listing an entry with `edit`, its text unchanged, clears "changed since", which check 4 already allows (`core/check_entries.py`, `check_entries`).
The viewer opens on the dependency order, as `lodge spec` prints.
The token is compared in constant time.
The design's count of entries naming another record was 17, but only 4 name another entry, which is what `rests_on` can hold.
The process consequences now list the specification entries that the design contradicts, among them s-j5ttw1, whose "There is no confirmation step" would read against confirming.
