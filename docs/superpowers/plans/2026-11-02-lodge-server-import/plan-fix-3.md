# Plan fix round 3: plan 4, the importer, the export, and the design's records

Planner, fix round 3, on `server-import` from 3b81af1, aligning with plan 2's fix round 3 at `origin/server-store` a035344 (Task 12c) and the author's answer to STORE-1 (d-2v8vtk, replacing d-x6vaw8).
Status: done.

## Changes

- The import's thread messages are not held: Task 12c changes `ask`, `reply`, and `close` (`ts/src/app/threads.ts`), `held.ts`, and `results.ts`, and leaves `Store.publish` as Task 12a has it, holding nothing; the import publishes its mapped thread files with one `publish` of the owner's own store, the owner signed in as the requester (Task 5), so it never meets the hold. The plan's note under "Names this plan consumes" and Task 5's `importStore` say so and cite d-2v8vtk where they cited d-x6vaw8.
- The export wrapper: Task 6 says `hold`, `held`, and `decline` pass through unchanged whatever the hold's kind, and that an approving `publish` (an approved add or relayed message) tells the exporter like any other `PUBLISHED` answer.
- Migrations: Task 7 adds an event kind, no migration and no derived table; it now says that a later migration of this plan would be `MIGRATIONS[2]` or later, since plan 2's `MIGRATIONS[1]` creates `held` with `at`.
- Waits: Task 6 uses `Store.trees`, `attachmentTexts`, and `publish` with `approves`, and passes `hold`, `held`, and `decline` through, all of Task 12a's port; it uses nothing of 12b (`Approved`, `AddOutcome.HELD`) or 12c (`Written.awaits` and `held`), so it still waits for 12a only; Task 5 uses `trees`, `publish`, `members`, and `storeFor`, none from 12b or 12c; Task 8 waits for all of plans 2 and 3.
- "Aligned against" and the ledger's alignment line name plan 2 at a035344.

## Names from plans 2 and 3

No name this plan consumes changed: `HeldDraft` becoming `HeldAdd | HeldMessage`, `Approved`, `Written.awaits` and `held`, and the holds' new words are plan 3's names, not plan 4's; plan 3's round 4 (the approval page's held messages) touches no name in plan 4's table.
