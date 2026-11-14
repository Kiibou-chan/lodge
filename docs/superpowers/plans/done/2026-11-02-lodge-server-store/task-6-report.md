# Task 6 report

Implemented confirmations and verified the application front door.

## Files

- `ts/src/app/confirm.ts`: reads the confirmation list once, rejects stale lists and invalid words, chooses the scope, writes a new confirmation through `add`, commits only staged writes when requested, and lists affected entries across areas without duplicates.
Callers must serialise the whole confirmation operation.
- `ts/src/app/lodge.ts`: adds asynchronous `confirm` and `behindArea` methods with the required trailing options and defaults.
- `ts/tests/app/confirm.test.ts`: ports all 19 Python test functions, including both cases of each parametrised test, for 21 cases.
- `ts/tests/app/front-door.test.ts`: uses the TypeScript parser and checker to compare exports with Python `__all__`, allowing only the specified additions.
- `ts/tests/parity.json`: marks the confirmation row ported by task 6.
All application rows are now ported or changed except the thread path command tests deferred to plan 3.
- `ts/src/app/index.ts`: inspected and left unchanged because its existing exports already include every required Python name and the current additions.
- This report records the work and verification.

## Test-first evidence

Every confirmation case failed before implementation in `cd ts && bun test tests/app`.
The first run ended with `120 pass`, `2 todo`, `21 fail`, and `Ran 143 tests across 14 files`.
The front-door tests passed over existing code, so each was then run against a targeted mutation, and both mutations were reverted before implementation.

| Test title (without parameter display suffixes) | First failure or mutation detected |
|---|---|
| `confirm_one_decision` | `TypeError: confirm is not a function` |
| `confirm_writes_only_a_new_decision_file` | `TypeError: confirm is not a function` |
| `confirmed_decision_keeps_decided_by_and_clears_its_flag` | `TypeError: confirm is not a function` |
| `scope_product_when_any_listed_is_product` | `TypeError: confirm is not a function` |
| `scope_process_when_all_are_process` | `TypeError: confirm is not a function` |
| `area_confirms_exactly_the_listed` | `TypeError: confirm is not a function` |
| `stale_area_list_writes_nothing` | `TypeError: confirm is not a function` |
| `second_identical_confirmation_is_stale` | `TypeError: confirm is not a function` |
| `words_required` | `TypeError: confirm is not a function` |
| `words_with_specials_kept_verbatim` | `TypeError: confirm is not a function` |
| `words_with_unstorable_character_refused` | `TypeError: confirm is not a function` |
| `commit_after_staged` | `TypeError: confirm is not a function` |
| `behind_area_lists_entries_in_other_areas` | `TypeError: lodge.behindArea is not a function` |
| `show_marks_confirmable` | `TypeError: confirm is not a function` |
| `confirmation_does_not_commit_unless_staged_and_requested` | `TypeError: confirm is not a function` |
| `confirmation_failed_check_writes_and_commits_nothing` | `TypeError: confirm is not a function` |
| `repeated_cr_before_lf_is_refused` | `TypeError: confirm is not a function` |
| `second_area_confirmation_is_stale` | `TypeError: confirm is not a function` |
| `duplicate_confirmation_ids_are_stale` | `TypeError: confirm is not a function` |
| `front_door_exports_every_python_name` | Removed the `Lodge` re-export from `index.ts`; missing `Lodge` failed the assertion, with `1 pass`, `1 fail`. |
| `front_door_exports_nothing_else` | Added `unexpectedTaskSixExport` to `index.ts`; the extra export failed the assertion, with `1 pass`, `1 fail`. |

No Python confirmation test is impossible in TypeScript, and none was weakened or deferred.
The two existing TODOs remain the plan 3 thread path command tests.

## Commands and results

- `cat docs/superpowers/plans/2026-11-02-lodge-server-store/task-6-brief.md`, then `cat CLAUDE.md`: read the requirements and repository instructions.
- `uv run --frozen --quiet lodge waiting`: both agent and author queues ended with `nothing`.
- Repository inspection used `rg`, `cat`, `head`, `wc`, `git status --short`, `git branch --show-current`, and `git diff`.
The branch was `server-store-a`.
- `cd ts && bun test tests/app`: first run ended with 21 failures; after implementation it ended with `141 pass`, `2 todo`, `0 fail`, and `Ran 143 tests across 14 files`.
- `cd ts && bun test tests/app/front-door.test.ts`: each of the two mutation runs ended with `1 pass`, `1 fail`, and `Ran 2 tests across 1 file`.
- `cd ts && bunx biome check --write src/app/confirm.ts src/app/lodge.ts tests/app/confirm.test.ts tests/app/front-door.test.ts`: `Checked 4 files`, `Fixed 4 files`.
- `sh scripts/check-ts.sh`: the first run found missing `rev` fields and a possibly undefined test path in TypeScript; explicit test types fixed them.
The second run found `app may not use confirm` because the structure guard reserves the browser global name even on a function declaration.
Renamed the internal helper to `confirmDecisions`, keeping the public `Lodge.confirm` unchanged.
- Final `sh scripts/check-ts.sh`: exit 0; Biome, TypeScript, dependency-cruiser, knip, and Bun tests passed.
Last test lines: `1176 pass`, `2 todo`, `0 fail`, `2906 expect() calls`, and `Ran 1178 tests across 86 files`.
- Staging and commit use only the six task paths, with the required identity and Codex trailer, followed by `git push origin server-store-a`.

## Concerns

No unresolved implementation concerns.
The brief's direct instruction to commit and push on `server-store-a` takes precedence over its repeated generic builder prohibition.
The coordinator's whole Python gate, merge, and ledger update are outside this task.
No packages were installed, and no Python implementation, historical brief, report, or review was edited.
The pre-existing untracked task execution log is excluded from the commit.
