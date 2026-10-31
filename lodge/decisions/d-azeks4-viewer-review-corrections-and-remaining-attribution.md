---
id: d-azeks4
kind: decision
title: "Viewer review corrections and remaining attribution dependency"
scope: product
decided_by: coordinator
date: 2026-10-31T03:46:21+01:00
changes:
  - {entry: s-2bzwzv, action: edit}
  - {entry: s-mc9n8a, action: edit}
  - {entry: s-r7c3wn, action: edit}
  - {entry: s-j5ttw1, action: link}
narrows: [d-vme42w, d-x42f0x]
numbers:
  - {value: "25", handle: "docs/superpowers/plans/2026-10-31-lodge-viewer.md, Calls made, Call 25"}
  - {value: "3", handle: "docs/superpowers/plans/2026-10-31-lodge-viewer.md, Task 3"}
  - {value: "8", handle: "docs/superpowers/plans/2026-10-31-lodge-viewer.md, Task 8"}
---

The viewer writes author confirmations and threads, dependency indentation follows the last same-area dependency placed, and the commit and doubt descriptions match the implemented safeguards.

## Reasoning

d-vme42w and d-x42f0x are narrowed only in their read-only claims: s-dm37qr, s-582qav, and d-h3v99q now provide author confirmations and threads.
d-2hcgav still holds because editing remains later; d-x42f0x's local operation, command-line start, and listed reads still hold.
s-2bzwzv follows d-a3h9f3: the last same-area dependency placed makes an entry ready, so its indentation shows a real dependency.
s-mc9n8a follows Call 25 of the viewer plan: an unfinished revert or stopped sequence is unsafe for a viewer commit as well as a merge, rebase, or cherry-pick.
s-r7c3wn distinguishes entries changed by the doubted decision from entries resting on them, as the plan's Task 3 and the implemented marks do.
s-j5ttw1 rests on s-aq3a5k because trusting and displaying the author label relies on that label's defined meaning; this closes the deferred Task 8 link.
The model and writing introductions now count threads and the dependency check, matching their current entries.
These are coordinator corrections of descriptions, not changes to the author's intent.
