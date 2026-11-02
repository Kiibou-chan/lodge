# Plan review, practice angle: plan 4, the importer, the export, and the design's records

Reviewer: practice angle, from the builder's seat (Codex, one task per brief, no network, no sockets, read-only git index).
Plan under review: `docs/superpowers/plans/2026-11-02-lodge-server-import.md` at 6c6322c on `server-import`.
Probes ran in a detached scratch worktree at `origin/server-core` 579fb11 (`.claude/worktrees/p4-practice`), with `server-core`'s installed `node_modules`.
Status: done.

## Findings

### P4-B1 (Blocking): `checkState` takes no settings, and three tests expect problems that no state check gives

Handle: plan line 143 (Task 1: `checkState(load(tree(...)), parseCoreSettings(...))`), lines 299 and 303 (Task 5: `checkState(load(tree(...)), coreSettings(copy.settings))` and `checkState(..., settings)`), line 314 (`failing_store_prepares_nothing`: emptied `[import]` sources give "lodge 0.2's check problem for the imported decision"; `mapped_state_is_checked_with_the_project_settings`: `[length] title_chars = 10` gives `stage` `"server"`), line 421 (Task 8's `failing_store_answers_check_failed`, the same emptied sources answering 422).
`checkState(s: Snapshot): CheckResult` takes one argument (`ts/src/core/check-state.ts:133` on `server-core` 579fb11, as `check_state(s)` at `src/lodge/core/check_state.py:25`); the unlisted-source problem is check 4 of `checkChange`, and only for a decision new against the published state (`src/lodge/core/check_entries.py:73-84`); `[length]` feeds `feedback.py` only and is never a check problem (`grep -rn title_chars src/lodge/core` hits `feedback.py` alone).
Verified: lodge 0.2's `lodge check` on the made-up store of `probes/zero-two-store/` committed in a scratch repository prints `ok` as given, `ok` with `sources = []` (and `ok` for `--gate`), and `ok` with `[length] title_chars = 10`.
Verified: `core.check_change(load(<empty tree>), load(<the store>), settings, 2026-11-03T00:00Z)` gives no problem with the store's settings and exactly `d-40q44p: imported from docs/choices.md, which is not listed in [import] sources` (check 4) with `sources = []`.
Failure: `tsc` refuses the two-argument call (TS2554) in Task 1, which the coordinator meets first, and in Task 5; if Codex drops the second argument to compile, `failing_store_prepares_nothing`, `mapped_state_is_checked_with_the_project_settings`, and Task 8's `failing_store_answers_check_failed` cannot pass, since the state check finds nothing in either store; Codex then stops BLOCKED or bends the tests, and d-ag8p8h's handle (`test_import_from_an_unlisted_source_fails_the_check`) is a test of `lodge add`, not of `lodge check` on a store at rest.
Fix: in Task 1 call `checkState(load(...))` with one argument; in Task 5 check both stages as a change from the empty state, `checkChange(load(tree({ rev: null, files: new Map() })), load(tree(...)), settings, now)`, which gives the store's settings a meaning (check 4) and refuses decisions dated after the import (check 1); `prepareImport` then needs `now: string` and `importStore` a `Clock` (plan 2's, as `app` takes time; Task 8 passes plan 3's `ApiOptions.clock`); replace the `[length]` test by project settings without the store's `[import]` source, which fails at `stage` `"server"`; since the server stage then needs the project's settings to list the store's sources, say so in Tasks 8 and 10 (the project of `import.test.ts`, `round-trip.test.ts`, and `ts/scripts/round-trip.ts` is created with the store's `[import]` table; lodge's own store holds 69 records with `imported_from`, `git grep -l '^imported_from' -- lodge | wc -l` at 6c6322c); record the correction to d-ag8p8h's reasoning with `lodge add`, since it is the planner's ruling.

### P4-I1 (Important): a call through a parameter named `write` fails the structure test in `hook`, `app`, and `main.ts`

Handle: plan line 251 (`run(read, write, context, resolve, cwd)` in `#hook`), line 342 (`ExportPorts.write`, called by `Exporters` in `ts/src/app/exporters.ts`, line 361), line 450 (`main.ts` gives `process.stdout`'s write), line 417 (`failed` writing on standard error in `main.ts`); `ts/tests/structure/calls.ts` on `server-core` 579fb11, whose `writes` set holds `write` and which reports any call whose callee's last name is in it, outside `git`, as "file writing outside git" (d-mfskz3).
Verified: in the scratch worktree, a `src/hook/post-tool-use.ts` whose `run` calls its `write` parameter, a `src/app/exporters.ts` calling `this.ports.write(...)`, and a `src/main.ts` calling `process.stdout.write(t)` each gave `file writing outside git` from `callViolations`.
Failure: Tasks 4 and 6 are built as the interfaces say, `sh scripts/check-ts.sh` fails on the structure test, and Codex either renames a member the plan fixes (and Task 8's `tsc` check of `exportStore` as `write` and Task 9's wiring then disagree with the brief) or stops BLOCKED; the CLAUDE.md rule forbids loosening the check.
Plan 3 already avoids it by naming its output functions `out` and `err` (plan 3, `Io` and `ServerIo`).
Fix: rename the members in the plan before the build: `#hook`'s `run(read, out, context, resolve, cwd)`, `ExportPorts.commit` (or `exportTo`) for the exporter's writer, and in Tasks 8 and 9 hand `main.ts`'s existing `io.out` and `io.err` of plan 3 to the hook and to `failed` rather than `process.stdout.write`; add one line to the Global Constraints: "no function or member that `src/` outside `git` calls may be named `write`, `writeFile`, `mkdir`, `rm`, or another name of `calls.ts`'s `writes` set".

### P4-I2 (Important): in Bun a spawn without `env` ignores `isolateGit()`'s changes to `process.env`, so a test helper can reach the real git configuration

Handle: plan line 183 (`isolateGit()` "registers `beforeEach` and `afterEach` hooks setting and restoring the variables", and deleting `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, and `GIT_COMMON_DIR`), line 184 (`repos.ts` carries `git`, `commit`, and the rest), line 451 (Task 9's `hookProject()` with its own `git(...args)`), line 31 (the Global Constraint on git in tests); `CLAUDE.md`, "Hard rules" (`GIT_CONFIG_GLOBAL` empty, `GIT_CONFIG_NOSYSTEM=1`).
Verified with Bun 1.3.14: after `process.env.FOO_PROBE = "mutated"`, `Bun.spawnSync(["sh", "-c", "echo $FOO_PROBE"])` with no `env` prints an empty line, as does `node:child_process`'s `spawnSync`, while `{ env: process.env }`, `{ env: { ...process.env } }`, and `Bun.$` print `mutated`; under `bun test`, a variable set in `beforeEach` is likewise absent from a spawn without `env` (the probe's test failed); and `process.env.PATH = "/nonexistent"` leaves a later spawn's `PATH` as it was at start.
Failure: a builder ports `repos.py`'s `git()` or writes `hookProject().git` as `Bun.spawnSync(["git", ...])`, the natural form; outside the sandbox the coordinator's `sh scripts/check.sh` then commits with her global configuration and identity (and her hooks or signing settings, if any), and inside it a commit fails for want of an identity, or, when the gate runs under a git hook with `GIT_DIR` set, the helper writes into the lodge repository itself; no planned test notices, since every test still passes on a machine with a global identity.
Fix: state in Task 2 that `attempt` builds `{ ...process.env, LC_ALL: "C", GIT_TERMINAL_PROMPT: "0", ...env }` at each call and passes it as `env`, and that every test helper spawns git only through `#git`'s `run` or `attempt` (or with `env: { ...process.env }`); add `isolation_reaches_git` to `run.test.ts` (inside `isolateGit()`, `run(["var", "GIT_AUTHOR_IDENT"], repo)` starts `Test Author <test@example.com>` and `run(["config", "--global", "--list"], repo)` is empty) and its twin for `repos.ts`'s `git` helper, each seen failing against a helper that drops `env`.

### P4-I3 (Important): `missing_git_is_one_sentence` with `PATH` emptied finds git all the same

Handle: plan line 188 (`missing_git_is_one_sentence`: "with `PATH` emptied for the call, `attempt` throws a `GitMissing`"); `tests/gitstore/test_setup.py:97-98` sets `PATH` to an empty folder, not to the empty string.
Verified with Bun 1.3.14: `Bun.spawn(["git", "--version"], { env: { ...process.env, PATH: "" } })` runs git and exits 0; with `PATH` an empty folder, or `/nonexistent`, it throws `ENOENT` with `Executable not found in $PATH: "git"`; setting `process.env.PATH` without passing `env` does not take effect (P4-I2).
Failure: Codex writes the test as worded, `attempt(["--version"], dir, { PATH: "" })` succeeds, and the test cannot go green without changing what it says; Codex either bends `attempt` to treat an empty `PATH` specially or stops.
Fix: word it as the Python test does: `attempt(["--version"], dir, { PATH: <an empty folder from mkdtempSync> })` throws a `GitMissing` with its sentence; and state that `GitMissing` is the `ENOENT` that `Bun.spawn` throws, whose `code` is `ENOENT`.

### P4-I4 (Important): `#app`'s front-door test refuses every name Tasks 4, 5, and 6 export, and no task may edit it

Handle: plan 2's Task 6 creates `ts/tests/app/front-door.test.ts`, whose `front_door_exports_nothing_else` "finds every other export among this plan's additions", a closed list (plan 2 at 7204ad3, line 333); plan 3's Task 4 lists that file in its Files to add its names (plan 3 at 3e4c29c, lines 265 and 322); this plan's Tasks 4, 5, and 6 add `parseHookSettings` (line 239), `ZeroTwoCopy`, `PreparedImport`, `Imported`, `prepareImport`, `importStore` (lines 281-296), and `ExportTarget`, `ExportOutcome`, `ExportTargets`, `ExportPorts`, `EXPORT_INTERVAL_SECONDS`, `KEPT`, `exportFiles`, `exportMessage`, `Exporters`, `exportingProjects` (lines 332-355) to `ts/src/app/index.ts`, and none of their Files (lines 233-234, 273-275, 324-326) names `front-door.test.ts`; `grep -n front-door` on the plan finds nothing.
Failure: each of the three lanes turns the front-door test red the moment it re-exports its names; the Global Constraint "every existing test keeps passing, edited only where a task says so" (line 26) forbids the edit that fixes it, so Codex stops BLOCKED three times, or edits the list in three parallel lanes and the merges conflict on the same lines.
Task 4 waits only for plan 2's Task 2 (line 90), so it can also land before plan 2's Task 6 creates the test; then the merge of plan 2's Task 6 into `server-import` is the commit that turns red, on `parseHookSettings`, in a test plan 4 never touched.
Fix: add `ts/tests/app/front-door.test.ts` ("the additions it allows") to the Files of Tasks 4, 5, and 6 with the names each adds, and to line 100's list of files whose merge keeps both sides' lines; have Task 4 wait for plan 2's Task 6, as Tasks 5 and 6 already do through Tasks 11 and 12.

### P4-I5 (Important): `exportingProjects` forwards `create` with plan 2's two parameters, and plan 3's third parameter then drops the project's settings without a type error

Handle: plan line 365 ("every other method of `Projects` ... passes to the inner one unchanged"), line 399 (Task 8 forwards "plan 3's `settings` and `names`" only), line 413 (`ApiOptions.projects` is `exportingProjects` over `SqliteProjects`); plan 2's `Projects.create(project, owner)` (plan 2 at 7204ad3, line 111), widened by plan 3's Task 4 to `create(project, owner, settings?)` (plan 3 at 3e4c29c, line 308), which `project-create` calls with the settings (this plan, line 78).
Verified: `tsc` 6.0.3 with `--strict --exactOptionalPropertyTypes` accepts `create: (project, owner) => inner.create(project, owner)` as the three-parameter `create` (exit 0 for that object), and refuses an object missing `names` (TS2741).
Failure: Task 6, built against plan 2's `Projects`, writes the two-parameter forwarder; after plan 3 merges, Task 8 adds `settings` and `names` as told, `tsc` stays green, and every project created through the API loses its settings, so `projects.settings(project)` answers `{}` and the import checks against defaults; separately, the merge of plan 3 into `server-import` is red until Task 8 lands, since Task 6's wrapper and the fake `Projects` of `import-store.test.ts` (line 315) and `exporting.test.ts` lack `settings` and `names`, and Task 8's Files do not name those test files.
Fix: say in Task 6 that every forwarded method passes its arguments through as a rest parameter (`create: (...args) => projects.create(...args)`), and give `wrapped_store_passes_every_other_method` a `Projects` case per method that asserts the arguments reach the inner one; in Task 8, name `ts/tests/app/import-store.test.ts` and `ts/tests/app/exporting.test.ts` beside `exporting.ts`, and add a test that `project-create` with settings through the wrapped `Projects` gives them back from `settings`; or have Task 6 wait for plan 3's Task 4, so the wrapper is written once against the final interface.

### P4-I6 (Important): the made-up store prepares eight files, not nine

Handle: plan line 314 (`clean_store_prepares_every_file`: "nine files: four decisions, one entry, one area, one thread, one attachment, and no `.gitkeep`"), line 315 (`owner_imports_into_an_empty_project`: "one publish of the nine files"); `probes/zero-two-store/lodge/` holds ten files, two of them `.gitkeep` (`find ... -type f`), and the items listed add up to 4 + 1 + 1 + 1 + 1 = 8.
Failure: Codex asserts `files.size` 9 as written, the test fails against a correct `prepareImport`, and Codex either bends the code (keeping one `.gitkeep`, against step 3 at line 302) or stops; the reviewer then reads a correct test as wrong or the reverse.
Fix: "eight files" in both tests, and name them by path from `ZERO_TWO_STORE`, so the count is checked against the fixture rather than a numeral.

### P4-I7 (Important): `moved_remote_branch_answers_moved` needs a seam `exportStore` does not have, and the local `moved` has no test

Handle: plan line 224 (`moved_remote_branch_answers_moved`: "a commit pushed to the remote by a second clone after the export's fetch and before its push"), line 211 (`exportStore(target, files, message)`, one call with nothing between the fetch and the push), line 221 (`update-ref` with the old value answers `moved`, no test names it); lodge 0.2 reaches the same window with a rigged remote whose `pre-receive` hook moves the branch once (`tests/gitstore/test_push_race.py:35-57`, `rigged_remote`).
Failure: Codex cannot place a second clone's push inside one `exportStore` call; it either runs the second push before the export (then step 2's `fetch` sees the new tip and the export commits on it, so the test asserts `moved` and gets `committed`), or adds a parameter to `exportStore` that Task 8's `tsc` check against `ExportPorts.write` then refuses; the `update-ref` branch of step 7 ships untested.
Fix: name `rigged_remote` of `test_push_race.py` as the way to build the race (a `pre-receive` hook in the bare remote moving the branch to a second clone's commit once, with the three `GIT_QUARANTINE_PATH`, `GIT_OBJECT_DIRECTORY`, and `GIT_ALTERNATE_OBJECT_DIRECTORIES` unset), carried into `repos.ts`; for the local case add `moved_local_branch_answers_moved` with a `reference-transaction` hook, or state that the local race is left untested and why.

### P4-I8 (Important): Task 2 creates `repos.ts` helpers that only Task 3 reads, so knip fails Task 2's gate

Handle: plan line 184 (`repos.ts` carries `git`, `bareRemote`, `clone`, `seeded`, `worktree`, `commit`, and `write`), line 30 ("every export a task adds has a reader in that task, its own tests counting"); Task 2's tests (line 188-190) need repositories and commits but no bare remote, clone, or second work tree, which only Task 3's tests use (`push_without_force`, `moved_remote_branch_answers_moved`, `checked_out_branch_is_refused`, `branch_with_other_files_is_refused` on `seeded`, line 224).
Verified: in the scratch worktree, a `tests/gitprobe/repos.ts` exporting two functions of which a test imports one made knip 6.42.0 print `Unused exports (1)` with the other; plan 1 lost rounds to the same bookkeeping (dispatch).
Failure: Codex ports `repos.py` whole in Task 2 as told, `check-ts.sh` fails on knip, and the builder either deletes helpers the plan lists or writes a test that exists only to read them.
Fix: Task 2's `repos.ts` carries the helpers its own tests call (name them); Task 3's Files gain `ts/tests/git/repos.ts`, adding `bareRemote`, `clone`, `seeded`, and `worktree` (and the rigged remote of P4-I7).

### P4-I9 (Important): in the branch layout `.lodge.toml` is not at the commit `readStore` reads, so `reads_the_branch_layout` cannot hold

Handle: plan line 185 (`zeroTwoRepository("branch")`: records on an orphan branch `lodge` holding only `lodge/`, "`.lodge.toml` on `main` in both", `rev` "the commit holding `lodge/`"), line 179 (`readStore` "reads `.lodge.toml` at the commit ..., null when there is none"), line 189 (`reads_the_branch_layout` expects ".lodge.toml's text in `settings`"); lodge 0.2's branch mode commits only `KEPT` to the branch (`src/lodge/gitstore/branch.py:169`), so a real branch-mode store never has `.lodge.toml` beside its records.
Failure: Codex implements `readStore` as line 179 says and `reads_the_branch_layout` fails on `settings`, or makes the test pass by reading `main`'s `.lodge.toml`, which the interface does not say; either way the import of a branch-mode store reaches `prepareImport` with `{}` settings, and once the check uses the store's `[import]` sources (P4-B1) every imported decision of such a store fails check 4, which `person_imports_the_made_up_store` (both layouts, line 421) and the round trip (line 470) then show.
Fix: give `readStore` (and the `import` operation, d-1skjw1) a second revision for the settings, `readStore(repository, rev, settingsRev = rev)`, the branch layout's test passing `main`; or state that `readStore` reads `.lodge.toml` at `rev` and else at `HEAD`, and test both; record the choice with the planner's ruling.

### P4-I10 (Important): `post-tool-use.test.ts` will pass 300 lines, and the plan names one file

Handle: plan line 235 (one test file for every test of `tests/hook/test_post_tool_use.py` and six new ones), line 29 (no file over 300 lines; `sizeViolations` counts `tests/`, `ts/tests/structure/calls.ts`); `tests/hook/test_post_tool_use.py` is 253 lines with 24 tests (`wc -l`, `grep -c "def test_"`), and plan 2's practice review measured plan 1's ported test files at a median of about 1.1 times their Python lines (its P-I5).
Failure: 253 at 1.1 is about 280 before the six moved-advice tests, each with its context object and three or four assertions; Codex writes the file whole, the structure test fails on size, and splitting it means a second file the Files list and the parity row's `ts` do not name.
This is an estimate from plan 2's measured ratio, not a port.
Fix: name the split now: `post-tool-use.test.ts` for the carried tests and `moved-advice.test.ts` for the six new ones, with the parity row's `ts` naming the carried file and Task 10's `rowMissing` reading only it.

### P4-I11 (Important): `Bun.spawn` with piped output hands git sockets, in a sandbox that refuses sockets, and the plan's evidence is for Python

Handle: plan line 178 (`attempt` spawns "with `Bun.spawn`"), line 22 ("sockets are refused"), line 23 (the evidence that git works in the sandbox: lodge 0.2's Python tests, `task-5-report.md:102` of an earlier plan); plan 1's only spawning test, `ts/scripts/differential.test.ts:15,43,61` on `server-core`, uses `Bun.spawnSync`.
Verified with Bun 1.3.14 outside the sandbox: a child of `Bun.spawn(..., { stdin: <bytes>, stdout: "pipe", stderr: "pipe" })` reads `/proc/self/fd/1` and `/2` as `socket:[…]` (a socket pair), and its standard input as `memfd:spawn_stdio_stdin`; a child of `Bun.spawnSync` has `memfd:` files for both.
Not verified: whether Codex's sandbox refuses a Unix socket pair, as against a network socket; I could not run inside it.
Failure: if it does, every git test of Tasks 2, 3, 8, 9, and 10 fails inside the sandbox with a spawn error, Codex cannot see red turn green for a reason of its own, and the builder's gate (`check-ts.sh`, line 24) is red while the coordinator's outside is green, which is the state in which plan 1's reviews found whole-function reds.
Fix: before Task 2, the coordinator runs one `codex exec` probe in the sandbox, `bun -e 'const p = Bun.spawn(["git", "--version"], { stdout: "pipe" }); console.log(await p.exited, await new Response(p.stdout).text())'`, and records the answer in the ledger; if it fails, Task 2 says `attempt` uses `Bun.spawnSync` (34 ms for a 402-file export by probe 4, acceptable for step 1's one-minute batches), or that the git tests run only in the coordinator's gate, named as such in each brief.

### P4-M1 (Minor): `resolve_rev_refuses_an_option` cannot fail, since `^{commit}` is appended to the argument

Handle: plan line 188 (`resolveRev(repo, "--output=x")` "writes no file named `x`, since `--end-of-options` comes first"); `resolve` of `src/lodge/gitstore/git.py:81-88` has no `--end-of-options`.
Verified: with git 2.56.0, `git rev-parse --verify --quiet '--output=x^{commit}'` exits 1 and writes nothing, with and without `--end-of-options`, and so do `--prefix=x`, `--since=2020`, `--all`, `--abbrev-ref`, `--symbolic`, and `--show-toplevel`, each with `^{commit}` appended.
Failure: the test is red only while the module is missing, the whole-function red of plan 1, and stays green against a mutation that drops `--end-of-options`; the report cannot name a mutation that kills it, as line 26 asks.
Fix: drop the test and keep `--end-of-options` as defence, or move the guard to a place a test can reach (for example `readStore` refusing a `rev` that starts with `-` with its own sentence) and test that.

### P4-M2 (Minor): "reads as its target's text" invites dereferencing a symbolic link

Handle: plan line 189 (`symbolic_link_reads_as_its_target`: "a link committed under `lodge/` reads as its target's text, as `read_tree` reads a blob of mode 120000"); `read_tree` decodes the blob, which for mode 120000 is the link's target path (`src/lodge/gitstore/trees.py:37-43`).
Failure: Codex reads "its target's text" as the text of the file the link points to and writes a test committing a target file and expecting its content, which `cat-file --batch` never gives.
Fix: "reads as the path the link names, the blob's text".

### P4-M3 (Minor): `exportingProjects` takes the class `Exporters`, so the planned stand-in does not type-check

Handle: plan line 355 (`exportingProjects(projects: Projects, exporters: Exporters)`), line 368 (`wrapped_store_tells_the_exporter_after_a_publish` with "a recording `Exporters` stand-in").
Verified: `tsc` refuses `{ written: async (p) => { … } }` for a parameter typed as a class with a private field and a `#private` one (TS2345, "missing the following properties from type 'Exporters': #runs, ports").
Failure: Codex casts the stand-in (`as unknown as Exporters`), which Biome or the review then flags, or builds a real `Exporters` with recording ports, which tests two units at once.
Fix: type the parameter as what the wrapper calls, `exportingProjects(projects: Projects, written: (project: string) => void)`, and have `main.ts` pass `(project) => void exporters.written(project)`.

### P4-M4 (Minor): `writes_within_a_minute_share_one_commit` needs a sleep the test can hold, which plan 2's `FixedClock` does not give

Handle: plan line 369 ("three writes 10, 20, and 30 seconds later before the run ends: `slept` holds the rest of the minute once"); plan 2's `FixedClock.sleep(seconds)` adds the seconds and resolves at once (plan 2 at 7204ad3, line 242).
Failure: after the first commit, a write at +10 s starts a run whose `sleep(50)` resolves on the next microtask, so the writes at +20 s and +30 s, made after any `await` in the test, start runs of their own and each commits; Codex either calls `written` three times without awaiting, which tests one instant rather than three, or invents a clock.
Fix: name a test-local clock in `exporters.test.ts` whose `sleep` records the seconds and resolves only when the test calls `release()`, moving the time; the test makes the three writes while the run is held and then releases it.

### P4-M5 (Minor): a target that always fails makes the exporter retry for ever under `FixedClock`

Handle: plan line 362 (a throwing `write` "marks a write pending again after `clock.sleep(EXPORT_INTERVAL_SECONDS)`"), line 418 (`world.ts` builds `moving` with `FixedClock`), line 422 (`person_sets_the_target`, then `void exporters.written(project)` at line 416).
Failure: Codex sets a target whose `repository` is not a repository in `person_sets_the_target`, which only reads the target back; each retry's sleep resolves at once, so the run spawns git, fails, and retries without end in the background of every later test in the file; I did not run this, so whether `bun test` hangs or only slows is not verified.
Fix: say that tests set only targets on a bare repository from `mkdtempSync`, give `Exporters` a `stop()` that ends every run after its current step (the API tests' teardown calls it), and test that `failed` is called once per minute of the clock, not once per microtask.

### P4-M6 (Minor): `hookProject().initialise()` must stage the two files, as `lodge init` does

Handle: plan line 451 (`initialise()` "making `lodge/decisions/.gitkeep` and `lodge/spec/.gitkeep` where the Python test ran `lodge init`"); `init_store` ends with `git add -- KEPT` (`src/lodge/gitstore/setup.py:56`); `test_hook_finds_the_repository_of_the_edited_file_not_of_the_session` commits right after `init` and then adds a work tree (`tests/e2e/test_hook_feedback_after_hand_edits.py:30-37`).
Failure: `git commit -m Store` exits 1 with nothing to commit in the fresh repository of `hookProject()`, so the carried test fails for a reason outside the hook.
Fix: "`initialise()` writes the two files and stages them with `git add`, as `init_store` does".

### P4-M7 (Minor): `export_of_an_export_is_unchanged` asks for an outcome `Exporters` does not expose

Handle: plan line 470 ("a second flush answers `unchanged`"); `Exporters` has `written`, `start`, and `settled`, none giving `write`'s outcome (lines 349-354).
Failure: Codex adds a getter for the last outcome to `Exporters`, an export only a test reads, or calls `exportStore` directly, which skips the exporter the test is about.
Fix: "a second `written` and `settled()` leave the exported branch's tip where it was".

### P4-M8 (Minor): a required `Io.hook` makes Task 9 edit every `Io` of plan 3's tests, one of them a file Task 8 edits at the same time

Handle: plan line 445 (`Io` gains `readonly hook`), line 452 ("Every other `Io` the tests build gains `hook: async () => 0`"), line 399 (Task 8 modifies `ts/tests/e2e/server.ts`), line 94 (8 beside 9).
Failure: Task 9's Files cannot list the test files it must touch ("every `Io` the tests build"), and Tasks 8 and 9 conflict in the e2e helpers on merge.
Fix: list the files from plan 3's merged tests (`grep -rln "version:" ts/tests` on the merged branch, by the coordinator, into the brief), or make the member optional (`readonly hook?: () => Promise<number>`), with `run` answering 0 when it is absent, so only `main.ts` and `hookProject()` give one.

### P4-M9 (Minor): Task 7 and plan 3's Task 4 both add cases to `store/events.ts`, which the merge list does not name

Handle: plan line 379 (Task 7 modifies `ts/src/store/events.ts`), line 100 (the files whose merge keeps both sides), plan 3 at 3e4c29c, line 265 (its Task 4 modifies `events.ts` and `schema.ts`).
Failure: plan 3 merges into `server-import` after Task 7 (line 94), both add `case` arms at the same switch, and the coordinator meets a conflict the ledger did not warn of.
Fix: add `ts/src/store/events.ts` to line 100's list.

## Verified, no finding

- The public-repository rule: `probes/fixture.py` reads only the folder it is given and writes a comment naming the probe; the eleven files of `probes/zero-two-store/` are a made-up project (`storage`, transcripts, logs, `docs/choices.md`, `ITEM-1`, `sizes.csv`), lodge 0.2's own output (probe 6); `grep -rnE "/home/|kiibou|/var/tmp|svenja|gmx|\.cache"` over the plan, the ledger, and the folder finds only the worktree path in `planner-brief.md:3`, which is the coordinator's brief and not a plan file.
- The fixture is stable under the writers the importer leans on: lodge 0.2's `write_record(parse_record(...))` gives back each of the four decisions and the entry byte for byte, and `write_thread(parse_thread(...))` the thread (scratch run), so `file_the_writer_would_not_give_back_is_refused` is not set off by the fixture itself.
- lodge 0.2's `lodge check` prints `ok` on the fixture committed in a scratch repository, as probe 6 says.
- `input_reaches_git`'s hash: `printf 'a\n' | git hash-object --stdin` prints `78981922613b2afb6025042ff6bd878ac1994e85`.
- The structure table on `server-core` 579fb11 already holds `git` and `hook`, each importing `app` and `core` (`ts/tests/structure/table.ts`); dependency-cruiser confines `child_process` to `git` and `fs` to `git` and `cli`, and `calls.ts` exempts `git` from the spawning and file-writing rules, so `Bun.spawn`, `realpathSync`, and `mkdtempSync` in `ts/src/git` pass, and `hook` may use `node:path`.
- The lanes' waits against each test file's imports, beyond P4-I4 and P4-I5: Task 2's tests read `#git`, `#core`'s codec (plan 2's 7a), `#app`'s `LodgeError` (plan 2's 2), and Task 1's fixture; Task 3's read Task 2's; Task 4's read `#hook` and `#app` only (`tests/hook/test_post_tool_use.py:8-9` imports `lodge.app` and `lodge.hook` alone); Task 5's read `#core`'s people functions (plan 2's 10, before its 11), `MemoryStore`'s `people` (plan 2's 11), and the fixture; Task 6's read `Store`'s Task 12 methods and `attachmentTexts` (plan 2's Task 2, line 97 of plan 2); Task 7's read `openDatabase`, `rebuild`, and `Tables` of `#store` (plan 2's 7a and 7b); no test of a lane imports a module another running lane creates.
- No step needs the network or a server socket: every remote is a bare repository named by its path, the API tests call the handler with a `Request`, and the only binary run (Task 9's Step 5) and the round-trip script are the coordinator's, outside the sandbox.
- No builder step writes the lodge repository's index: Tasks 2 to 10 run git only in folders from `mkdtempSync`, and Tasks 11a to 11c use the `.drafts/index` copy of the viewer plan (line 34).

## Not verified

- Whether Codex's sandbox refuses the Unix socket pair `Bun.spawn` makes (P4-I11); I ran every probe outside it.
- Whether the endless retry of P4-M5 hangs `bun test` or only slows it.
- The 300-line estimate of P4-I10 is from plan 2's measured ratio, not a port.

## Files read

The plan, its ledger, `planner-brief.md`, `planner-report.md`, `probes.md`, `questions.md`, `probes/fixture.py`, and the eleven files of `probes/zero-two-store/`; `CLAUDE.md`; plan 2 at 7204ad3 (interfaces, lanes table, Tasks 2, 6, 7a, 7b, 11, and 12 by grep and excerpt) and its practice review; plan 3 at 3e4c29c (Tasks 4 and 5 interfaces, `Io`, `ServerIo`, Task 7a's Files); plan 1's ledger at 579fb11 (grep); plan 1's `task-12-report.md`; d-ag8p8h through `lodge show --reasoning`; on `server-core` 579fb11: `ts/tests/structure/calls.ts`, `table.ts`, `ts/.dependency-cruiser.cjs`, `ts/knip.json`, `ts/package.json`, `ts/src/core/snapshot.ts:1-40`, `check-state.ts:120-150`, `check-change.ts:18-25`, `ts/scripts/differential.test.ts` (spawn lines); lodge 0.2's `src/lodge/core/check_entries.py`, `check_change.py:1-100`, `app/reads.py:75-100`, `app/state.py:35-75`, `gitstore/git.py:81-88`, `gitstore/trees.py:23-45`, `gitstore/plumbing.py:50-85`, `gitstore/setup.py:35-70`, `hook/post_tool_use.py:44-56`, `tests/gitstore/test_push_race.py:1-80`, `tests/hook/test_post_tool_use.py` (imports and settings tests), `tests/e2e/test_hook_feedback_after_hand_edits.py:1-40`, `test_hook_outside_repository_exit_0_silent.py`, `tests/e2e/conftest.py:1-70`.
Not read: the server design document, plan 1 in full, plans 2 and 3 beyond the parts named, `probes/decode*.ts`, `export-probe.ts`, `sqlite-surrogate.ts`, the other rulings of the plan (d-1skjw1, d-83kt6y, d-ryss91, d-y42b7b, d-pv341r, d-sj6hmf, d-j5s0h0, d-va3j7x, d-bs5mm8, d-yng7m8), which are the correctness and design angles' ground, and Tasks 11a to 11c against the design's lines.

## Counts

1 Blocking (P4-B1), 11 Important (P4-I1 to P4-I11), 9 Minor (P4-M1 to P4-M9).
