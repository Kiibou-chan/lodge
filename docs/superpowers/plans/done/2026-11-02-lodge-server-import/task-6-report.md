# Task 6 report

Implemented the export file layout, target validation, publication wrappers, and per-project batching.

## Files changed

| File | Change |
|---|---|
| `ts/src/app/exporting.ts` | Defines `ExportTarget`, `ExportOutcome`, and `ExportTargets`, validates targets with the specified sentences, assembles every current file and attachment with the two empty keep files, counts record paths for the commit message, formats failure lines, and wraps projects and stores through bound proxies. |
| `ts/src/app/exporters.ts` | Defines `ExportPorts`, `EXPORT_INTERVAL_SECONDS`, and `Exporters`, retaining commit times separately for each project, coalescing writes while sleeping, retrying moved targets and failures after 60 seconds, starting configured exports, and awaiting active runs. |
| `ts/src/app/index.ts` | Exposes exactly the twelve Task 6 names through `#app`, retaining Task 5's imports. |
| `ts/tests/app/exporting.test.ts` | Adds seven tests for files, messages, refusal sentences, publication notifications, and argument-preserving wrappers. |
| `ts/tests/app/exporters.test.ts` | Adds nine tests for immediate exports, batching, intervals, missing targets, unchanged results, retries, independent projects, and startup. |
| `ts/tests/app/front-door.test.ts` | Adds exactly the twelve Task 6 names to the permitted additions. |
| `docs/superpowers/plans/2026-11-02-lodge-server-import/task-6-report.md` | Records implementation, test-first evidence, commands, and deviations. |

`exporting.test.ts` reads `ExportTarget`, `KEPT`, `exportTargetProblem`, `exportFiles`, `exportMessage`, `exportFailedLine`, and `exportingProjects` through `#app`.
`exporters.test.ts` reads `ExportPorts`, `ExportTargets`, `ExportOutcome`, `Exporters`, and `EXPORT_INTERVAL_SECONDS` through `#app`.
The implementation never imports `#git` from `app`, introduces no dependency, and spawns no process.

## Test-first evidence

Both new test files were written before either implementation module or its front-door exports existed.
Their first run failed at module loading, which the plan explicitly accepts as test-first evidence.
The first error for `exporting.test.ts` was `SyntaxError: Export named 'exportTargetProblem' not found in module` followed by the app front-door filename.
The first error for `exporters.test.ts` was `SyntaxError: Export named 'EXPORT_INTERVAL_SECONDS' not found in module` followed by the same filename.
The command ended with `0 pass`, `2 fail`, and `2 errors`.

| Test | file:line | First failure or mutation |
|---|---|---|
| `export_files_hold_the_store_and_kept` | `ts/tests/app/exporting.test.ts:26` | Missing `exportTargetProblem` export prevented loading the file. |
| `failed_line_names_the_project` | `ts/tests/app/exporting.test.ts:47` | Same initial missing export. |
| `message_counts_the_records` | `ts/tests/app/exporting.test.ts:54` | Same initial missing export. |
| `target_problems_are_named` | `ts/tests/app/exporting.test.ts:63` | Same initial missing export. |
| `wrapped_store_tells_the_exporter_after_a_publish` | `ts/tests/app/exporting.test.ts:89` | Same initial missing export. |
| `wrapped_store_passes_every_other_method` | `ts/tests/app/exporting.test.ts:124` | Same initial missing export. |
| `wrapped_projects_pass_every_method_with_its_arguments` | `ts/tests/app/exporting.test.ts:171` | Same initial missing export. |
| `first_write_exports_at_once` | `ts/tests/app/exporters.test.ts:56` | Missing `EXPORT_INTERVAL_SECONDS` export prevented loading the file. |
| `writes_within_a_minute_share_one_commit` | `ts/tests/app/exporters.test.ts:91` | Same initial missing export. |
| `write_a_minute_after_exports_at_once` | `ts/tests/app/exporters.test.ts:123` | Same initial missing export. |
| `no_target_writes_nothing` | `ts/tests/app/exporters.test.ts:133` | Same initial missing export. |
| `unchanged_counts_no_commit` | `ts/tests/app/exporters.test.ts:139` | Same initial missing export. |
| `moved_retries_a_minute_later` | `ts/tests/app/exporters.test.ts:149` | Same initial missing export. |
| `failure_is_reported_and_retried` | `ts/tests/app/exporters.test.ts:159` | Same initial missing export. |
| `projects_batch_apart` | `ts/tests/app/exporters.test.ts:170` | Same initial missing export. |
| `start_exports_projects_with_a_target` | `ts/tests/app/exporters.test.ts:178` | Same initial missing export. |
| `front_door_exports_nothing_else` | `ts/tests/app/front-door.test.ts:78` | Removed `Exporters` from permitted additions temporarily: expected `[]`, received `["Exporters"]`, ending `1 pass`, `1 fail`, and `2 expect() calls`; restored immediately. |

The files test publishes all eight synthetic fixture files through `MemoryStore.publish` and verifies the exact map in both store modes.
It also verifies that an extra nested keep file is omitted.
The wrappers test successful, rejected, staged, and approving publication, callback timing, bound receivers, argument identity, and returned answers.
The project wrapper also forwards settings, names, and creation settings, which already exist on this branch.
The held clock records a 50-second sleep after a write ten seconds after the first commit, accepts two further writes during that sleep, and verifies exactly two total exports with the latest attachment text.
It verifies that `written` and `settled` remain pending during the wait.
Every retry test has a finite failure sequence and a successful default outcome.

## Commands and results

Read-only inspection used `cat`, `sed`, `rg`, `wc -l`, `git status --short --branch`, `git diff --stat`, and `git diff` on the guidance, requirements, existing interfaces, fixture, structure rules, and changed files.
The branch was `server-import-export`, and the initial working tree was clean.
`uv run --frozen --quiet lodge waiting` ended with `waiting for the author` and `nothing`, with nothing waiting for an agent either.

| Command | Result and last output |
|---|---|
| `cd ts && bun test tests/app/exporting.test.ts tests/app/exporters.test.ts` before implementation | Exit 1; `0 pass`, `2 fail`, `2 errors`, `Ran 2 tests across 2 files`. |
| Same focused command after implementation | Exit 0; `16 pass`, `0 fail`, `82 expect() calls`, `Ran 16 tests across 2 files`. |
| `bunx --no-install biome check --write --error-on-warnings` with the six changed TypeScript paths | Exit 0; initial run fixed five files, and the last run ended `Checked 6 files in 8ms. Fixed 1 file.` |
| `bunx --no-install tsc --noEmit -p .` | Initial exit 2 identified an inferred `remote: null` map and typed identity assertions against generic proxy answers; corrected with an explicit `ExportTarget` annotation and `expect<unknown>`, then exit 0 with no output. |
| `bunx --no-install depcruise src tests scripts --config .dependency-cruiser.cjs` | Exit 0; `no dependency violations found (340 modules, 1266 dependencies cruised)`. |
| `bunx --no-install knip` | Exit 0 with no output. |
| `bun test` | Exit 0; `1954 pass`, `0 fail`, `6739 expect() calls`, `Ran 1954 tests across 178 files`. |
| `cd ts && bun test tests/app/front-door.test.ts` with the temporary mutation | Exit 1; `1 pass`, `1 fail`, `2 expect() calls`, `Ran 2 tests across 1 file`. |
| `sh scripts/check-ts.sh` as the final validation | Exit 0; Biome reported 30 infos, with no warnings or errors, dependency checks passed, and the last lines were `1954 pass`, `0 fail`, `6739 expect() calls`, and `Ran 1954 tests across 178 files`. |

One attempted editing command used a root-relative filename while its working directory was `ts/`, ending `FileNotFoundError` before writing anything.
The immediately following checks therefore repeated the existing type errors.
The edit was rerun from the repository root, and TypeScript then passed.
A search for guessed core filenames also found no such files; the actual `snapshot.ts` was located by content and read.

## Deviations and uncertainties

The plan header asks for an unavailable `superpowers:subagent-driven-development` skill.
The coordinator tool ruled: `Option A: implement Task 6 directly, test-first, no delegation.`
No delegation or skill installation occurred.
The brief overrides the plan's sandbox restrictions on committing and pushing, and specifies the Codex co-author trailer and this branch.
Only the TypeScript gate is run here; the coordinator's whole-repository gate remains its step.
The merged `Projects.create` already accepts settings, so the wrapper test covers that argument here, along with `settings` and `names`, instead of postponing it until Task 8.
There are no unresolved questions or known implementation concerns.
