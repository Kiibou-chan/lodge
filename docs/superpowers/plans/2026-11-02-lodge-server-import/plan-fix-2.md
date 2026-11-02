# Plan fix round 2: plan 4, the importer, the export, and the design's records

Planner, fix round 2, on `server-import` from c87247d, answering `plan-recheck-1.md` (0 Blocking, 1 Important, 3 Minor), aligned with plan 3 at `origin/server-api` 57c582c.
Status: done.

## Findings

- N-I1 (fixed): Task 6's `wrapped_projects_pass_every_method_with_its_arguments` calls `members`, `addMember`, and `create` with the arguments plan 2's `Projects` declares; `create`'s settings argument is left to Task 8's `project_settings_survive_the_wrapper`, which runs after plan 3 merges.
- N-M1 (fixed): the Global Constraint on the file-writing rule and Task 9's `main.ts` line cite d-d0vca9, which replaces d-4zg8q3.
- N-M2 (fixed): the ledger's line for d-sdpcyb notes that its reasoning cites d-pmaw3a, now d-j28rp0 (narrowed by d-n9nm8h), with the same refusals.
- N-M3 (fixed): Task 8 says `world.ts` has plan 2's `FixedClock` and the e2e `server.ts` plan 3's `TestClock`.

## Alignment with plan 3 at 57c582c

Plan 3's fix round 2 changes no name this plan consumes: `recordFromDraft` is newly consumed by plan 3's Task 6 and not by this plan; `check(gate)`, `tokenId`, the guide's line 24 clause, and the `tests/test_wheel.py` parity row are not this plan's; its citations of d-pmaw3a and d-4zg8q3 became d-j28rp0 and d-d0vca9, as this plan's now are.
