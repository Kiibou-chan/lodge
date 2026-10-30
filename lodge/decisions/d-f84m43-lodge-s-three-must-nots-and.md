---
id: d-f84m43
kind: decision
title: "lodge's three must-nots and how the design answers each are entries"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:15+01:00
changes:
  - {entry: s-q4s548, action: create}
  - {entry: s-pncjp8, action: create}
  - {entry: s-4ykcm0, action: create}
---

The three things lodge must not do are specification entries: show wrong information, let an agent quietly rewrite the author's decision, and become a costly third copy. Each entry carries how the design answers it.

## Reasoning

The author named the tool showing wrong information as the clearest must-not, and said the others would also not be good.

The answer to the first is that every Level 1 view carries who decided, the status, and any open review flag, because a short entry could otherwise read as more settled than it is.

The reads and the viewer use the same parser and check as the gate, so a record that fails the check is shown as failing, and derived facts are computed rather than typed by hand, so they cannot drift from the files.

The answer to the second is that decisions are never rewritten, and an agent decision that touches something the author decided is flagged until she confirms it; the review flag is described in the writing area.

The answer to the third is that the old files are frozen after the pilot and then retired, the readable specification is generated rather than committed, and no link is stored in two places.

Upkeep cost is itself a success measure, so the third must-not is measured.
