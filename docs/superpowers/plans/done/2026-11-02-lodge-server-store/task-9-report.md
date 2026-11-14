# Task 9 report

Implemented the check-on-every-write proof against the SQLite events store.
No production change was needed.

## Files

| File | Change |
| --- | --- |
| `ts/tests/store/seed.ts` | Adds `seeded(...items)`, an in-memory database, `storage-notes` owned by `author`, direct publication of `filesOf(...items)`, and database cleanup after each test. |
| `ts/tests/app/reads-published.test.ts` | Carries all six Python titles with the server behaviours specified in the brief, including check 5, the agent-specific message, unchanged events, and clean reads. |
| `ts/tests/app/writes-retry.test.ts` | Carries all eight Python titles and all three parametrised malformed-name cases through `Interleaving` over SQLite, preserving the Python assertions. |
| `ts/tests/store/checked-writes.test.ts` | Adds the interleaved retirement race, event preservation for refusals and dry runs, current-state gate proof after three adds, and feedback on a refused add. |
| `ts/tests/parity.test.ts` | Applies existence, Python-name retention, and no-TODO checks to changed rows in plan 2, preserving the existing plan 1 existence check. |
| `ts/tests/parity.json` | Assigns both carried changed rows to task `9`, retaining their changed status and explanations. |
| This report | Records changes, red evidence, validation, and interpretation of the brief. |

`ts/knip.json` already omitted `tests/store/interleaving.ts` from `entry`, so it needed no edit.
All temporary mutations were restored, and no production files remain changed.
The pre-existing untracked task log is excluded from the commit.

## Test-first evidence

The read and retry suites were written before `seed.ts`.
Their first run failed with `Cannot find module '../store/seed.ts'`, reporting `0 pass`, `2 fail`, and `2 errors`.
After the helper existed, all 16 cases passed against the earlier tasks' code.
The four checked-write tests were then written and run before any possible production fix.
Two passed immediately, and two exposed fixture assumptions: retirement writes two file events, and feedback concerns newly written decisions, rather than edits of existing decisions.
The event assertion was corrected to count A's two events, and the feedback fixture now creates a new decision with a long title and an entry resting on a missing entry.
All four passed without changing production code.

Each passing test was then seen failing against the targeted mutations below.
Mutations affected real checks, publication, retry, error classification, read flags, or gate results, never an unconditional exception at function entry.

| Test or named group | Mutation and observed failure |
| --- | --- |
| `show_flags_a_hand_edited_published_decision` | Skip `if (!check.ok)` in `writes.ts`: throws the store's published-decision rewrite `LodgeError` instead of returning `CHECK_FAILED`. |
| `search_and_timeline_flag_it_too` | Same skipped-check mutation: published-decision rewrite `LodgeError`. |
| `plain_check_lists_the_problem_and_fails` | Same skipped-check mutation: published-decision rewrite `LodgeError`. |
| `gate_still_reports_it_once` | Same skipped-check mutation: published-decision rewrite `LodgeError`. |
| `an_unedited_published_state_reads_clean` | Replace `readChecked`'s failing IDs with all decision IDs: clean decision unexpectedly has `fails check`. |
| `a_shrunk_agent_reasoning_fails_on_a_read` | Skip the write check: published-decision rewrite `LodgeError`. |
| `add_retry_keeps_concurrent_entry` | Reduce `ATTEMPTS` from three to one: throws `Conflict` instead of publishing. Also fails with the compare-and-set removed. |
| `add_retry_concurrent_edit_of_same_entry_conflicts` | One attempt: conflict message lacks `it changed since the draft was made`. Also fails with the compare-and-set removed. |
| `add_gives_up_after_three` | One attempt: attempts are one instead of three. Also fails with the compare-and-set removed. |
| `ref_moving_between_reads_retries` | One attempt: throws `Conflict` instead of publishing. Also fails with the compare-and-set removed. |
| `area_created_by_another_add_is_a_conflict` | Remove the revision predicate from `touchHead`: publication succeeds instead of raising `Conflict`. |
| `entry_created_by_another_add_is_a_conflict` | Same removed compare-and-set: publication succeeds instead of raising `Conflict`. |
| `refusal_on_the_first_attempt_is_a_usage_error` | Classify usage refusals as `Conflict`: violates the non-conflict assertion. |
| `unhashable_names_are_usage_errors`, all three cases | Same error-classification mutation: each malformed-name case violates the non-conflict assertion. |
| `every_write_is_checked_against_the_state_it_lands_on` | Skip the write check: publishes instead of returning `CHECK_FAILED`. Removing the compare-and-set also makes this fail. |
| `a_refused_write_leaves_no_event` | Skip the write check: the edited-decision add throws instead of returning `CHECK_FAILED`. |
| `gate_on_the_server_is_the_current_state` | Return an empty published file map from the store gate: gate result differs from current-state problems. |
| `a_refused_add_carries_its_feedback` | Clear feedback in the `CHECK_FAILED` result: expected length feedback is absent. Skipping the check also fails this test. |
| `ported_files_exist` | Temporarily remove the changed plan 2 read suite: expected `true`, received `false`. |
| `ported_files_keep_every_python_test_name` | Temporarily replace the clean-read test with `test.todo("removed_name", ...)`: missing Python title. |
| `ported_files_hold_no_todo` | Same changed-row mutation: unexpected TODO title. |

The skipped-check run reported eight failures, one-attempt four, removed compare-and-set seven, error-classification four, read-flags four, altered gate one, and cleared feedback one.
The parity mutations reported one missing-file failure and two name/TODO failures.
Every mutation was reverted before validation.

## Commands and results

Read-only inspection used `cat`, `rg`, `sed`, `head`, `tail`, `wc`, and Git status, branch, and diff commands.
Some initial `cat` and `rg` probes named absent candidate modules and returned file-not-found diagnostics; the actual modules were then located by `rg --files`.
Temporary Python scripts wrote the new test files and orchestrated reversible mutations.
No dependency installation or Python source change was made.

| Command | Result or last lines |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | `waiting for an agent: nothing`; `waiting for the author: nothing`. |
| `cd ts && bun test tests/app/reads-published.test.ts tests/app/writes-retry.test.ts`, before seed | `0 pass`, `2 fail`, `2 errors`; missing `seed.ts`. |
| Same command, after seed | `16 pass`, `0 fail`, `61 expect() calls`. |
| `cd ts && bun test tests/store/checked-writes.test.ts`, first fixture run | `2 pass`, `2 fail`, `17 expect() calls`. |
| Same command, corrected fixtures | `4 pass`, `0 fail`, `18 expect() calls`. |
| Mutation runs using `bun test` on the selected suites | All exited 1, with the failures listed above. |
| `cd ts && bun test tests/app tests/store` | `220 pass`, `2 todo`, `0 fail`, `651 expect() calls`; 222 tests across 26 files. |
| `cd ts && bunx biome check --write` on the changed TypeScript files and parity JSON | Formatting fixed; no remaining diagnostics. |
| `git diff --check` | Exit 0, no output. |
| First `sh scripts/check-ts.sh` | Type errors: missing required `tree.rev`, and `{}` instead of `filters()`; corrected in the new tests. |
| Next `sh scripts/check-ts.sh` | Parity JSON needed Biome formatting; corrected. |
| Final `sh scripts/check-ts.sh` | Exit 0; Biome, TypeScript, dependency-cruiser, knip, and tests pass; `1218 pass`, `2 todo`, `0 fail`, `3067 expect() calls`, 1220 tests across 93 files. |

## Behaviour differences and concerns

No Python assertion is impossible because of TypeScript itself.
The six read-test titles remain, with the server-specific assertions required by the brief.
For the five edited-state scenarios, Python's direct hand edit and subsequent invalid reads cannot occur on this server: `add` refuses the edit and leaves the valid published state intact.
The unedited-state scenario keeps its original clean-read assertions.
The retry tests retain Python's behaviour, including malformed YAML list and mapping names as usage errors.

The brief refers to three changed files, but the parity table contains exactly two changed rows in plan 2, for the read and retry suites.
The new checked-write suite has no Python counterpart and no parity row was invented for it.
The general changed-row parity checks cover any later plan 2 changed rows automatically.
The two existing TODOs belong to the command tests deferred to plan 3, outside this task.

The brief's opening explicitly requests a commit and push, overriding its repeated generic builder restriction.
The coordinator's whole-project gate, merge, and ledger update remain outside this task.
