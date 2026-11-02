# Plan recheck 1: plan 4, the importer, the export, and the design's records

Rechecked: fix round ae2db4e..8d995b5 on `server-import`, against `plan-review-correctness.md`, `plan-review-practice.md`, `plan-fix-1.md`, `probes.md`, and `questions.md`.
Names checked against plan 1 at `origin/server-core` 9e133ea, plan 2 at `origin/server-store` 5307e56, and plan 3 at `origin/server-api` 7dfdf40.
Probes ran in a detached scratch worktree at 8d995b5 under `/var/tmp`, removed afterwards.
Status: done.

Counts: Blocking 2 of 2 resolved; Important 15 of 15 resolved; Minors as claimed, with one claim (P4-I5's test) carrying a new Important.
New: 0 Blocking, 1 Important, 3 Minor.

## Blocking

### B-1 and P4-B1 · Resolved

Task 1 Step 2 calls `checkState(after)` with one argument and adds `checkChange` from an empty state (plan line 152).
Task 5 checks both stages with `checkChange(empty, …, settings, now)` (lines 315 and 320), `prepareImport` taking `now` and `importStore` a `Clock` (lines 310 and 311).
`checkChange(published, after, settings, now: string, current = null)` exists with that signature (`ts/src/core/check-change.ts:18-24` on `server-core`), and it runs `checkState(after)` inside it (line 28), so check 3 of the server stage holds; its `dates` gives check 1 for a decision dated after `now` before the `importedFrom` skip (lines 70-71), so the imported d-40q44p, dated 2026-01-05, is correctly absent from `store_dated_after_now_is_refused`.
The replaced tests now expect what a change check gives: `failing_store_prepares_nothing` check 4 at `"lodge 0.2"`, `mapped_state_is_checked_with_the_project_settings` check 4 at `"server"`, `owner_name_used_as_a_role_fails_the_server_check` check 3 (plan line 334), Task 8's `failing_store_answers_check_failed` and `project_without_the_sources_answers_check_failed` (line 445).
Probe 9 re-run: `check-change-empty.py` on the made-up store prints `files 10 state problems 0` and `change problems 0 {}`.
d-sdpcyb replaces d-ag8p8h and d-y42b7b; each argument has a handle (`check-state.ts:133`, `check_entries.py:73-84`, `branch.py:169`, probe 9, design lines 75, 79, 289, 304); one handle is stale (new Minor N-M2).
Plan 2's d-j28rp0 is narrowed to match by d-n9nm8h at 5307e56.

## Important

### I-1 and P4-I9 · Resolved

`readStore(repository, rev, settingsRev?)` (plan line 181), `zeroTwoRepository` returning `settingsRev` (line 197), `reads_the_branch_layout` passing it and `branch_layout_without_a_settings_revision_has_no_settings` new (line 201), Task 8's `import` taking `settingsRev` (line 438), and `branch_layout_without_its_settings_fails_check_4` (line 445).

### I-2 · Resolved

Probe 7 is rewritten in place with the outputs the review measured (`probes.md:34-39`): the thread's `problem:` line, the heading losing `· question open`, `lodge waiting` printing `nothing`, and `--gate` noting rather than failing.
IMP-1 is answered A (d-b61590, `decided_by: author`, with her quote), so the inaccurate wording no longer steers a ruling; `questions.md` marks it answered.

### I-3 · Resolved, differently but adequately

d-b61590 removes the requirement that lodge 0.2 read the export cleanly, and the plan now reads design line 284 as file layout only (plan lines 58-59).
Task 10's script compares files and runs no lodge 0.2 command on the export (line 499), so the 69 spurious check 4 problems cannot appear in its report; the project is created with the store's `[length]` and `[import]` tables (line 498).

### I-4 and P4-I5 · Resolved in the code, with a new Important in the test (N-I1)

`exportingProjects` is a `Proxy` forwarding every member but `storeFor` bound to the inner object (plan line 387, d-v0r9cb), so `create`'s third argument and plan 3's `settings` and `names` pass without an edit, and Task 8 no longer edits `exporting.ts` (line 436).
`importStore` takes `Pick<Projects, "members" | "storeFor">` (line 311), so its stand-in survives plan 3's merge.
Task 8's `project_settings_survive_the_wrapper` (line 445) checks the settings through the wrapper once plan 3 is merged.
d-v0r9cb's arguments have handles (plan 3 at 3e4c29c, Task 4; the review's `tsc` run).

### P4-I1 · Resolved by d-4zg8q3, now d-d0vca9

`#hook`'s `run` takes `out` (plan line 266); the rule change is plan 1's (Global Constraint, line 25), and `ExportPorts.write` is a method on a receiver that is not `Bun.file(…)`, which the narrowed rule does not report.
The plan cites d-4zg8q3, which the coordinator has replaced by d-d0vca9 (N-M1).

### P4-I2 · Resolved

`attempt` builds `{ ...process.env, LC_ALL: "C", GIT_TERMINAL_PROMPT: "0", ...env }` at each call (plan line 187); every helper runs git through `#git` (lines 35, 196, 476); `isolation_reaches_git` is new with a named mutation (line 200).
Re-run: `bun probes/spawn-env.ts` prints `no env: [] explicit env: [mutated]`.

### P4-I3 · Resolved

`missing_git_is_one_sentence` empties `PATH` to a folder (line 200).
Re-run: `bun probes/spawn-sync.ts <empty folder>` prints `"" exit 0` and `"<folder>" threw ENOENT Executable not found in $PATH: "git"`.

### P4-I4 · Resolved

`ts/tests/app/front-door.test.ts` is in the Files of Tasks 4, 5, and 6 (lines 249, 289, 345) and in the lanes' merge list (line 108); Task 4 waits for plan 2's Task 6 (line 98), which creates that test (plan 2 at 5307e56, line 343).

### P4-I6 · Resolved

"the eight files … named by path" (line 334) and "one publish of the eight files" (line 335); `probes/zero-two-store/lodge/` holds ten files, two of them `.gitkeep`.

### P4-I7 · Resolved

`riggedRemote` carries `rigged_remote` of `tests/gitstore/test_push_race.py:35-57` into `repos.ts` (line 236) and `moved_remote_branch_answers_moved` uses it (line 238); the untested local race is stated with its reason (line 239).

### P4-I8 · Resolved

Task 2's `repos.ts` carries `git`, `commit`, and `write` only (line 196); Task 3 adds the rest and lists `repos.ts` under Modify (line 212).

### P4-I10 · Resolved

The split into `post-tool-use.test.ts` and `moved-advice.test.ts` (line 250), the parity row naming the carried file (line 127), and Task 10's name check reading only it (line 497).

### P4-I11 · Resolved

Global Constraint line 24 makes every spawn `Bun.spawnSync`; Task 2's `run.ts` is synchronous (lines 168-174), `readStore` and `exportStore` keep a `Promise` shape for their ports (line 189); no `Bun.spawn(`, `Bun.$`, or `child_process` remains in the plan (grep).
Re-run: the child's three streams are `memfd:spawn_stdio_stdin`, `…stdout`, `…stderr`.
`differential.test.ts:15,43,61` on `server-core` uses `Bun.spawnSync`, and `task-12-report.md:30` there reports its passing run.

## Minor (claims of `plan-fix-1.md` only)

- Correctness M-1 and P4-M6: `initialise()` stages with `git add --` (line 476). Holds.
- Correctness M-2: Task 4's test-local `resolve` resolves the longest existing prefix (line 276). Holds.
- Correctness M-3: Task 7 decodes with `decodeUtf8` and adds `escaped_path_is_read_back` (lines 408, 412); Task 9 reads strictly (line 471); `zeroTwoCoreTable` refuses U+DC80 to U+DCFF with `not_utf8_is_one_sentence` (lines 427, 448). Holds.
- Correctness M-4 and P4-M4: the test-local clock with `release()` (line 391). Holds.
- Correctness M-5: answered by `riggedRemote` (P4-I7). Holds.
- Correctness M-6: the restart exception stated (lines 116, 385, 531). Holds.
- Correctness M-7 and P4-M2: `symbolic_link_reads_as_the_path_it_names` (line 201) and the mode change stated (lines 235, 500). Holds.
- Correctness M-8: `undecodable_record_refuses_the_import` (line 334) and the `\xff\xfe` attachment in the round trip (line 496). Holds.
- Correctness M-9: the ledger's ruling lines rewritten in place (`…-progress.md:8-20`), no "replacing" clauses left on the replaced rulings. Holds.
- Correctness M-10: the ledger line for d-j5s0h0 notes the stale handle. Holds.
- Correctness M-11: `ts/tests/cli/settings.test.ts` under Task 9's Modify, `hook_is_left_alone` becoming `hook_is_checked` (lines 458, 474); `hook_is_left_alone` exists in plan 3 at 7dfdf40, Task 3. Holds.
- Correctness M-12: `exportTargetProblem` (line 378), `bad_target_is_usage` (line 446), Task 3's own sentences (line 227). Holds.
- Correctness M-13: moot under d-b61590. Holds.
- P4-M1: test dropped, `--end-of-options` kept and said so (line 188). Holds.
- P4-M3: `exportingProjects(projects, written)` (line 376), `main.ts` passing a function (line 440). Holds.
- P4-M5: in part, as claimed (lines 392, 447); `stop()` parked. Holds.
- P4-M7: tip unmoved after a second `written` and `settled()` (line 496). Holds.
- P4-M8: `Io.hook` optional, `run` answering 0 without it (lines 470, 473). Holds.
- P4-M9: `ts/src/store/events.ts` in the merge list (line 108). Holds.

## New findings

### N-I1 · Important · `wrapped_projects_pass_every_method_with_its_arguments` cannot compile in Task 6's lane

Handle: plan line 390 ("`members`, `addMember`, and `create` called with three arguments each reach it with the same three"); plan 2 at 5307e56, "Interfaces for plans 3 and 4" (`create(project, owner)`, `members(project)`, `addMember(project, person, role, by)`); lanes table line 100 (Task 6 starts after plan 2's Task 12a, before plan 3 merges, line 102).
Run in the scratch worktree with `tsc --strict --exactOptionalPropertyTypes` over those three signatures: `create("p", "ana", {…})` gives TS2554 "Expected 2 arguments, but got 3", `members("p", "x", "y")` "Expected 1 arguments, but got 3", and `addMember("p", "bo", "member")` "Expected 4 arguments, but got 3".
Failure: the test is called through the wrapper, whose type is `Projects`, so the builder's `tsc` refuses it; the builder either casts the wrapper (`as unknown as …`), which Biome or the review flags, or stops BLOCKED; and the case the fix meant to cover, `create`'s third argument, has no type in Task 6's lane at all.
Fix: Task 6's test calls each method with its declared arguments (`members(p)`, `addMember(p, person, role, by)`, `create(p, owner)`) and asserts each reaches the inner stand-in with those arguments and returns its answer; the extra-argument case stays with Task 8's `project_settings_survive_the_wrapper` (line 445), which already proves plan 3's `create(…, settings)` passes through once plan 3 is merged.

### N-M1 · Minor · the plan cites d-4zg8q3, which d-d0vca9 replaces

Handle: plan lines 25 and 475; `plan-fix-1.md:23`.
Fix: cite d-d0vca9 at both plan lines (the rule is unchanged).

### N-M2 · Minor · d-sdpcyb's reasoning cites the replaced d-pmaw3a

Handle: `lodge show d-sdpcyb --reasoning`, "the events store refuses (d-pmaw3a)"; plan 2 at 5307e56, line 181 ("d-j28rp0, replacing d-pmaw3a"); plan line 320 already cites d-j28rp0.
The conclusion stands on d-j28rp0, which says the same of a surrogate path.
Fix: note it in the ledger line for d-sdpcyb, as M-10 did for d-j5s0h0; no new record is needed.

### N-M3 · Minor · Task 8 says the e2e `server.ts` has a `FixedClock`

Handle: plan line 441 ("`world.ts` and the e2e `server.ts` build `moving` the same way …, with their `FixedClock` and `log`"); plan 3 at 7dfdf40, Task 7a (`server.ts`'s `clock: TestClock`, a minute clock until `standStill()`).
Failure: a builder looks for a `FixedClock` in `server.ts` and finds none, or swaps the test server's clock and changes plan 3's carried e2e tests.
Fix: "with their own clock and `log`".

## Checked and holding

- Lane waits against imports: Task 2 (plan 2's 2 and 7a: `LodgeError`, the codec), Task 3 (Task 2), Task 4 (plan 2's 6: the front-door test; `LodgeError`), Task 5 (plan 2's 11, after 10: `Tree.people`, `MemoryStore`'s `people`, `#app`'s `coreSettings` and `Forbidden`), Task 6 (plan 2's 12a: `held` in the store's forwarding test), Task 7 (Task 6's `ExportTargets`, plan 2's 7b), Task 8 (Tasks 2, 3, 5, 6, 7, plans 2 and 3), Task 9 (Tasks 2 and 4, plan 3) each match what the task reads.
- No task exports into this repository: Global Constraint line 36, Task 10 lines 494 and 499 (`mktemp -d`, `git clone --no-local`), Task 8's targets from `mkdtempSync` (line 446); Task 9 Step 5 only reads this repository through the hook.
- `Bun.spawnSync` everywhere: line 24, Task 2's synchronous `run.ts`, helpers through `#git`; the `Promise` returns of `readStore`, `exportStore`, and `repoRootOf` are consistent with their ports (`Moving.read`, `ExportPorts.write`, `hookContextFor`'s `git.repoRootOf`).
- Names from plan 1 at `server-core`: `checkChange`, `checkState`, `load`, `tree` (attachments optional), `parseCoreSettings(table)` (accepts `[store]` and `[hook]`), `problem`, `Problem`, `CoreSettings`, `ATTACHMENTS`, `parseRecord`, `writeRecord` all exported from `ts/src/core/index.ts`.
- Names from plan 2 at 5307e56: `Clock`, `Now`, `stampOf`, `Store` with `attachmentTexts` and Task 12a's methods, `PublishOutcome`, `Actor`, `person`, `agent`, `actorText`, `Role`, `Projects`, `LodgeError`, `NotFound`, `Conflict`, `Forbidden`, `#app`'s `coreSettings(table)`, `LodgeDatabase`, `openDatabase`, `SqliteProjects`, `appendEvents`, `applyEvent`'s rule for a new kind, `FixedClock(start, stepMs)` with `slept`, `START`, `CountingIds`, `MemoryStore(items, { staged, people })` with `publishes`, `Tree.people`, `parseThread` and `writeThread` with defaulted `people`; plan 2 changed between c3541fc and 5307e56 only by its recheck file, one citation line, and d-n9nm8h.
- Names from plan 3 at 7dfdf40: `Projects.create(…, settings?)`, `settings(project)` null for an unknown project, `names()`; `ApiOptions` with `projects`, `lodgeFor`, `clock`, `log`; `lodgesOver(projects, clock, ids)`; `handler`; the person's operations and `only the signed-in person may <operation>`; `Io` without `hook`, so the optional member is an addition; `run`, `readSettings`, `CliError`; `hook_is_left_alone`; `help_lists_every_command` and `every_command_has_help`; `world.ts`'s `FixedClock` at 2026-10-29T09:30:00+01:00 moved by `sleep`, so the five days of line 442 put it after 2026-11-02T18:56:30+01:00.
- Types across tasks: `ExportTarget` and `ExportOutcome` (Task 6) match `exportStore`'s local types (Task 3); `ZeroTwoCopy` (Task 5) matches `Moving.read` (Task 8) and `StoreRead` plus `zeroTwoCoreTable`; `prepareImport`'s and `importStore`'s parameters match their callers in Tasks 5, 8, and 10; the exporter's sentences for a bad branch and remote are the same in Tasks 3 and 6.

## Files read

`plan-review-correctness.md`, `plan-review-practice.md`, `plan-fix-1.md`, `questions.md`, `probes.md`, `probes/spawn-sync.ts`, `probes/spawn-env.ts`, the plan in full at 8d995b5, the ledger's head; d-sdpcyb, d-v0r9cb, and d-b61590 through `lodge show --reasoning --provenance`; d-n9nm8h and d-4zg8q3 from their branches; plan 2 at 5307e56 (interfaces, lanes, and greps of Tasks 2, 6, 7a, 7b, 10 to 12a); plan 3 at 7dfdf40 (Tasks 3 to 8 by grep and excerpt); on `server-core`: `ts/src/core/index.ts`, `check-change.ts:1-80`, `settings.ts`, `snapshot.ts:1-45`, `differential.test.ts` (spawn lines), `task-12-report.md:26-32`.
Not read: plan 1's tasks, plans 2 and 3's tasks beyond the parts named, Tasks 11a to 11c against the design's lines (unchanged in substance by this round but for line 531).
