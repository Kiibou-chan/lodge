# Task 3 report

Implemented the export writer and the three Task 2 review Minors.

## Files changed

| File | Change |
|---|---|
| `ts/src/git/export.ts` | Adds private target and outcome types, validates paths and target names, reads and fetches tips, refuses checked-out branches and unrelated trees, builds a complete tree through a temporary index and encoded blobs, skips unchanged trees, creates commits with the specified identity, and updates local or remote branches without force. |
| `ts/src/git/index.ts` | Exposes `exportStore` through `#git`, read by `export.test.ts`. |
| `ts/src/git/paths.ts` | Follows symbolic links component by component, including dangling relative targets, before processing parent segments. |
| `ts/tests/git/repos.ts` | Uses core `strip` and adds `bareRemote`, `clone`, `seeded`, `worktree`, and `riggedRemote`, all read by the export tests. |
| `ts/tests/git/export.test.ts` | Adds the planned export cases, extra invalid path cases, byte comparisons, identity checks, a real remote race with retry, a fresh-clone read, and unusual filename coverage. |
| `ts/tests/git/paths.test.ts` | Adds the dangling-link regression. |
| `ts/tests/git/read-store.test.ts` | Gives the invalid primary revision a valid settings revision. |
| `ts/tests/git/repos.test.ts` | Tests Python stripping through stored blobs, including U+0085 and U+FEFF. |
| `docs/superpowers/plans/2026-11-02-lodge-server-import/task-3-report.md` | Records the changes, failing evidence, validation, and deviations. |

The writer stores every supplied path as mode 100644, and removes omitted paths by building a fresh index.
Temporary files and the index are removed in a `finally` block.
All processes use the existing `Bun.spawnSync` adapter, and all test repositories are isolated temporary repositories with local path remotes.
No dependency, historical document, Python source, or structure rule changed.
Every changed module remains below 300 lines.

## Test-first evidence

The export tests and repository helpers were written before `exportStore` or its front-door export.
Their first run failed with `SyntaxError: Export named 'exportStore' not found in module`, ending with `0 pass`, `1 fail`, and `1 error`.
Each export case below was present in that run, including all parameter cases.
The table calls this failure `missing exportStore`.

| file:line | Test | First failure or mutation |
|---|---|---|
| `ts/tests/git/export.test.ts:20` | `first_export_makes_the_branch` | missing exportStore |
| `ts/tests/git/export.test.ts:32` | `same_files_make_no_commit` | missing exportStore |
| `ts/tests/git/export.test.ts:39` | `changed_file_makes_one_commit_on_the_last` | missing exportStore |
| `ts/tests/git/export.test.ts:52` | `removed_file_leaves_the_tree` | missing exportStore |
| `ts/tests/git/export.test.ts:58` | `escaped_bytes_are_written_as_bytes` | missing exportStore |
| `ts/tests/git/export.test.ts:65` | `path_outside_lodge_is_refused` | missing exportStore, for README, parent traversal, `.git`, empty segment, dot segment, backslash, NUL, and bare `lodge` cases |
| `ts/tests/git/export.test.ts:79` | `branch_with_other_files_is_refused` | missing exportStore |
| `ts/tests/git/export.test.ts:86` | `checked_out_branch_is_refused` | missing exportStore |
| `ts/tests/git/export.test.ts:94` | `lodge_zero_two_branch_is_a_target` | missing exportStore |
| `ts/tests/git/export.test.ts:102` | `bad_branch_name_is_refused` | missing exportStore, for `-x`, `a..b`, and `a b` |
| `ts/tests/git/export.test.ts:107` | `bad_remote_is_refused` | missing exportStore, for `-r` |
| `ts/tests/git/export.test.ts:112` | `push_without_force` | missing exportStore; the later fresh-clone assertion was run against replacing the helper's clone operation with `git init -b main`, failing with `fatal: 'origin' does not appear to be a git repository` |
| `ts/tests/git/export.test.ts:121` | `moved_remote_branch_answers_moved` | missing exportStore |
| `ts/tests/git/export.test.ts:128` | `exported_store_reads_back` | missing exportStore |
| `ts/tests/git/read-store.test.ts:33` | `revision_that_is_no_commit_is_refused rev` | Removing only the primary-revision guard produced `fatal: Not a valid object name null` instead of the required `nope is not a commit` sentence |
| `ts/tests/git/paths.test.ts:41` | `resolve_follows_a_dangling_link_before_dot_dot` | Expected the synthetic root's `missing/file.md`, but received its `file.md` |
| `ts/tests/git/repos.test.ts:7` | `git_helper_uses_python_strip` | Expected `record`, but received U+0085 surrounding `record` |

Both mutations were restored before validation.
The settings-revision refusal parameter remained passing during the primary-guard mutation.
Existing tests were retained, with only the brief's specified revision-test adjustment.

## Task 2 review Minors

1. The invalid primary revision now has a valid settings revision, so the settings guard cannot mask removal of the primary guard.
The mutation run ended with `1 pass`, `1 fail`, and `9 filtered out`.
The production reader was restored without a lasting change.
2. `resolvePath` now reads link targets before normalising subsequent parent segments, including `linked -> missing/child`.
The initial regression run failed as specified, while all five existing path tests passed.
After the fix, all six pass.
3. The repository helper now calls `strip` from `#core`.
The blob regression checks that U+0085 is stripped and U+FEFF is retained, matching Python.
The initial combined path and helper run ended with `5 pass` and `2 fail`.

## Commands and results

Inspection used `cat`, `sed`, `nl`, `wc -l`, and Git status and diff commands over the required guidance, plan sections, Task 2 files and report, Python reference implementations, and structure rules.
One exploratory read of `ts/tests/structure/io.ts` reported that the file does not exist; the existing structure table and full structure tests provide the applicable checks.

| Command | Result and last meaningful output |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Exit 0; both waiting lists say `nothing`. |
| `git status --short --branch` before changes | Exit 0; branch `server-import-git`. |
| `cd ts && bun test tests/git/read-store.test.ts -t revision_that_is_no_commit_is_refused` with the primary guard removed | Exit 1; `1 pass`, `1 fail`, `9 filtered out`, and `4 expect() calls`. |
| `cd ts && bun test tests/git/paths.test.ts tests/git/repos.test.ts` before fixes | Exit 1; `5 pass`, `2 fail`, and `11 expect() calls`. |
| `cd ts && bun test tests/git/paths.test.ts tests/git/repos.test.ts tests/git/read-store.test.ts` after fixes | Exit 0; `18 pass`, `0 fail`, and `33 expect() calls`. |
| `cd ts && bun test tests/git/export.test.ts` before implementation | Exit 1; `0 pass`, `1 fail`, and `1 error`, missing `exportStore`. |
| `cd ts && bun test tests/git` after implementation | Exit 0; `46 pass`, `0 fail`, and `91 expect() calls`. |
| `cd ts && bunx --no-install biome check --write --error-on-warnings src/git tests/git` | Exit 0; `Checked 13 files`, `Fixed 6 files`. |
| First `sh scripts/check-ts.sh` | Exit 1; knip reported unused export `clone`, after formatting, TypeScript, and dependency checks passed. |
| `cd ts && bun test tests/git/export.test.ts -t push_without_force` with the clone mutation | Exit 1; `0 pass`, `1 fail`, and `22 filtered out`. |
| `cd ts && bunx --no-install biome check --write --error-on-warnings tests/git/export.test.ts` | Exit 0; `Checked 1 file`, `No fixes applied`. |
| `git diff --check` | Exit 0; no output. |
| `sh scripts/check-ts.sh` after adding the clone reader | Exit 0; `1909 pass`, `0 fail`, and `6531 expect() calls`, across 174 files. |

The full gate runs Biome with warnings failing, strict TypeScript, dependency-cruiser, knip, and every Bun test, including the structure tests.
Biome reports 30 existing informational diagnostics, with no failing warning or error.
The final verification command is `sh scripts/check-ts.sh` again after this report is complete, followed only by explicit-path staging, the requested commit, push, and repository status checks.

## Deviations and uncertainties

The coordinator ruled that the header's subagent workflow belongs to the plan's author session, and that this brief should be implemented directly by one builder.
No workflow skill was installed and no subagent was used.
The brief authorises committing and pushing in this environment, overriding the plan's sandbox restriction on those operations.
The coordinator's whole-project gate and other coordinator steps remain the coordinator's responsibility.
The invalid-remote assertion has its own test name for clarity, retaining the exact planned sentence and case.
Additional invalid paths and unusual filenames strengthen the planned assertions without changing behaviour.
There is no local race test, as the plan explicitly leaves that refusal to Git's compare-and-swap behaviour and probe 4.
No implementation deviation or unresolved uncertainty remains.
No package installation was needed.
