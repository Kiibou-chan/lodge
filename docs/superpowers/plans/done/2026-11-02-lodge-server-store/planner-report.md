# Planner report: plan 2, the events store and the operations

Status: done; plan written, self-reviewed, and aligned with the drafts of plans 3 and 4; twelve rulings recorded.

## Done

- Read the brief, plan 1 (Global Constraints, Calls made, the rest of build step 1, Settled for the later plans, the parity table), its ledger, the design, `src/lodge/app`, `tests/app`, and `tests/gitstore/test_concurrent.py`.
- Probes 1 to 8 (`probes.md`): a `text` column loses a leading U+FEFF and corrupts lone surrogates, so file texts go in `blob`s; Kysely serialises transactions on one connection; a read-then-write transaction across two connections fails, a compare-and-set first statement does not; the app's default-filling functions; an edit of a decision through `add` is refused by check 5.
- First draft: 14 tasks, lanes A (app, Tasks 2 to 6), B (store, Tasks 7 and 8), and C (core people and flags, Tasks 10 and 13).

## Rulings

d-59q4jc (asynchronous ports), d-ae1vn5 (the port's shape), d-wje1cn (events and the compare-and-set), d-vd3175 (options objects), d-t7er56 (lanes), d-rp74dr (thread fix paths), d-kj59bz (people), d-znagqe (held drafts), d-4spcem (flags per person), d-fv20kp (the check on every write), d-wx7d0f (projects), d-pprhpz (the import checks itself, narrowing d-fv20kp); `lodge check` ok.

## Shape

15 tasks: 1 (setup, coordinator); lane A 2 to 6 (app at parity); lane B 7a, 7b, 8 (store), after Task 2 (7b after Task 3); lane C 10, 13 (people and flags in the core), after Task 1; then 9 (after 4 and 8), 11 (after 6, 8, 10), 12 (after 9 and 11), 14 (closing).
Self-review: Task 7 split into 7a and 7b for size; the after-state's `tree()` note corrected; a raw U+2212 removed.

## For the coordinator (alignment with plans 3 and 4)

- Plan 3 (f2dcc72) plans its own `project-created` event and project list in its Task 4, while plan 2 has `Projects.create` and a `project` event (d-wx7d0f); its ledger alignment should consume plan 2's.
- Plan 3 approves by a decision ID (`approve(project, id)`); plan 2 holds a drafted add under the number of its `held` event and mints the decision's ID at approval (d-znagqe), so plan 3's `approve` and `drafted` take that number.
- Plan 3's hand edits (RULE-E2E) can write through `Store.publish`, which runs no check (d-pprhpz).
- Plan 4 (34c12f1) says its import writes "through plan 2's check on every write"; `publish` has no check, and plan 4's own state check (d-ag8p8h) is what checks the import (d-pprhpz).
- Plan 4's export reads attachment texts: `Store.attachmentTexts()` was added for it.
- Plan 4's codec names (`decodeStored`, `encodeStored`) differ from plan 2's `decodeUtf8` and `encodeUtf8` of `text.ts`; its d-ryss91 already defers to plan 2's.

## Open

- Nothing for the author: no value trade-off, so no `questions.md`.

## Concerns

- The parity table marks only two app test files as changed, but four more carried files test the staged mode, commits, and the labelled gate (`tests/app/test_reads.py:149-195`, `test_confirm.py:90-178`, `test_thread_ops.py:163-181`, `test_writes.py:126-136`, `test_writes_dates.py:50-54`); the plan keeps the port's shape so they carry unchanged over the fakes (RULING-PORT).
- `tests/app/test_thread_fix_paths.py` imports the command (`lodge.cli`), which plan 3 ports; two of its tests wait for plan 3 (RULING-FIXPATHS).
