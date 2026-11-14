# Plan fix round 2: plan 2, the events store and the operations

Planner, fix round 2, on `server-store` from d3ce2fd, answering the new findings of `plan-recheck-1.md` (0 Blocking, 1 Important, 4 Minor).
Status: done.

## Ruling recorded

- d-j28rp0 (replaces d-pmaw3a): the same refusals in `publish`, with the reasoning's claim narrowed to "no write of `app` changes a decision's fields"; a decision added back with no field changed but another rendering is refused, which it accepts, since nothing is lost and comparing parsed fields belongs to the core's check, not the adapter (N-2).

## Findings

- N-1 (Important, `held.ts` and `writes.ts` import each other): fixed in Task 12b: who an add awaits moves to a new `ts/src/app/awaits.ts`, listed under Create, which imports neither; `writes.ts` imports `awaits.ts`, `held.ts` imports `writes.ts`, and the Interfaces state the edges `held.ts → writes.ts → awaits.ts` against plan 1's `no-circular` rule; the lane waits are unchanged.
- N-2 (d-pmaw3a's claim too broad): ruled d-j28rp0, replacing d-pmaw3a, its text corrected and the re-render case named with its cost; the plan cites d-j28rp0 throughout; Task 7b's `rebuild_gives_the_same_tables` rewrites an entry, and `a_published_decision_is_never_rewritten` says a re-rendered decision with the same fields is refused too.
- N-3 (the `where` refusal fires before `Forbidden`): fixed in Task 11: `an_agent_cannot_write_as_a_person` gives each call `where: "chat"`.
- N-4 (ledger line 18): rewritten in place: STORE-1 waits for the author in `questions.md` (d-x6vaw8); the ledger's ruling line for the store's refusals now names d-j28rp0.
- N-5 (Task 10's grep matches the definitions): fixed in Task 10 Step 3: the only lines without `people` are the definitions of `isAuthor`, `parseThread`, `writeThread`, and `tree`.

## For plans 3 and 4

- The store's refusal decision is now d-j28rp0; its rules are unchanged, so nothing plans 3 and 4 consume changes; plan 4 may note that an imported decision added back unchanged is refused when lodge's rendering differs from the imported text.
