# Plan fix round 1: plan 4, the importer, the export, and the design's records

Planner, fix round 1, on `server-import` from ae2db4e, answering `plan-review-correctness.md` (1 Blocking, 4 Important, 13 Minor) and `plan-review-practice.md` (1 Blocking, 11 Important, 9 Minor), with the coordinator's rulings of the dispatch and plan 2's fix round at `origin/server-store` 61f87ad.
Status: done.

## Rulings recorded

- d-sdpcyb (replaces d-ag8p8h and d-y42b7b): the import checks the store as a change from an empty state with the store's settings, read at a settings revision defaulting to the store's, maps, checks the mapped state the same way with the project's settings and owners, refuses a path that is not UTF-8, and publishes through the owner's store (B-1, P4-B1, I-1, P4-I9; plan 2's d-pmaw3a and d-x6vaw8).
- d-v0r9cb: the exporting wrappers forward every method they do not change through a `Proxy`, and `exportingProjects` takes a function (I-4, P4-I5, P4-M3).
- d-b61590 (the author's, recorded before this round): the export names the person, with no lodge 0.2 compatibility (IMP-1).

## Probes added

- Probe 9 (`probes.md`): lodge 0.2's `check_change` from an empty state on this repository's records and on the made-up store, and `Bun.spawnSync`'s standard streams and environment.
- Probe 7 rewritten in place with its re-run outputs (I-2).

## Findings

- Correctness B-1 and practice P4-B1 (fixed, d-sdpcyb replacing d-ag8p8h and d-y42b7b): Task 1 Step 2 calls `checkState(after)` with one argument and adds `checkChange` from an empty state; Task 5 checks both stages with `checkChange` from an empty state, `prepareImport` taking `now` and `importStore` a `Clock`; the tests whose problems a state check could not give now expect check 4 of a change (probe 9).
- Correctness I-1 and practice P4-I9 (fixed, d-sdpcyb): `readStore(repository, rev, settingsRev = rev)`; `zeroTwoRepository` returns `settingsRev`; Task 2 Step 1's `reads_the_branch_layout` passes it and `branch_layout_without_a_settings_revision_has_no_settings` is new; Task 8's `import` takes `settingsRev`.
- Correctness I-2 (fixed): probe 7 rewritten in place with its re-run outputs; IMP-1 needs no re-ask (the dispatch), marked answered in `questions.md` with d-b61590.
- Correctness I-3 (fixed): the plan's Calls made says design line 284 now means lodge 0.2's file layout only; the export writes no `.lodge.toml`; Task 10's script compares files and no longer runs lodge 0.2 on the export; a Global Constraint says no task exports into this repository.
- Practice P4-I1 (fixed, d-4zg8q3 on `server-core`): a Global Constraint states the rule change lands in plan 1's fix wave; `#hook`'s `run` takes `out`, not `write`.
- Practice P4-I2 (fixed): Task 2 says `attempt` passes `{ ...process.env, … }` as `env` at each call and that every helper runs git through `#git`; `isolation_reaches_git` is new; a Global Constraint repeats it (probe 9).
- Practice P4-I3 (fixed): Task 2 Step 1's `missing_git_is_one_sentence` empties `PATH` to a folder, and `GitMissing` is the `ENOENT` `Bun.spawnSync` throws (probe 9).
- Practice P4-I4 (fixed): `ts/tests/app/front-door.test.ts` in the Files of Tasks 4, 5, and 6 and in the lanes' merge list; Task 4 waits for plan 2's Task 6.
- Practice P4-I8 (fixed): Task 2's `repos.ts` carries `git`, `commit`, and `write`; Task 3 adds `bareRemote`, `clone`, `seeded`, `worktree`, and `riggedRemote`.
- Practice P4-I11 (fixed): plan 1 has no git adapter; its one spawning test uses `Bun.spawnSync` and passed in the sandbox (`task-12-report.md:30` on `server-core`), so a Global Constraint makes every spawn `Bun.spawnSync`, which uses `memfd` files and no socket (probe 9); Task 2's `run.ts` functions are synchronous.
- Practice P4-M1 (fixed): `resolve_rev_refuses_an_option` dropped; `--end-of-options` kept as a defence, said so in Task 2.
- Correctness M-7 and practice P4-M2 (fixed): `symbolic_link_reads_as_the_path_it_names` in Task 2; Task 10 states that a link comes back as a regular file.
- Correctness M-9 (fixed): the ledger's lines for d-bh93bn, d-m31e0d, and d-srfxj8 rewritten in place with the current decisions, the "replacing" clauses dropped.
- Correctness M-10 (fixed): the ledger line for d-j5s0h0 notes the stale plan 3 handle; the conclusion stands on its other argument.
- Correctness M-6 (fixed): Review Focus 4 and Task 6 state that `start` exports at once after a restart, so one minute holds within one run of the server; Task 11a's entry says so.
- Correctness I-4 and practice P4-I5 (fixed, d-v0r9cb): Task 6's `exportingProjects` is a `Proxy` forwarding every member but `storeFor` with its arguments, the store's wrapper a `Proxy` intercepting only `publish`; `wrapped_projects_pass_every_method_with_its_arguments` is new; Task 5's `importStore` takes `Pick<Projects, "members" | "storeFor">`, so its stand-in needs no edit at plan 3's merge; Task 8 no longer modifies `exporting.ts` and adds `project_settings_survive_the_wrapper`.
- Practice P4-I6 (fixed): Task 5 Step 1 says eight files, named by path from `ZERO_TWO_STORE`, in both tests.
- Practice P4-I7 and correctness M-5 (fixed): Task 3 carries `rigged_remote` of `tests/gitstore/test_push_race.py` into `repos.ts` as `riggedRemote`, which `moved_remote_branch_answers_moved` uses; the local race is stated as untested, with the reason and probe 4.
- Practice P4-I10 (fixed): Task 4 splits its tests into `post-tool-use.test.ts` (carried) and `moved-advice.test.ts` (new); the parity row and Task 10's name check read the carried file.
- Correctness M-1 and practice P4-M6 (fixed): Task 9's `initialise()` stages the two files with `git add --`, as `init_store` does.
- Correctness M-2 (fixed): Task 4's test-local `resolve` resolves the longest existing prefix, as Task 2's `resolvePath` does.
- Correctness M-3 (fixed): Task 7 encodes and decodes the target's body with plan 2's codec, with `escaped_path_is_read_back`; Task 9 reads `.lodge.toml` strictly, not UTF-8 giving null; Task 8's `zeroTwoCoreTable` refuses a text holding U+DC80 to U+DCFF, with `not_utf8_is_one_sentence`.
- Correctness M-4 and practice P4-M4 (fixed): Task 6's `writes_within_a_minute_share_one_commit` uses a test-local clock whose `sleep` resolves on `release()`.
- Correctness M-8 (fixed): Task 5 adds `undecodable_record_refuses_the_import`; Task 10's round trip adds an attachment holding `\xff\xfe` to the branch layout and compares its bytes.
- Correctness M-11 (fixed): Task 9's Modify lists `ts/tests/cli/settings.test.ts`, its `hook_is_left_alone` becoming `hook_is_checked`.
- Correctness M-12 (fixed): Task 6's `exportTargetProblem`, which Task 8's `export-target` answers as `usage` (`bad_target_is_usage`); Task 3 refuses a bad branch or remote with the same sentences, not `.lodge.toml`'s.
- Correctness M-13 (moot): IMP-1 is answered A (d-b61590), so B's cost to Task 6 no longer arises.
- Practice P4-M3 (fixed, d-v0r9cb): `exportingProjects(projects, written)`; `main.ts` passes `(project) => void exporters.written(project)`.
- Practice P4-M5 (fixed in part): Tasks 6 and 8 say no test sets a target whose export fails without end; `Exporters.stop()` is parked, since no test needs it once that holds.
- Practice P4-M7 (fixed): Task 10's `export_of_an_export_is_unchanged` asserts the tip unmoved after a second `written` and `settled()`.
- Practice P4-M8 (fixed): Task 9's `Io.hook` is optional and `run` answers 0 without it, so no `Io` of plan 3's tests changes.
- Practice P4-M9 (fixed): the lanes' merge list names `ts/src/store/events.ts` (Task 7 and plan 3's Task 4).

## Alignment with plans 2 and 3

- Plan 2 at c3541fc (fix rounds 1 and 2): Task 6 waits for plan 2's Task 12a (was 12); the names table gives `MemoryStore(items, { staged, people })`, `parseThread` and `writeThread` with `people` defaulted (d-vwsnz5), `Tree.people` as the owners, `stampOf`, and `publish`'s refusals (d-j28rp0, replacing d-pmaw3a); Task 5 refuses a file name that is not UTF-8 at the server stage, since `publish` refuses a surrogate path; Task 5 states that the import writes each file once, in one publish into an empty project, and Tasks 5 and 10 that no test re-adds an imported decision; the thread messages the import writes under the owner's name go through `Store.publish` of the owner's own store, never `ask` or `reply`, so d-x6vaw8's refusal is not on the path and the requester is the person named.
- Plan 3 at 7dfdf40 (fix round 1): `ApiOptions.clock` and `ApiOptions.log` (the export's failures go to `log`); `world.ts`'s `FixedClock` moved on by `await clock.sleep(…)`, which Task 8's tests use to pass the made-up store's dates (probe 9); `ts/bunfig.toml` (d-svv7gv) in Task 1's unchanged files; d-amxk94's `/** @public */` on the consumed names, in the Exports constraint; `TestServer.handEdit(project, files)` is not used by this plan.

## Counts

Blocking: 2 fixed (B-1, P4-B1, one cause). Important: 15 fixed (I-1 to I-4, P4-I1 to P4-I11), 0 rejected. Minor: 21 fixed or moot, 1 parked in part (P4-M5's `stop()`).
