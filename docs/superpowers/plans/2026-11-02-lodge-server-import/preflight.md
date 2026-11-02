# Preflight scan: plan 4 of the server build

Plan `docs/superpowers/plans/2026-11-02-lodge-server-import.md` at 1946379 on `server-import`; ledger `…-progress.md`.
Read-only scan, before the build; a table and not a verdict.

Sources read, by handle:
- Plan 1 code at `/var/tmp/lodge-server-core/ts/src` (branch `server-core`, 7d5ecbc), `ts/tests/structure/{calls,table}.ts`, `ts/.dependency-cruiser.cjs`, `ts/knip.json`, `ts/tests/parity.json`, `ts/tests/parity-names.ts`, `ts/tsconfig.json`.
- Plan 2 text at `/var/tmp/lodge-server-store/docs/superpowers/plans/2026-11-02-lodge-server-store.md` (branch head 0244e79; the plan aligns to a035344, and I diffed the two: nothing plan 4 consumes changed).
- Plan 3 text at `/var/tmp/lodge-server-api/docs/superpowers/plans/2026-11-02-lodge-server-api.md` (working tree at 9ac93ac; the plan aligns to 9988813, and I diffed the two: nothing plan 4 consumes changed, but `asPerson` left `TestServer` and `Project`, see M3).
- Plan 4's own text in full, the ledger, `probes.md`, `questions.md`, the made-up store `probes/zero-two-store/`, the Python sources the tasks cite (`tests/hook/`, `tests/e2e/test_hook_*`, `tests/gitstore/repos.py`, `conftest.py`, `test_push_race.py`, `src/lodge/hook/post_tool_use.py`, `src/lodge/main.py`, `src/lodge/gitstore/{trees,plumbing,settings,setup,branch}.py`, `src/lodge/cli/parser.py`, `commands.py`), and the design's section headings.

Not read: plan 4's other review files (`plan-review-*.md`, `plan-recheck-*.md`, `plan-fix-*.md`, `planner-*.md`), plans 2 and 3's probes, plan 1's task reports, `src/lodge/app/*.py` beyond what the tasks cite.

Run by me, in the scratchpad and outside the repository:
- `bun probe1.ts`: plan 1's `load`, `checkState`, and `checkChange` over `probes/zero-two-store/` (Task 1's two assertions): `state []`, `change []` at 2026-11-03T00:00:00+00:00; at plan 2's `START` three check-1 problems (`d-q59cdf`, `d-qqrf9k`, `d-t46j05`), as Task 5 line 334 expects; `writeRecord` and `writeThread` of each parsed file give its text back byte for byte; three author decisions, one coordinator decision, thread messages by `coordinator` and `author`.
- `bun probe2.ts`: a decision holding U+DCFF in its body or its header is `problem` check 1 `the text is not valid UTF-8` in plan 1's `parseRecord` and `load`, as Task 5 line 334 (`undecodable_record_refuses_the_import`) expects.
- `git hash-object --stdin` of `a\n`: `78981922613b2afb6025042ff6bd878ac1994e85`, as Task 2 line 200 says.
- `lodge show` of every record ID the plan cites, in the branch that holds it: all exist (plan 4's branch, `server-core`, `server-store`, `server-api`); none is missing.

Plan 4 line numbers are those of the file at 1946379.

## 1. Pairs of plan 4 tasks that share a file or an interface

Columns: earlier task Produces, later task Consumes, found.
"match" means the names, parameters, return types, and paths agree as written.

| # | Pair | Produces (plan line) | Consumes (plan line) | Found |
|---|---|---|---|---|
| A1 | 1 to 2 | `ZERO_TWO_STORE: ReadonlyMap<string, string>` in `ts/tests/core/zero-two-store.ts`, eleven files (146) | `zeroTwoRepository` commits it (165, 197) | match; eleven files counted in `probes/zero-two-store/` (ten under `lodge/`, plus `.lodge.toml`) |
| A2 | 1 to 5 | the same map (146) | `ZERO_TWO_STORE` as a `ZeroTwoCopy`, "the eight files under `lodge/` that do not end `/.gitkeep`" (334) | match; eight counted (four decisions, entry, area, thread, attachment); the tests build `settings` from the `.lodge.toml` text, no helper named (Task 8's `zeroTwoCoreTable` is not available to lane 5) |
| A3 | 1 to 6 | the same map (146 names Task 6 as a reader) | `export_files_hold_the_store_and_kept` (390) | mismatch M7: Task 6's Consumes (349) omits Task 1; and `MemoryStore` takes records, not files (plan 2:264) |
| A4 | 1 to 8, 10 | the same map (146 names Tasks 8 and 10) | through `zeroTwoRepository` (445, 497) | match through Task 2; Tasks 8 and 10 do not list Task 1 or Task 2's helper names beyond "Tasks 2 to 9" (493) |
| A5 | 2 to 3 | `attempt`, `runBytes`, `run`, `resolveRev`, `readStore`, `isolateGit`, `repos.ts` `git`, `commit`, `write`, `zeroTwoRepository` (168 to 197) | "Task 2's `run.ts`, `readStore`, and test helpers" (216); `repos.ts` gains `bareRemote`, `clone`, `seeded`, `worktree`, `riggedRemote` (212, 236) | match; Python names exist (`tests/gitstore/repos.py:18,30,38,44,52,58,64`, `test_push_race.py:35-57`) |
| A6 | 2 to 8 | `readStore(repository, rev, settingsRev?)` returning `Promise<StoreRead { rev, files, settings: string \| null }>` (176 to 181) | `Moving.read(repository, rev, settingsRev): Promise<ZeroTwoCopy>`, "main joins `#git`'s `readStore` and `#cli`'s `zeroTwoCoreTable`" (432, 441) | match: `rev` and `files` carry over, `settings` text becomes a table by `zeroTwoCoreTable` (`{}` when null, 441); `settingsRev` always passed, defaulted by the operation (439) |
| A7 | 2 to 9 | `repoRootOf(edited): Promise<string>`, `isFolder(path): boolean`, `resolvePath(path): string`, `isolateGit()` (183 to 186, 195) | `hookContextFor(edited, git: { repoRootOf, isFolder })` (466 to 469); `main` passes `resolvePath` as `Resolve` (476) | match; `Resolve = (path: string) => string` (263) agrees with `resolvePath` |
| A8 | 3 to 8 | `exportStore(target, files, message): Promise<committed \| unchanged \| moved>`, parameter and result types unexported (219 to 225) | `ExportPorts.write: (target: ExportTarget, files, message) => Promise<ExportOutcome>` (362); Task 8 passes `exportStore` as `write` (441, 452) | match field by field (`repository`, `branch`, `remote: string \| null`; the three outcome kinds); only `tsc` can prove it, which Step 4 of Task 8 (452) says |
| A9 | 3 to 6 | the sentences `export-target: branch must be …`, `export-target: remote must not start with -` (227) | `exportTargetProblem` gives the same two sentences (378) | match, character for character |
| A10 | 4 to 9 | `parseHookSettings(table: unknown): readonly string[]` through `#app` (254); `respond`, `run`, `HookContext`, `Resolve` through `#hook` (257 to 266) | `readSettings` checks `[hook]` with it (475); `main` calls `run(read, out, context, resolve, cwd)` (476); `hookContextFor` returns `{ repoRoot, dataRoot, frozen, server }` (469) | match: argument order of `run` agrees (266, 476), the context shape agrees with `HookContext` (257 to 261), `Io.hook?: () => Promise<number>` accepts `run`'s `Promise<0>` |
| A11 | 4 to 9 | `texts.ts` moved texts chosen by `context.server` (270 to 274) | `hookContextFor` fills `server` from `[server].url` (472) | match; `holds_records` and `data_root` of `src/lodge/gitstore/setup.py:58-67` agree with 472 (branch mode always true, `dataRoot` null) |
| A12 | 5 to 8 | `importStore(copy, project, requester, projects: Pick<Projects, "members" \| "storeFor">, settings: CoreSettings, clock): Promise<Imported>` (311); `ZeroTwoCopy`, `Imported` (296 to 309) | the `import` operation calls `importStore(copy, project, <signed-in person>, options.projects, coreSettings(settings), options.clock)` (439) | match in order and types; `Imported` is plain data, so `toWire` (plan 3:379) takes it; the 422 answer is plan 3's helper, not named (M16) |
| A13 | 6 to 7 | `ExportTargets { target(project), setTarget(project, target, by: Actor) }`, `ExportTarget` (352 to 357) | `SqliteExportTargets implements ExportTargets` (407) | match; Task 7 waits for Task 6 (101) |
| A14 | 6 to 8 | `Exporters(ports)`, `written`, `start`, `settled`, `exportingProjects(projects, written)`, `exportTargetProblem`, `ExportPorts` (358 to 376) | `main` builds `Exporters` and `exportingProjects(sqliteProjects, (project) => void exporters.written(project))` (437, 441); the `export-target` operation calls `exportTargetProblem`, `setTarget`, `written` (440) | match; `exportingProjects` returns `Projects`, so plan 3's `ApiOptions.projects` and `lodgesOver` (plan 3:370, 377) accept it |
| A15 | 7 to 8 | `SqliteExportTargets(database: LodgeDatabase, clock: Clock)` through `#store` (407) | `main`: "`SqliteExportTargets` over the opened store" (441) | match |
| A16 | 6, 8 to 10 | `Exporters.settled()` (374) | `export-target.test.ts` and `round-trip.test.ts` call `exporters.settled()` (447, 497) | mismatch M2: nothing says how the tests reach `exporters` through `world.ts` or `testServer()` |
| A17 | 8 to 10 | `import` and `export-target` operations, a person's session, the clock moved by `sleep(432000)` (438 to 443) | `round-trip.test.ts` "through the server's handler in process" (497) | mismatch M3 and M4: no person's request helper in plan 3's `TestServer`, person `author` in the e2e server, `TestClock.sleep` in minute mode unspecified |
| A18 | 2 to 10 | `zeroTwoRepository(layout)` takes no extra file (197) | an attachment of the bytes `\xff\xfe` "added to the branch layout's store" (497) | mismatch M5 |
| A19 | 8 and 9 | both edit `ts/src/main.ts` and `ts/src/cli/index.ts` (108); disjoint names (`zeroTwoCoreTable`; `hookContextFor`, `Io.hook`) | | match; merge note present (108); `readSettings` is edited by Task 9 only (459), Task 8 does not touch `settings.ts` (see M1) |
| A20 | 2, 4, 9 and plan 1's parity | rows of `ts/tests/parity.json`: `tests/gitstore/conftest.py` planned and `repos.py` planned (plan 1 table), hook rows `changed`, `test_hook_outside_repository_exit_0_silent.py` planned | "Parity rows this plan settles" (123 to 130); Task 10 widens `ported_files_exist` (498) | match with plan 1's `parity.json` (statuses and `plan` 4 agree); plan 3's widening of the same tests to `plan` 2 or 3 (plan 3:514) leaves plan 4's rows for Task 10, as 498 says |
| A21 | 4, 5, 6 | each adds names to `ts/src/app/index.ts` and `front-door.test.ts`'s allowed list (108) | plan 2 Task 6 creates the test (plan 2:360); Task 4 waits for it (109) | match; Task 5 waits for plan 2's Task 11 and Task 6 for 12a, both after Task 6 |
| A22 | 7 and plan 3's Task 4 | each adds `applyEvent` cases in `ts/src/store/events.ts` (108) | plan 2: unknown kind throws, a later plan adds its case (plan 2:188, 393) | match; merge keeps both sides (108) |
| A23 | 2, 4, 9 | `ts/package.json` `imports` gains `#git` (Task 2), `#hook` (Task 4) | `layoutViolations` demands `imports` equal the folders of `src` (`calls.ts`, plan 1) | match per lane; line 108's list of shared files omits `ts/package.json` and `ts/tests/parity.json` (M13) |
| A24 | 10 to 11a to 11c | the round trip and its report (487 to 506) | 11a builds Export and Moving entries "from what Tasks 2 to 10 built" (532) | match; design headings at lines 52, 64, 280, 287 and the part boundaries of 529 to 540 agree with `docs/superpowers/specs/2026-11-02-lodge-server-design.md` |

## 2. One row per task: does its own text agree with itself

Checked: tests against the code the Interfaces specify, files created against files later touched, lane waits (lanes table, 93 to 105) against what the task's tests import.

| # | Task | Tests against code | Files created against later use | Lane waits against imports | Found |
|---|---|---|---|---|---|
| B1 | 1 (136 to 155) | `zero_two_store_checks_clean` asserts `checkState` and `checkChange` find nothing (152); I ran both over the made-up store with plan 1's code: both empty | creates `zero-two-store.ts` and its test; read by Tasks 2, 5, 6, 8, 10 (146) | `plan 1 merged` (95); imports only `#core` | match; the generator `probes/fixture.py` exists (153); `Bun.TOML.parse` in a test is allowed (the ban of plan 3:54 is for the command) |
| B2 | 2 (157 to 206) | 5 + 10 + 5 tests (200 to 202) cover `attempt`, `runBytes`, `run`, `resolveRev`, `readStore`, `resolvePath`, `repoRootOf`, `isFolder`, `isolateGit`; `GitMissing` read by `missing_git_is_one_sentence` | `repos.ts` created here, extended by Task 3 (212); `zero-two.ts` read by Tasks 3, 8, 10 | waits Task 1, plan 2's Tasks 2 and 7a (96): imports `LodgeError` (plan 2 Task 2), `decodeUtf8`, `encodeUtf8` (7a), `ZERO_TWO_STORE` (Task 1): covered | match, with M6 (`GitDone`, `StoreRead` have no named reader); `input_reaches_git` hash confirmed by running git; the `undecodable_name…` test passes U+DCFF in a string `input`, which `attempt` encodes through `encodeUtf8` (187), consistent |
| B3 | 3 (208 to 243) | 13 tests (238) cover steps 1 to 7 of `exportStore`; `bad_branch_name_is_refused` covers the remote sentence too; the local race has no test and says why (239) | `export.ts` read by Task 8's `main`; `repos.ts` gains five helpers (212, 236) | waits Task 2 (97): imports `run.ts`, `readStore`, `isolateGit`, `repos.ts`, `zeroTwoRepository`, `encodeUtf8`: covered | match; `exportStore`'s types are unexported (225), so no knip finding |
| B4 | 4 (245 to 283) | 24 carried + 6 new tests (278, 279) cover `respond`, `run`, the three moved texts, `parseHookSettings` | creates `hook-settings.ts` (app) read by Task 9; `#hook` read by Task 9's `main` | waits Task 1, plan 2's Task 6 (98): the front-door test it edits is created there (plan 2:360); imports `LodgeError` only; `resolve` is test-local, so no wait on Task 2 (276) | match, with M6 (`HookContext`, `Resolve`, `HookOutput`) and M18 (279's "not `lodge/decisions` as a place to edit": the moved text names the path, which is under `lodge/decisions/`, so the assertion needs a sentence of the Python text to be absent, not the folder name) |
| B5 | 5 (285 to 339) | 13 + 7 tests (334, 335) cover the four checks, the mapping, the refusals, the owner rules, the clock | `importing.ts` read by Task 8 (`importStore`) and by Task 10 through the operation | waits Task 1, plan 2's Task 11 (99): needs `Tree.people` (plan 2 Task 10, before 11), `Forbidden`, `MemoryStore` `people` (both Task 11), `Role`, `coreSettings`, `FixedClock`, `START`: covered | match, with M6 (`PreparedImport`, `Imported`) and M19 (the stand-in's `MemoryStore` must be built with `people` `{owner}`, plan 2:560, else `current.people` is `{author}` and the mapped state is checked with the wrong people; 335 does not say) |
| B6 | 6 (341 to 396) | 6 + 9 tests (390, 391) cover `exportFiles`, `exportMessage`, `exportTargetProblem`, `exportingProjects`, `Exporters`; 392 bounds retries | creates `exporting.ts`, `exporters.ts`; read by Tasks 7, 8, 10 | waits Task 1, plan 2's Task 12a (100): `wrapped_store_passes_every_other_method` names `held` (390), a 12a method; `MemoryStore`, `FixedClock` from Task 2: covered | M7 (Consumes omits Task 1 and the made-up store; `MemoryStore` takes records, plan 2:264) and M6 (`ExportTarget`, `ExportOutcome`, `ExportTargets`, `ExportPorts`: Task 7 reads two, no later-read table as plans 2 and 3 have) |
| B7 | 7 (398 to 417) | 8 tests (413) cover target set, read back, escaped path, newest wins, null, event shape, rebuild, unknown project | creates `export-targets.ts`; `index.ts` and `events.ts` edited | waits Task 6, plan 2's Task 7b (101): imports `appendEvents` (7a), `SqliteProjects` (7b), `openDatabase`, `rebuild`, `FixedClock`: covered; `MIGRATIONS[1]` held table already merged via Task 6's wait on 12a (409) | match, with M8 (unknown project is `NotFound`, 411, while `import` says `no-project`, 439) and M9 (read before write, plan 2:191) |
| B8 | 8 (419 to 453) | 10 + 5 + 5 tests (446 to 449) cover both operations, the wrapper, `zeroTwoCoreTable`; `main.ts` wiring has no test of its own (the `failed` log line, `start`) | creates `moving.ts`, `zero-two.ts`; edits `person.ts`, `index.ts`, `main.ts`, `world.ts`, `server.ts`; Files omit `ts/src/cli/settings.ts` | waits Tasks 2, 3, 5, 6, 7 and plans 2 and 3 merged (102): imports every one of those; plan 3's helpers named in 445 | mismatches M1, M2, M3, M15, M16; note M10 (`start` in `open` runs for `setup` too) |
| B9 | 9 (455 to 483) | every carried test of the two e2e files plus `hook_gives_the_moved_advice…` (479); `hook_is_checked` replaces `hook_is_left_alone` (475) | creates `hook-context.ts`, `repository.ts`; edits `grammar.ts`, `commands.ts`, `settings.ts`, `index.ts`, `main.ts`, four test files, `parity.json` | waits Tasks 2 and 4 and plan 3 merged (103): imports `repoRootOf`, `isFolder`, `resolvePath`, `isolateGit` (Task 2), `#hook` and `parseHookSettings` (Task 4), `run`, `Io`, `readSettings` (plan 3): covered | match; the carried tests' `init` and `search` calls fail in `readSettings` before any `fetch` (the helper's `fetch` throws, 477), as the Python test expects (exit 2, `lodge: .lodge.toml: …`); this repository's `.lodge.toml` (`[store]`, `[import]`, `[hook]`, no `[server]`) gives the record advice at 483 |
| B10 | 10 (485 to 506) | 2 tests + 2 parity tests + 2 scripts (497 to 500); step 3 runs the scripts | creates `round-trip.test.ts`, `round-trip.ts`, `round-trip.sh` | waits Tasks 8 and 9 (104); consumes "Tasks 2 to 9" (493) | mismatches M2 to M5; the script cannot import `src/main.ts` (the dependency-cruiser `front-door` rule, plan 1 `.dependency-cruiser.cjs`, lets `scripts/` import `src/` only through `#…`), so "the real clock" (499) is its own, unstated; this repository has both `.gitkeep` files, so the file comparison of 505 holds |
| B11 | 11a (529 to 532) | no tests; verified by `lodge check`, `lodge show` (543) | edits entries and decisions that exist: `s-a4jfp1`, `s-v1sb0j`, `s-165qfh`, `s-3xka4c`, `s-07ar34`, `s-z1zvb4`, `s-j8tp0n`, `d-zq5sfb`, `d-jxwj8m`, `d-cg3nn3`, `d-a3e8kb` all `show` current | waits Task 10 (105) | match; design lines 52 to 62, 64 to 94, 280 to 290 agree with the design's headings |
| B12 | 11b (534 to 535) | | `purpose` entries; the four added must-nots are design lines 47 to 50 (items 4 to 7), as 535 says | in order after 11a | match |
| B13 | 11c (537 to 540) | step 2 runs the hook on the design (543) | edits the design, `.lodge.toml` `frozen` (line 8 there), `CLAUDE.md` | in order after 11b | match, with M14 (`CLAUDE.md` names the two frozen design documents on line 8 and again on line 33, 540 says "one line") |

## 3a. Names consumed from plan 1 (code at `/var/tmp/lodge-server-core/ts/src`, 7d5ecbc)

Plan 4's table puts these in row 75 (line 75) and in the Interfaces of Tasks 1, 2, 3, 5, 6; the table's heading says "from plans 2 and 3", see M12.

| # | Name | Used by (plan 4 line) | In plan 1 | Found |
|---|---|---|---|---|
| C1 | `checkChange(published, after, settings, now)` | Tasks 1, 5 (152, 315, 320) | `core/check-change.ts:18`: `(published: Snapshot, after: Snapshot, settings: CoreSettings, now: string, current: Snapshot \| null = null): CheckResult` | match; both snapshots, `now` a stamp string; the fifth parameter defaults |
| C2 | `checkState(snapshot)`, `CheckResult` | Task 1 (152) | `core/check-state.ts:133`; `CheckResult { problems, notes, ok }` at `:7` | match |
| C3 | `load(tree)`, `Snapshot` | Tasks 1, 5 (152, 314 to 320) | `core/snapshot.ts:44`; paths ending `/.gitkeep` skipped at `:80-82` | match; 319's "`load` skips `.gitkeep`" holds |
| C4 | `tree({ rev, files, attachments?, people? })`, `Tree` | Tasks 1, 5, 6 (152, 315, 320, 368) | `core/snapshot.ts:17` (`attachments` defaulted); `Tree { rev, files, attachments }` at `:12`, no `people` | match for Task 1 and for plan 4's `rev`/`files`/`attachments`; `people` and its default come from plan 2's Task 10 (row C21) |
| C5 | `parseCoreSettings(table)`, `CoreSettings`, `coreSettings(partial)` | Tasks 1, 5 (152, 293) | `core/settings.ts:35`, `:20`, `:24`; accepts `store`, `hook`, `length`, `import` and refuses any other name (`:36-40`) | match; Task 1 passes the whole `.lodge.toml` table, whose names are all accepted; `#core`'s `coreSettings` is the default-filling one, plan 4 names plan 2's `#app` namesake (293) |
| C6 | `parseRecord(path, text)`, `writeRecord(record)` | Task 5 (293, 317, 318) | `core/fileformat.ts:18`, `:30`; `writeRecord` throws `ValueError` on a statement holding the reasoning heading | match; I ran `writeRecord(parseRecord(…))` over all four decisions: byte-equal; `Decision.decidedBy` is the field (`core/model.ts:28`) |
| C7 | `parseThread(path, text)`, `writeThread(thread)` | Task 5 (293, 317, 318) | `core/threads.ts:25`, `:107`, one and two parameters respectively as plan 1 ports them; `Message.by` at `core/model.ts:132` | match for the one-argument calls (the "default people" read in 318); the `people` parameter is plan 2's (row C21); I ran `writeThread(parseThread(…))` over the made-up thread: byte-equal |
| C8 | `Problem`, `problem(value)` | Task 5 (293, 318, 320) | `core/model.ts:113`, `:120`; `problem({ path, check, message })` fills `kind` and `line` | match |
| C9 | `ATTACHMENTS` | Task 5 (293, 329) | `core/snapshot.ts:29` = `"lodge/attachments/"` | match |
| C10 | `Tree` as a type | Task 6 (349, 368) | `core/snapshot.ts:12`, re-exported by `export * from "./snapshot.ts"` (`core/index.ts`) | match |
| C11 | structure facts plan 4 relies on: `PACKAGES` holds `git` (imports `app`, `core`) and `hook` (imports `app`, `core`), `main` imports all; `process-confinement`, `file-confinement`, `network-confinement` allow `git` (process, files), `git` and `cli` (files) | Global Constraints (32), Tasks 2, 3, 9 | `tests/structure/table.ts:3-11`, `.dependency-cruiser.cjs` rules | match; no table change is needed, as Task 1 (148) says; `layoutViolations` (`calls.ts`) requires `package.json` `imports` to equal the folders of `src`, which each lane meets alone |
| C12 | the file-writing call rule as d-d0vca9 changes it | Global Constraints (25), Tasks 6, 8, 9 (`ExportPorts.write`, `process.stdout.write`) | `tests/structure/calls.ts:147` (`writes.has(attr)`) still reports any call whose last name is in the `writes` set, `write` included, outside `git` | precondition, not yet in the code at 7d5ecbc: line 25 says the rule change lands in plan 1's fix wave before this plan builds; until it does Tasks 6 (`ports.write`), 8, and 9 fail `check-ts.sh` |
| C13 | `callViolations` rules for `app` and `hook` | Tasks 4, 5, 6 | `calls.ts:95` and `:118`: `app` and `core` may not name `Bun`, `process`, `setTimeout`, `Date` (but `new Date(ms)` in `app`); `hook` is not pure | match; Task 6 waits only through `clock.sleep` (386); Task 4's `hook` uses `RegExp`, `JSON`, nothing banned |
| C14 | `parity.json` rows of plan 4 and `parity-names.ts` `rowMissing` | Tasks 2, 4, 9, 10 | `tests/parity.json`: `tests/gitstore/conftest.py` planned, `repos.py` planned, `tests/hook/test_post_tool_use.py` changed, `test_hook_feedback_after_hand_edits.py` changed, `test_hook_outside_repository_exit_0_silent.py` planned, `test_help_lists_every_command.py` planned (plan 3); `tests/parity-names.ts:45` `rowMissing(root, pythonPath, row)` | match with the "Status now" column (124 to 130); `rowMissing` takes `{ ts }`, which Task 10 (498) calls |

## 3b. Names consumed from plan 2 (plan text, branch head 0244e79; plan lines)

| # | Name | Used by (plan 4 line) | In plan 2 | Found |
|---|---|---|---|---|
| C15 | `Clock { now(): Now; sleep(seconds): Promise<void> }`, `Now { epochMs, offsetMinutes }` | Tasks 5, 6, 7, 8 (67) | 92, 93 | match |
| C16 | `stampOf(now): string` | Tasks 5, 7 (67, 327, 408) | 123, 258 | match; "2026-10-29T09:30:00+01:00" shape |
| C17 | `Store`: `trees()` as `readonly [Tree, Tree]`, `attachmentTexts()`, `publish(base, writes, message, approves?)`, `hold`, `held`, `decline`, `commit`, `freshness`, `gate`; `PublishOutcome` | Tasks 5, 6 (68, 326 to 328, 383) | 95, 101 to 111 | match; Task 5 calls `store.publish(current, files, message)` and `trees()` destructuring `[current]` as 326 and 328 say; `REJECTED` is plan 2's name |
| C18 | `publish` refuses a surrogate path and a changed decision file (d-j28rp0) | Task 5 (68, 320, 330) | 190, Task 7b 422 | match: a path holding any surrogate throws `LodgeError("<path>: a path holding a lone surrogate cannot be stored")`; an empty base cannot trigger the second refusal |
| C19 | `Actor`, `person(name)`, `agent(role?)`, `actorText`, `Role { OWNER, MEMBER }` | Tasks 5, 6, 7, 8 (69, 325, 387, 441) | 112 to 116 | match; `agent("exporter")` (441) takes a role string |
| C20 | `Projects`: `members(project)` as `ReadonlyMap<string, Role>` in code-point order, `storeFor(project, actor)`, `create`, `addMember` | Tasks 5, 6, 8 (69, 324) | 117 to 122; code-point order at Task 7b | match; Task 5 filters `Role.OWNER` (324) |
| C21 | `Tree.people` (owners), `tree()` defaulting `people` to `{author}`, `parseThread(path, text, people?)`, `writeThread(thread, people?)` (d-vwsnz5) | Task 5 (74, 315, 317, 318, 320) | Task 10: 522 to 525 (`isAuthor(d, people = AUTHOR_ONLY)`, trailing defaulted parameters) | match; Task 5's "default people" read and the owner's set are the two cases |
| C22 | `LodgeError`, `NotFound`, `Conflict`, `Forbidden`, `coreSettings(table)` (throws `LodgeError`) | Tasks 2 to 9 (72, 293) | 140 to 145; `Forbidden` added in Task 11 (144); `coreSettings` in Task 2 (262) | match; `Forbidden` needs plan 2's Task 11, which Task 5 waits for (99) |
| C23 | `decodeUtf8(bytes): string`, `encodeUtf8(text): Uint8Array` through `#core` | Tasks 2, 3, 7 (73) | Task 7a: 379, 380 (U+DC00 + byte for an invalid byte; a lone surrogate outside the escapes throws `ValueError`) | match |
| C24 | `LodgeDatabase`, `openDatabase(path)`, `SqliteProjects(database, clock)`, `appendEvents(tx, project, actor, at, events)`, `applyEvent` | Tasks 7, 8 (76, 408) | 179 to 183; `appendEvents` exported from `store/events.ts` (393), `applyEvent` not exported (inside the file Task 7 edits) | match; `NewEvent` is unexported, Task 7 passes plain objects |
| C25 | `FixedClock(start = START, stepMs = 0)` with `slept` and `sleep` moving it; `MemoryStore(items, { staged, people })` with `publishes`, `rejectNext`; `CountingIds`; `START` | Tasks 5, 6 (77, 335, 391) | 262 to 266 (Task 2), 560 (Task 11 `people`) | match; `MemoryStore`'s items are `(Area \| Decision \| SpecEntry)[]` (264), see M7 and M19; `START` is not in plan 4's table (77) though Task 5 reads it (293, 334) |
| C26 | `front_door_exports_nothing_else` and its list of allowed additions | Tasks 4, 5, 6 (70) | Task 6: 360 | match |
| C27 | held-message rule (d-2v8vtk): `Store.publish` neither holds nor refuses a message; Task 12c changes only `threads.ts`, `held.ts`, `results.ts` | 86, 331 | Task 12c, 634 to 640, Files (`threads.ts`, `held.ts`, `results.ts`, tests) | match; plan 2's latest fix round (waiting follows published messages only) does not touch plan 4 |
| C28 | transaction rule (d-thvvzx): a store transaction that reads before it writes opens with a write | Task 7 | 191 | Task 7 (408) does not carry it, M9 |

## 3c. Names consumed from plan 3 (plan text, working tree 9ac93ac; plan lines)

| # | Name | Used by (plan 4 line) | In plan 3 | Found |
|---|---|---|---|---|
| C29 | `Projects.create(project, owner, settings?)`, `settings(project): Promise<table \| null>`, `names()` in code-point order | Tasks 6, 8 (71, 387, 439, 441) | 339 to 341 | match; the wrapper test defers `create`'s third argument to Task 8 (390), consistent |
| C30 | `ApiOptions { accounts, projects, lodgeFor, clock, random, version, log }`; `lodgesOver(projects, clock, ids)`; `handler(options)` | Task 8 (78, 437, 441) | 368 to 378 | match for `projects`, `lodgeFor`, `clock`, `log`; adding a required `moving` (429) breaks any other literal `ApiOptions`, M15 |
| C31 | the person's operations of `ts/src/api/person.ts` and their `forbidden` sentence | Task 8 (78, 438) | 410 to 442: "each `forbidden` (`only the signed-in person may <operation>`) for an agent token", `person.ts` in Task 6's Files | sentence matches; no operation table or registration function is named, M16 |
| C32 | `project-create`'s `settings`, owner = the person the server is set up for | Task 8 (79, 85, 445) | 393 | match; whether a signed-in person (not a token) may call it is not stated (396 gives the token's rule only), M3 |
| C33 | the session cookie with the server's `Origin`; the 422 answer with the whole result | Task 8 (78, 439) | `Origin` rule 441; 422 at 386 and 392 for `add`, `ask`, `reply`, `close` (and `approve`, 443) | behaviour matches; no helper for the person's cookie request in the test world and none named for the 422 answer, M3 and M16 |
| C34 | `Accounts.setup(): Promise<ServerSetup \| null>`, `ServerSetup { origin, person, at }` | Task 8 (79) | 303, 320 | match |
| C35 | `world.ts` (the API's test world) | Task 8 (80, 442) | 398: `openDatabase(":memory:")`, `FixedClock` at 2026-10-29T09:30:00+01:00 (moved by `await clock.sleep(seconds)`), server set up for `ada`, project `work`, an agent token, `log` into an array | match for the clock arithmetic (432000 s is five days, past 2026-11-02T18:56:30+01:00, 443); no person's session helper, no `exporters`, M2 and M3 |
| C36 | e2e `server.ts`: `TestServer`, `TestClock { minutes(), standStill(), slept }` | Task 8 (80, 442) | 517 to 534: person `author` (530), `fetch`, `origin`, `token`, `clock`, `approve`, `handEdit`, `stored`, `paths` | M2, M3, M4: no `exporters`, no person's request, `sleep` in minute mode not specified |
| C37 | `Io { cwd, env, fetch, out, err, version }`, `run(argv, io)`, `parse(argv, version)`, `Command`, `readSettings(root)`, `CliError(message, exitCode)` | Tasks 8, 9 (81, 471) | 202 (Command), 220 (parse), 253 (CliError), 263 (readSettings), 477 (Io), 485 (run) | match; `Io.hook?` is additive (471) and `exactOptionalPropertyTypes` (`tsconfig.json`) accepts an omitted optional property |
| C38 | "the TOML conversion of `ts/src/cli/settings.ts`" | Task 8 (81, 428) | inline in the text of `readSettings` (275): `integersAsBigInt`, `bigint` to number, float and date to `null`; no exported function takes text | M1 |
| C39 | `settings.test.ts`'s `hook_is_left_alone` | Task 9 (81, 475) | 285 (the test), 278 (`[hook]` left as it is) | match; Task 9 renames it to `hook_is_checked` |
| C40 | `ts/src/main.ts`: `serverCommand`'s `open(data)`, the command's `Io`; `ServerParts { options }` | Tasks 8, 9 (82, 441, 476) | 421 to 428, 574 to 590 (`open(data)` builds `ApiOptions`; `Io` at 577) | match; `ServerParts` has only `options`, so `exporters.start` has no serve-only place (M10) |
| C41 | `grammar.test.ts`'s `help_lists_every_command` and `every_command_has_help`, `ts/tests/e2e/help-lists-every-command.test.ts`, `parity.json`'s `dropped` | Task 9 (83, 479) | 235, 150, 471; `dropped` 33, 131 | match; plan 3's `why` for the help row ends "`hook` for plan 4" (plan 3:150), which line 129 of plan 4 removes |
| C42 | the exports plan 3 tags `@public` from plan 4's table | Global Constraints (33) | 63: plan 3's Task 8 pastes plan 4's table "as it stands the day the brief is written" | match in mechanism; it keys on the table's names, which includes non-exports (methods of `Store`, test names), harmless |

## 4. Counts

Section 1: 24 rows (A1 to A24).
Section 2: 13 rows (B1 to B13: Tasks 1 to 10, 11a, 11b, 11c).
Section 3: 14 rows for plan 1 (C1 to C14), 14 rows for plan 2 (C15 to C28), 14 rows for plan 3 (C29 to C42).
Total: 79 rows.

## 5. Mismatches

Each with the plan line, the handle, and what would close it.
M1 to M3 and M16 are the ones a builder cannot resolve from the plans alone.

- **M1 · the TOML conversion has no name** (plan 4:428, 422 to 424, 81; plan 3:275).
  Task 8 produces `zeroTwoCoreTable(text)` "with the conversion `readSettings` uses (RULE-TOML)".
  Plan 3 describes the conversion only as steps inside `readSettings(root)` (a function of a folder, 263 and 275), exports no function that takes text, and Task 8's Files do not list `ts/src/cli/settings.ts`.
  `RULE-TOML` is defined in neither plan (`grep -rn RULE-TOML docs` finds plan 4:428 and `d-j5s0h0` only).
  Close it by naming the plan 3 function the coordinator will find when it aligns (or by adding `settings.ts` to Task 8's Files with an exported text-level function), and by dropping or defining `RULE-TOML`.
- **M2 · the tests cannot reach `exporters`** (plan 4:442, 447, 497; plan 3:398, 517 to 528).
  `export-target.test.ts` and `round-trip.test.ts` call `exporters.settled()`, and the e2e round trip needs the exporter too.
  Plan 3's `world.ts` returns a handler, an agent token, a clock, and a log, and `TestServer` has `fetch`, `origin`, `token`, `clock`, `approve`, `handEdit`, `stored`, `paths`; neither exposes the `Exporters` or the `Moving`.
  442 says only "build `moving` the same way".
  Close it by saying that both helpers return `exporters` (and the `targets`), and where the third copy of the wiring (`ts/scripts/round-trip.ts`, 499) gets its own.
- **M3 · no named way to make a signed-in person's request** (plan 4:445, 446, 497; plan 3:398, 517 to 528, 458, and the plan 3 diff 9988813..9ac93ac).
  The import tests need the person (`project-create`, `import`, `export-target` with the session cookie and the server's `Origin`).
  Plan 3's fix round 4 removed `asPerson` from `TestServer` and `Project`; `TestServer.approve` is the only person's call left, `world.ts` holds an agent token only, and plan 3 names no helper that signs in.
  Plan 3 also states the token's rule for `project-create` (396) and not whether a session may call it.
  Close it by naming the helper (or telling Task 8 to add one to `world.ts` from plan 3's `SoftAuthenticator` and `issueSetupCode`, 421 to 460) and stating the session may create a project.
- **M4 · Task 10's harness is not named, and two of its assumptions fail on the e2e one** (plan 4:443, 497, 499; plan 3:517 to 534).
  `round-trip.test.ts` lives in `ts/tests/e2e/`, whose `testServer()` has the person `author` (plan 3:530), so the mapping `decided_by: author` to the person is a no-op (Task 5's `owner_named_author_changes_nothing`, 334) and the test's "read the person's name" assertion has nothing to see; and `TestClock.sleep` is specified only for the stood-still mode (plan 3:517, 531), so `await clock.sleep(432000)` (443) may not move the minute clock past 2026-11-02T18:56:30+01:00 (check 1 then fails).
  With `world.ts` (person `ada`, `FixedClock`) both hold.
  The script `ts/scripts/round-trip.ts` cannot import `src/main.ts`, so its "real clock" (499) is its own, unstated.
  Close it by naming `world.ts` (or giving `testServer()` a person parameter and a defined `sleep`).
- **M5 · the attachment of the round trip has no helper** (plan 4:197, 497).
  `zeroTwoRepository(layout)` takes no extra file, and 497 adds an attachment of the bytes `\xff\xfe` "to the branch layout's store".
  Task 2's `commit(repo, path, text, message)` carries text (196), and a file of two non-UTF-8 bytes needs `encodeUtf8` of U+DCFF U+DCFE written by the test.
  Close it by giving `zeroTwoRepository` an `extra` parameter or by saying the test writes the file itself.
- **M6 · exports with no named reader in their task** (plan 4:33 against 170, 176, 257 to 264, 301 to 309, 352 to 364, 431).
  Line 33 says every export a task adds has a reader in that task, so knip (with `includeEntryExports`, plan 3:63) passes; plans 2 and 3 keep a "read in a later task" table for the names that do not.
  Not shown to have a reader: `GitDone`, `StoreRead` (Task 2); `HookContext`, `Resolve`, `HookOutput` (Task 4; Task 9's `hookContextFor` returns an inline type, 469); `PreparedImport`, `Imported` (Task 5); `ExportTarget`, `ExportOutcome`, `ExportTargets`, `ExportPorts` (Task 6, whose first named reader is Task 7, 407, or Task 8); `Moving` (Task 8, 431).
  Close it by naming a reader (a test that annotates with the type), by `knip.json` `entry` in the task and out in the reader's, or by not exporting the type.
- **M7 · Task 6 reads Task 1's store and the fake takes records** (plan 4:349, 390; plan 2:264).
  Task 6's Consumes omits Task 1 though Task 1 (146) lists Task 6 as a reader.
  `export_files_hold_the_store_and_kept` holds "the made-up store's records" in a `MemoryStore`, whose constructor takes `(Area | Decision | SpecEntry)[]`, so the thread and the attachment cannot be passed as items; the test has to write them through `publish` or the fake's `files`, which 390 does not say.
- **M8 · an unknown project answers differently** (plan 4:411, 439, 440, 447; plan 3:394).
  `import` answers `no-project` for `projects.settings(project)` null, `export-target` reaches Task 7's `NotFound` (`not-found`, 404), and `export-target.test.ts` has no test for it.
  Close it by one rule for both, and a test.
- **M9 · Task 7 drops the read-before-write rule** (plan 4:408; plan 2:191, d-thvvzx).
  `setTarget` must find out whether the project exists before it appends; plan 2 requires such a transaction to open with a write on the `heads` row.
  Task 7 says "appends one event" and `NotFound` and nothing on how.
- **M10 · `exporters.start` runs for `setup` too** (plan 4:441; plan 3:421 to 428).
  `open(data)` serves `serverCommand`'s `setup` as well as `serve`, and `ServerParts` has only `options`, so a `start` in `open` (not awaited) has no serve-only place.
  On a fresh `setup` there are no projects, so it is a no-op; on a second `setup` before a passkey it starts exports in a process that then exits.
- **M11 · three different pins for plan 3, two for plan 2** (plan 4:17; ledger, "Alignment" line; heads).
  Plan 4 says plan 2 a035344 and plan 3 9988813; the ledger says plan 2 a035344 and plan 3 7dfdf40; the branches are at 0244e79 and 9ac93ac.
  I diffed both plan texts against the pins in plan 4:17: nothing plan 4 consumes changed (plan 3's `asPerson` removal is M3).
  Close it by one pin per plan, re-stated at the next alignment.
- **M12 · the names table is mislabelled** (plan 4:61, 75, 428).
  The heading says "from plans 2 and 3", and row 75 (line 75) is plan 1's names; row 81 lists a "TOML conversion" that is no name (M1); `START` (read at 293, 334) is missing from row 77.
- **M13 · line 108 lists the shared files incompletely** (plan 4:108, 148).
  Tasks 2 and 4 both edit `ts/package.json`'s `imports`, and Tasks 2, 4, and 9 `ts/tests/parity.json`; only `index.ts`, `front-door.test.ts`, `events.ts`, `main.ts`, and `cli/index.ts` are named.
  Textual conflicts only.
- **M14 · `CLAUDE.md` names the frozen documents twice** (plan 4:540).
  Line 8 ("Both design documents … are frozen history") and line 33 ("both design documents and the done ledger") both go stale; 540 says one line.
- **M15 · a required `moving` breaks other `ApiOptions` literals** (plan 4:429, 423 to 424; plan 3:421 to 428, 459).
  Task 8's Files list `world.ts` and `server.ts`; plan 3's `setup.test.ts` builds a `ServerParts { options }` over the store (`open`), and any other literal of `ApiOptions` fails `tsc` unless it spreads the world's.
  Not verifiable until plan 3 is built; close it by making `moving` optional with a refusal, or by naming every builder.
- **M16 · no registration point and no 422 helper named in plan 3** (plan 4:423, 438, 439; plan 3:386, 392, 442 to 443).
  Task 8 modifies "its operation table (`ts/src/api/person.ts`)", registers `import` and `export-target` "with the person's operations", and answers `check-failed` "as plan 3 answers a write whose check fails".
  Plan 3 describes the behaviour (the `forbidden` sentence, the 422 body with `result`) and names no table, registration function, or answer helper; 63 of plan 4 already sends the coordinator to the merged code, but the Files and the test lists of Task 8 depend on the shape.
- **M17 · `main.ts`'s wiring is not under test** (plan 4:441, 448).
  `failed` (the log line `lodge: the export of <project> failed: <message>`) and `exporters.start` are in `main.ts`, which no test imports, and 448 says no test makes an export fail; the line is pinned by nothing except the coordinator's reading.
- **M18 · wording of a test** (plan 4:279).
  `moved_record_edit_names_the_server` asserts "not `lodge/decisions` as a place to edit", but the moved text carries `{path}`, a path under `lodge/decisions/`; the assertion has to name a phrase of the Python text that is gone ("do not edit it by hand" or "outside `lodge/`"), not the folder.
- **M19 · the stand-in's people** (plan 4:335; plan 2:560).
  `import-store.test.ts`'s `MemoryStore` must be built with `people` `{owner}`; its default is `{author}`, with which the mapped state is checked as if the owner's decisions were roles (320, 321).

Preconditions, not mismatches:
- C12: the d-d0vca9 write rule is not in plan 1's code at 7d5ecbc; Tasks 6, 8, and 9 cannot pass `check-ts.sh` until it lands (25).
- C21, C22, C25: Task 5 needs plan 2's Tasks 10 and 11 merged, Task 6 needs 12a; the lanes table has both (99, 100).

Files read: all those under "Sources read" above, plus `ts/src/core/{index,snapshot,model,settings,threads,fileformat,check-change,check-state,derive,stamps}.ts` of plan 1, plan 4's whole text, ledger, `probes.md`, `questions.md`.
Files not read: see the header.
