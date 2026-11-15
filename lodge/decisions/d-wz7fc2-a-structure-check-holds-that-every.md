---
id: d-wz7fc2
kind: decision
title: "A structure check holds that every people-aware core call passes the snapshot's people"
scope: process
decided_by: coordinator
date: 2026-11-14T22:23:36+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "10", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/task-10-review.md, finding C-I1 (ten reversion sites)"}
  - {value: "11", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store.md, heading `### Task 11`, Step 3"}
---

Once Task 11 has passed `people` at every call in `app`, `ts/tests/structure/calls.ts` fails any call of `isAuthor`, `parseThread`, or `writeThread` under `ts/src` outside `core` that passes fewer than two arguments, so the grep of Task 11's Step 3 becomes a test.

## Reasoning

The Task 10 review (D-M1 and C-I1 of `task-10-review.md`) shows that the defaulted parameter `people = AUTHOR_ONLY` at `ts/src/core/derive.ts:158` and `ts/src/core/threads.ts:28` and `:116` lets a later call compile without `people`, and every carried test runs over `{author}` and passes, so a project whose person is `ada` would read `ada` as an agent without any test failing.
The defaults are the plan's (d-d96y91), so lane A's one-argument `writeThread` call compiles until Task 11 replaces it.
The rule adds a check and loosens nothing: no limit is raised and no import edge is allowed.
Cost if wrong: a legitimate one-argument call, such as a test of the default, needs a narrower rule, a small edit to `calls.ts`.
