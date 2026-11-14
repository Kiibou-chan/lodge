# Task 4 report

Implemented Task 4 on `server-store-a`.

## Changes by file

| File | Change |
|---|---|
| `ts/src/app/reads.ts` | Checked search, show, waiting, timeline, specification, gate checks, and drafts, with value-based problem grouping and code point ordering. |
| `ts/src/app/threads.ts` | Thread reads and retryable message writes, validation, checked publication, optional commits, and waiting lists. |
| `ts/src/app/lodge.ts` | Async read and thread operations, delegating with trailing defaulted options. |
| `ts/tests/app/reads.test.ts` | First eleven Python read tests, including all eight unreadable-read cases. |
| `ts/tests/app/reads-checks.test.ts` | Remaining Python read tests, including all four unreadable-reference cases. |
| `ts/tests/app/writes.test.ts` | Six remaining Python write tests, preserving the existing thirteen tests. |
| `ts/tests/app/writes-dates.test.ts` | All six Python date tests, using injected `Now` values. |
| `ts/tests/structure/calls.ts` | Apply the object-literal `ok` prohibition to app as well as core. |
| `ts/tests/structure/core-rules.test.ts` | Four failing app literal fixtures and a permitted constructor fixture. |
| `ts/knip.json` | Remove state, writes, and support from entry points now their readers exist. |
| `ts/tests/parity.json` | Mark reads, writes, and writes_dates ported under Task 4, naming both read test files. |
| This report | Changes, first failures, mutation evidence, and validation. |

## Test-first evidence

Before implementation, `cd ts && bun test tests/app` ended with `36 pass`, `45 fail`, and `Ran 81 tests across 8 files`.
The twelve new write and date tests first failed because `draft` was missing.
The existing thirteen write tests were unchanged and continued passing.
The following read tests failed on missing Lodge methods before implementation, except the settings test, whose existing implementation was verified with a targeted mutation below.

| Test | First failing output or mutation |
|---|---|
| `show_of_an_entry_carries_the_deciding_views_with_its_reasoning` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `show_resolves_code_and_levels` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `show_unknown_ref_is_an_error` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `show_ambiguous_code_is_an_error` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `show_flags_a_failing_record` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `search_listed_with_read` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `search_honours_filters` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `unparsable_file_reported_by_every_read` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `waiting_lists_flagged` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `timeline_newest_first_and_limited` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `spec_renders_and_narrows_to_an_area` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `problems_run_the_one_state_checks` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `check_gate_compares_with_the_published_state` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `check_gate_names_the_state_that_fails` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `check_gate_merges_a_problem_both_states_have` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `check_gate_prints_the_gate_notes` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `draft_prints_file_with_base` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `draft_area` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `core_settings_error_becomes_lodge_error` | Replace `parseCoreSettings(table)` with `parseCoreSettings({})`: expected 50, received 100, one test failed, exit 1. |
| `not_found_lists_all_unreadable_files_when_none_matches` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `timeline_refuses_a_negative_limit` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `not_found_does_not_call_a_missing_file_unreadable` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `search_says_how_many_more_matched_beyond_the_limit` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |
| `not_found_names_the_files_lodge_cannot_read` | `TypeError`: the required Lodge method is not a function, before implementing reads and delegates. |

After `draft` existed, each of the twelve carried tests also failed against the following targeted mutation of Task 3 code.
All mutations were reverted.

| Test | Mutation | Result |
|---|---|---|
| `add_stale_base_conflicts_writes_nothing` | stale refusal loses Conflict | exit 1, test failed |
| `feedback_skips_edited_decisions_which_the_check_refuses` | feedback includes edited decisions | exit 1, test failed |
| `staged_second_edit_builds_on_first` | dates staged add against published decisions instead of current decisions | exit 1, test failed |
| `unchanged_draft_publishes_nothing` | unchanged draft publishes | exit 1, test failed |
| `only_changed_files_are_published` | publishes unchanged files | exit 1, test failed |
| `cycle_made_in_one_add_is_refused` | cycle check bypassed | exit 1, test failed |
| `add_in_the_second_of_the_newest_decision_waits_for_the_next` | sleep skipped | exit 1, test failed |
| `add_sleeps_to_the_next_whole_second` | sleep fixed at one second | exit 1, test failed |
| `add_after_the_newest_second_does_not_wait` | whole-second ordering reversed | exit 1, test failed |
| `two_adds_in_one_second_are_dated_a_second_apart` | equal second allowed | exit 1, test failed |
| `a_decision_far_ahead_of_the_clock_is_not_waited_for` | far-future shortcut reversed | exit 1, test failed |
| `a_decision_a_few_seconds_ahead_of_the_clock_is_waited_for` | third wait omitted | exit 1, test failed |

The initial staged-edit mutations of the check predecessor, apply predecessor, and merged after-state did not fail this test.
They were reverted and replaced by the clock predecessor mutation, which failed with expected `staged`, received `check failed`.
No mutation throws at a function entry.

`app_builds_results_through_constructor` failed on `ok`, `'ok'`, `['ok']`, and shorthand `ok` object properties before extending the structure rule: `31 pass`, `4 fail`, `Ran 35 tests across 1 file`.
The `checkResult` fixture passed before and after the rule change.

## Commands and final output

| Command | Last output or outcome |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Nothing waiting for an agent or the author. |
| `cd ts && bun test tests/app`, before implementation | 36 pass, 45 fail, 81 tests. |
| `cd ts && bun test tests/structure/core-rules.test.ts`, before rule change | 31 pass, 4 fail, 35 tests. |
| `cd ts && bun test tests/app`, after implementation | 81 pass, 0 fail, 236 expectations. |
| Individual `bun test` commands with exact test-name patterns and mutations | Each of the twelve listed tests failed, exit 1, with all mutations reverted. |
| Settings test with settings mutation | 0 pass, 1 fail, exit 1, expected 50, received 100. |
| Biome `check --write` on changed files and `format --write tests/parity.json` | Formatting and import ordering applied. |
| First `sh scripts/check-ts.sh` | Failed formatting checks. |
| Second `sh scripts/check-ts.sh` | Type errors identified the missing thread discriminator and a mixed-record map type, both corrected. |
| `sh scripts/check-ts.sh`, before parity changes | 1,018 pass, 0 fail, with no dependency violations and no unused exports. |
| `bun -e` synthetic in-memory thread lifecycle | `thread lifecycle smoke passed`. |
| Final `sh scripts/check-ts.sh`, after parity changes | 1,018 pass, 0 fail, 2,547 expectations, 71 files, exit 0. |

The lifecycle smoke exercised ask, reply, author waiting, record thread views, close, open-thread listing, and thread detail.
No package installation was needed.
No Python source, Python tests, previous brief, previous report, previous review, or main branch was edited.
The untracked session log `task-4-codex.log` is excluded from the commit.

## TypeScript exceptions and uncertainty

No Python test needed a TypeScript-specific exception.
No unresolved implementation concerns remain.
The brief's opening explicitly authorises committing and pushing this worktree, overriding its repeated generic builder restrictions.
The coordinator's whole-repository gate, merge, and ledger step remain with the coordinator.
