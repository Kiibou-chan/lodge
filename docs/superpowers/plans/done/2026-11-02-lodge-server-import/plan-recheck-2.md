# Plan recheck 2: plan 4, the importer, the export, and the design's records

Rechecked: fix round c87247d..91b08e3 on `server-import`, against `plan-recheck-1.md` and `plan-fix-2.md`.
Plan 3 compared from `origin/server-api` 7dfdf40 to 9988813.
Status: done.

Counts: 4 of 4 resolved (N-I1, N-M1, N-M2, N-M3); new: 0 Blocking, 0 Important, 2 Minor.

## Findings of recheck 1

### N-I1 · Resolved

Task 6's `wrapped_projects_pass_every_method_with_its_arguments` now calls `members`, `addMember`, and `create` "with the arguments plan 2's `Projects` declares" and leaves `create`'s third argument to Task 8's `project_settings_survive_the_wrapper` (plan line 390, diff of 91b08e3).
That matches plan 2 at 5307e56 (`create(project, owner)`, `members(project)`, `addMember(project, person, role, by)`), so the three calls compile in Task 6's lane, and Task 8's test (plan line 445) still covers the settings once plan 3 is merged.

### N-M1 · Resolved

Plan lines 25 and 475 cite d-d0vca9, line 25 noting that it replaces d-4zg8q3; `lodge/decisions/d-d0vca9-the-file-writing-rule-matches-fs.md` exists on `origin/server-core`.

### N-M2 · Resolved

The ledger's line for d-sdpcyb (`…-progress.md:8`) notes that its reasoning cites d-pmaw3a, which plan 2 replaced by d-j28rp0, narrowed by d-n9nm8h, with the same refusals.

### N-M3 · Resolved

Plan line 441 names `world.ts`'s `FixedClock` and `server.ts`'s plan 3 `TestClock`, as plan 3 at 9988813 declares them (Task 5's `world.ts`, Task 7a's `TestClock`).

## Plan 3 from 7dfdf40 to 9988813

The plan 3 diff (`git diff 7dfdf40 9988813 -- docs/superpowers/plans/2026-11-02-lodge-server-api.md`) changes citations (d-4zg8q3 to d-d0vca9, d-pmaw3a to d-j28rp0), `AgentToken.id`'s comment (`tokenId`), the `check` operation's `gate` passed positionally, Task 6's consumption of `recordFromDraft` and the `held` operation's draft shape, the guide's line 24 clause, the `tests/test_wheel.py` parity row, and the knip note on plan 4's table.
None of these is a name plan 4 consumes: `ApiOptions` (with `projects`, `lodgeFor`, `clock`, `log`), `lodgesOver`, `Projects.create`, `settings`, `names`, `Io`, `run`, `readSettings`, `CliError`, `hook_is_left_alone`, the help tests, `world.ts`, `server.ts`, and `main.ts`'s `open(data)` are unchanged.

## New findings

### N2-M1 · Minor · "Aligned against" still names plan 3 at 7dfdf40

Handle: plan line 17 (`plan 3 at origin/server-api 7dfdf40 (after its fix round 1)`); `plan-fix-2.md` says it aligned with 57c582c, and plan 3 is now at 9988813.
Failure: a coordinator checking the consumed names against plan 3 reads the older commit; nothing consumed differs (above), so only the pointer is stale.
Fix: name 9988813 (after its fix round 3) on line 17, and in the ledger's alignment line.

### N2-M2 · Minor · the ledger's line for d-sdpcyb closes a parenthesis twice

Handle: `…-progress.md:8`, ending `probe 9); its reasoning cites d-pmaw3a, … with the same refusals).`; the opening `(d-sdpcyb,` is closed at `probe 9)`, so the last `)` has no partner.
Fix: drop the last `)`, or turn `); its reasoning` into `; its reasoning`.

## Files read

`plan-fix-2.md`; `git diff c87247d 91b08e3` (the plan and its ledger); `git diff 7dfdf40 9988813` of plan 3's plan file, and its log; `git ls-tree origin/server-core lodge/decisions` for d-d0vca9.
