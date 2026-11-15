---
id: d-b7328n
kind: decision
title: "The held answer carries each draft's full text and its attachments"
scope: process
decided_by: server-api-task
date: 2026-11-15T02:40:29+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-api.md"
---

The `held` operation of the person's API adds, to every draft it lists, the draft's own text as `text`, and to a held add its attachments as `attachments`, a list of `{name, text}` pairs.
The typed fields (`title`, `statement`, `quote`) stay as the plan prescribes, so a page that reads only them is unchanged.

## Reasoning

The plan's shape (the plan's person's operations) gives a decision's `{name, kind, title, statement, quote}`, which leaves out `changes`, `scope`, `replaces`, `narrows`, `confirms`, `numbers`, the reasoning, and the attachments (the final review's Important finding, `ts/src/api/person.ts:21-46`; a scratch test in which an agent's held decision carried `replaces`, reasoning, and an attachment returned none of them).
Approval publishes all of that in the person's name, and d-zzfmj2 says a person's decision becomes current when that person approves it, which a person cannot do knowingly over fields they never saw.
The author put the interaction in the UI to "a later point" (d-zzfmj2's quote), so which fields the page presents stays open; sending the raw text commits to nothing and lets the later page choose.
An added field is read by no existing consumer, so no name another plan consumes changes.
Cost if wrong: the later interface wants a typed shape instead, and the raw text is dropped from the answer in that step.
