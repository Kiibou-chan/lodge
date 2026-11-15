# Task 2 report

Implemented the Git process adapter, lodge 0.2 store reader, path helpers, and isolated repository fixtures.

## Files changed

| File | Change |
|---|---|
| `ts/src/git/index.ts` | Exposes the eight required functions and `GitMissing` through `#git`; each export has a reader in this task's tests. |
| `ts/src/git/run.ts` | Runs Git synchronously with an explicit environment, encodes input, preserves output bytes, reports Git's first error line, and resolves commit references. |
| `ts/src/git/read-store.ts` | Resolves both revisions, lists every lodge file, reads unique blobs and settings in one batch, and preserves undecodable bytes and names through the core codec. |
| `ts/src/git/paths.ts` | Resolves existing symbolic links before parent segments, finds the repository above an edited path, and checks folders. |
| `ts/tests/git/isolated.ts` | Sets and restores the isolated Git configuration and synthetic identity for each test. |
| `ts/tests/git/repos.ts` | Carries `git`, `commit`, and `write`, and adds temporary folder and repository helpers with cleanup. |
| `ts/tests/git/zero-two.ts` | Builds checkout and orphan-branch fixtures from `ZERO_TWO_STORE`, with optional encoded extra files. |
| `ts/tests/git/run.test.ts` | Adds five process, reference, input, and isolation tests. |
| `ts/tests/git/read-store.test.ts` | Adds eleven store-reading cases, including both revision refusal cases, byte preservation, names, links, and absent settings. |
| `ts/tests/git/paths.test.ts` | Adds five path, repository, and folder tests. |
| `ts/package.json` | Registers `#git` without adding dependencies. |
| `ts/tests/parity.json` | Marks `conftest.py` as ported and `repos.py` as changed, with the plan's exact explanation. |
| `docs/superpowers/plans/2026-11-02-lodge-server-import/task-2-report.md` | Records changes, failing evidence, validation, and scope decisions. |

The structure table already contains `git`, its allowed imports, and its edge from `main`.
The dependency-cruiser configuration derives its package rules from that table and already confines processes and file access correctly, so neither file needed editing.
`GitDone`, `StoreRead`, and the internal listing entry type remain private.
No application package file or historical report was changed.

## Test-first evidence

All three test modules and their helpers were written before the production Git package or its imports-map entry.
The first `bun test tests/git` run reported `0 pass`, `3 fail`, and `3 errors` because each test module could not resolve `#git`.
In the table, `missing #git` means the first failing output `error: Cannot find package '#git'`, with the importing file identified in the first column.
The two layout tests share one generated declaration, and the revision refusal test retains both parameter cases.

| file:line | Test | First failure or mutation |
|---|---|---|
| `ts/tests/git/run.test.ts:8` | `missing_git_is_one_sentence` | missing `#git` |
| `ts/tests/git/run.test.ts:15` | `failure_names_gits_first_line` | missing `#git` |
| `ts/tests/git/run.test.ts:22` | `resolve_rev_gives_null_for_a_missing_ref` | missing `#git` |
| `ts/tests/git/run.test.ts:28` | `input_reaches_git` | missing `#git` |
| `ts/tests/git/run.test.ts:36` | `isolation_reaches_git` | missing `#git`; also failed against removal of the spawn's `env` option |
| `ts/tests/git/read-store.test.ts:14` | `reads_the_checkout_layout` | missing `#git` |
| `ts/tests/git/read-store.test.ts:14` | `reads_the_branch_layout` | missing `#git` |
| `ts/tests/git/read-store.test.ts:29` | `branch_layout_without_a_settings_revision_has_no_settings` | missing `#git` |
| `ts/tests/git/read-store.test.ts:33` | `revision_that_is_no_commit_is_refused rev` | missing `#git` |
| `ts/tests/git/read-store.test.ts:33` | `revision_that_is_no_commit_is_refused settingsRev` | missing `#git` |
| `ts/tests/git/read-store.test.ts:39` | `revision_without_lodge_is_refused` | missing `#git` |
| `ts/tests/git/read-store.test.ts:45` | `undecodable_record_reads_as_escapes` | missing `#git` |
| `ts/tests/git/read-store.test.ts:50` | `undecodable_attachment_keeps_its_bytes` | missing `#git` |
| `ts/tests/git/read-store.test.ts:60` | `undecodable_name_reads_as_escapes` | missing `#git` |
| `ts/tests/git/read-store.test.ts:74` | `symbolic_link_reads_as_the_path_it_names` | missing `#git` |
| `ts/tests/git/read-store.test.ts:81` | `settings_absent_is_null` | missing `#git` |
| `ts/tests/git/paths.test.ts:10` | `resolve_follows_links` | missing `#git` |
| `ts/tests/git/paths.test.ts:17` | `resolve_takes_dot_dot_through_missing_folders` | missing `#git` |
| `ts/tests/git/paths.test.ts:23` | `repo_root_of_a_file_that_does_not_exist_yet` | missing `#git` |
| `ts/tests/git/paths.test.ts:27` | `repo_root_outside_a_repository_is_one_sentence` | missing `#git` |
| `ts/tests/git/paths.test.ts:33` | `is_folder_says_whether_a_folder_exists` | missing `#git` |

For the isolation mutation, removed only the explicit `env` property from `Bun.spawnSync` in `ts/src/git/run.ts`.
`isolation_reaches_git` failed at `ts/tests/git/run.test.ts:38` with `error: expect(received).toStartWith(expected)` and expected prefix `Test Author <test@example.com>`.
The mutation run ended with `0 pass`, `1 fail`, and `4 filtered out`.
The mutation was reverted before formatting and the successful full gate.
The report omits the inherited identity returned by the mutation, which is not synthetic fixture data.

## Commands and results

Commands below use repository-relative paths.
Inspection also used `cat`, `sed`, `rg`, `nl`, `git diff --stat`, and `git status --short` over the guidance, the required plan sections, the Python reference implementations, the merged interfaces, the structure rules, and the resulting files.
Those reads established that the Task 2 codec and error names have the required meaning and that no new dependency or structure registration is needed.
One exploratory read of `tests/gitstore/test_git.py` found no such file; the adapter's reference implementation is `src/lodge/gitstore/git.py`.
One exploratory search for `ts/src/api/handler.ts` found no such file; the public `handler` is exported from `http.ts` with its expected meaning.

| Command | Result and last meaningful output |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Exit 0; both waiting lists say `nothing`. |
| `git status --short --branch` before changes | Exit 0; `## server-import-git`. |
| `cd ts && bun test tests/git` before implementation | Exit 1; `0 pass`, `3 fail`, `3 errors`, across three files. |
| `cd ts && bun test tests/git` after implementation | Exit 0; `21 pass`, `0 fail`, `43 expect() calls`. |
| `cd ts && bun test tests/git/run.test.ts -t isolation_reaches_git` against the mutation | Exit 1; `0 pass`, `1 fail`, `4 filtered out`. |
| `cd ts && bunx --no-install biome check --write --error-on-warnings src/git tests/git package.json tests/parity.json` | Exit 0; `Checked 12 files`, `Fixed 6 files`. |
| `cd ts && bunx --no-install biome check --write --error-on-warnings tests/git/read-store.test.ts` | Exit 0; `Checked 1 file`, `Fixed 1 file`, after making the checkout case exercise the default settings revision explicitly. |
| `sh scripts/check-ts.sh` | Exit 0; no dependency violations, `1884 pass`, `0 fail`, `6483 expect() calls`, across 172 files. |

The full gate runs Biome with warnings failing, strict TypeScript, dependency-cruiser, knip, and every Bun test, including the structure tests.
Biome emitted 30 informational diagnostics in existing files, with no failing warning or error.
The final verification command is another `sh scripts/check-ts.sh` after this report is written.
The task commit uses explicit paths and the requested Codex trailer, followed by `git push origin server-import-git`.

## Deviations and uncertainties

No implementation deviation or unresolved requirement remains.
The brief authorises committing and pushing from this environment, overriding the plan's sandbox restrictions for those operations.
The coordinator's whole-project gate and other coordinator steps were left to the coordinator.
No package installation was needed, no dependency was added, and no test used a network remote or a real store.
The process-environment mutation establishes why passing an explicit environment remains necessary in this environment.
