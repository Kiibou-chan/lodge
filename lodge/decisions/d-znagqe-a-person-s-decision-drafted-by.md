---
id: d-znagqe
kind: decision
title: "A person's decision drafted by anyone else is held whole until that person approves or declines it"
scope: process
decided_by: planner
date: 2026-11-02T19:05:49+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "3", handle: "s-yhppm5, its title"}
---

An add whose new decisions name in `decided_by` a person other than the actor is checked and then held whole as a `held` event, not published: it answers `HELD`, its decision is not current, and `held()` lists it; that person's `approve` runs the add again as them, dated at the approval, publishing the files and the approval in one transaction, and their `decline` with a reason drops it; an add naming two such persons is refused.

## Reasoning

SRV-2 (d-zzfmj2): a session drafts the person's decision with their quote, the draft waits in their waiting list, and it becomes current when they approve it (design, "The model").
Holding the whole add keeps s-8m99ba, a decision added with the entries it changes; holding only after the check passes means a draft without the person's quote never reaches them (check 3, s-yhppm5).
Running the add again at the approval checks it against the state it then lands on (d-fv20kp).
The design names no way to drop a draft, but without one a draft the person will never approve stays in their waiting list for good (design, "The waiting list"); she left the interface of approving open (design, "Open"), so this decides the operations only.
One person a hold keeps the waiting list a person's own; a session splits a two-person add into two.
Cost if wrong: a held event keeps the drafts whole, so another way of approving reads the same holds.
