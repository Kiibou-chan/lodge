# Plan recheck 3: plan 4, the importer, the export, and the design's records

Rechecked: fix round 3b81af1..1946379 on `server-import`, against `plan-fix-3.md`, plan 2 at `origin/server-store` a035344 (Task 12c), and d-2v8vtk.
Status: done.

Counts: 5 of 5 claims hold; new: 0 Blocking, 0 Important, 1 Minor.

## Claims

### The import's messages go through the owner's store and never meet the hold · Holds

Plan 2's Task 12c lists as its Files `ts/src/app/threads.ts`, `ts/src/app/held.ts`, and `ts/src/app/results.ts`, with `ports.test.ts` and new tests (plan 2 at a035344, Task 12c, "Files"); `Store.publish` and both stores are not among them.
The hold is placed only in `ask`, `reply`, and `close` from an agent actor with a `by` in `people` (Task 12c, "Interfaces", third item), which call `store.hold` instead of publishing.
Plan 4 Task 5 writes the mapped thread files with one `store.publish` of `projects.storeFor(project, person(owner))`, the requester being that owner (plan lines 326 to 331), so no hold is on its path; plan line 86 and Task 5's note now say so with d-2v8vtk.

### The export wrapper passes `hold`, `held`, and `decline` through, and an approving publish tells the exporter · Holds

Plan line 387: the store's `Proxy` intercepts only `publish`, calling `written(project)` after any `PUBLISHED` answer, `approves` included, and forwards `hold`, `held`, and `decline` bound to the inner store.
Plan 2's approval of a held add or message publishes through `publish` with `approves` = `seq` (Task 12c, `approve(seq)` of a `HeldMessage`; Task 12b for an add), through the store `Lodge` holds, which Task 8 builds over the wrapped `ApiOptions.projects` (plan line 436), so the approval reaches the exporter.
`Store.hold(held: HeldDraft)` with `HeldDraft = HeldAdd | HeldMessage` (plan 2 at a035344, lines 108 and 125) is a Task 12a name, which the `Proxy` forwards without naming its type.

### No plan 4 task needs Task 12b or 12c · Holds

Task 6 reads `trees`, `attachmentTexts`, `publish` with `approves`, `hold`, `held`, and `decline` (Task 12a's port, plan 2 lines 107 to 110 and 581 to 586) and waits for 12a (plan line 100); Task 5 reads `trees`, `publish`, `members`, and `storeFor` and waits for plan 2's Task 11 (line 99); Task 8 waits for all of plans 2 and 3 (line 102).
`grep -n '12b\|12c'` on the plan finds only line 86's citation of Task 12c and line 387's "Tasks 12a to 12c", neither a wait.

### Task 7's migration note · Holds

Plan line 409: Task 7 adds no migration; plan 2's Task 12a's `MIGRATIONS[1]` creates `held(… at text not null …)` and raises `user_version` to 2 (plan 2 at a035344, Task 12a, its `MIGRATIONS[1]` item), so a later one would be `MIGRATIONS[2]`.

### No d-x6vaw8 citation left · Holds

The two remaining mentions name it only as what d-2v8vtk replaces: plan line 86 ("d-2v8vtk, the author's, replacing d-x6vaw8") and the ledger's alignment line (`…-progress.md:19`).
d-2v8vtk is on `server-store` with `decided_by: author`, her quote, and `replaces: [d-x6vaw8]`.

## New findings

### N3-M1 · Minor · the ledger's alignment line still names plan 3 at 7dfdf40, and a comma is missing

Handle: `…-progress.md:19` ("plan 3 at 7dfdf40 (`origin/server-api`)"), against plan line 17 ("plan 3 at `origin/server-api` 9988813"); recheck 2's N2-M1 fix asked for both lines.
The same line reads "are not held and whose `Store.attachmentTexts()` serves the export", where the list of `whose` clauses needs a comma before `and`.
Failure: a coordinator reading the ledger checks plan 3's names at the older commit; nothing consumed differs (recheck 2), so only the pointer is stale.
Fix: name 9988813 there, and write "are not held, and whose".

## Files read

`plan-fix-3.md`; `git diff 3b81af1 1946379` (plan and ledger); plan 2 at a035344, Task 12c in full, "Interfaces for plans 3 and 4" (lines 100 to 194 by grep), Task 12a's Files and `MIGRATIONS[1]`; d-2v8vtk's header on `server-store`.
