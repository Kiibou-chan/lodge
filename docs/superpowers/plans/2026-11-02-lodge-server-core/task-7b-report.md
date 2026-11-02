# Task 7b report

Status: DONE.

## Changes

- `ts/src/core/confirmation.ts`: ports confirmation selection, creator and latest changer ordering, constants, and YAML drafts preserving author text.
- `ts/src/core/confirmation.ts`: keeps the Python empty area-list failure through a private `IndexError` extending `LookupError`.
- `ts/src/core/order.ts`: ports readonly `Placement` and `Branch` interfaces, ranked area names, written ordering, depth-first placement, cycle fallback, and dependency trees.
- `ts/src/core/index.ts`: exports exactly this task’s public interfaces.
- `ts/tests/core/confirmation.test.ts`: carries all eight Python test names, including both parameter cases, and adds the empty area-list regression.
- `ts/tests/core/order.test.ts`: carries all thirteen Python tests.
- `ts/tests/parity.json`: marks only confirmation and order as `ported`.
- `ts/knip.json`: removes only `src/core/derive.ts` from entry exemptions.

## Failing-first evidence

All carried tests were written before the implementation and run with `cd ts && bun test tests/core`.
Both test modules failed to load because their public exports were absent.
The first output for every confirmation test below was `SyntaxError: Export named 'confirmationDraft' not found in module .../ts/src/core/index.ts`.
The first output for every order test below was `SyntaxError: Export named 'writtenOrder' not found in module .../ts/src/core/index.ts`.
The module failure counts as the missing-export failure required by the brief.

Confirmation tests:

- `confirmable_ids_skip_author_confirmed_and_replaced`.
- `behind_area_lists_creators_and_last_changers_oldest_first`.
- `behind_area_includes_the_retirer_of_a_retired_entry`.
- `confirmation_draft_single`.
- `confirmation_draft_area_lists_with_the_oxford_comma`.
- `behind_area_same_date_uses_id_tie_break`.
- `confirmation_draft_two_uses_and`.
- `confirmation_draft_without_area_requires_one_id %p`, with the complete cases `[]` and `["d-aaaaaa", "d-bbbbbb"]`.

Order tests:

- `ranked_areas_first_then_by_name`.
- `shared_rank_ordered_by_name`.
- `folder_without_area_file_sorts_with_unranked`.
- `entry_after_what_it_rests_on`.
- `no_links_keeps_written_order`.
- `under_is_the_target_placed_last`.
- `dependant_follows_what_it_rests_on`.
- `cycle_falls_back_to_written_order`.
- `retired_target_does_not_hold_an_entry_back`.
- `dependants_follow_depth_first`.
- `diamond_uses_last_placed_target_at_depth_two`.
- `rests_on_tree_reaches_the_roots`.
- `rests_on_tree_stops_on_a_cycle`.

The additional `confirmation_draft_empty_area_list_keeps_python_index_error` was run before adding its guard.
Its first failing output was `Expected: "IndexError"; Received: "Error"`, because the call returned and the test’s sentinel error was caught.
That run ended `9 pass, 1 fail, 23 expect() calls; Ran 10 tests across 1 file`.
No mutations of earlier task code were needed.

## Commands and results

- Read the brief, `CLAUDE.md`, runtime skill, Python source and tests, existing TypeScript helpers, core modules, package manifest, and parity configuration using `cat`, `head`, and `rg`.
- `uv run --frozen --quiet lodge waiting`: last section was `waiting for the author / nothing`; nothing waited for an agent either.
- `rg --files -g AGENTS.md -g "*SKILL*"`: no matching repository files, exit 1.
- Temporary Python scripts wrote the test translations and made scoped file edits, exit 0.
- `cd ts && bun test tests/core`, before implementation, twice: `350 pass, 4 todo, 2 fail, 2 errors; 1142 expect() calls; Ran 356 tests across 25 files`.
- `bunx --no-install biome check --write` on task files: initial output included non-null assertion warnings; these were removed from the code without disabling rules.
- `cd ts && bunx --no-install tsc --noEmit -p .`: exit 0, no output.
- Targeted carried tests after implementation: `22 pass, 0 fail, 45 expect() calls; Ran 22 tests across 2 files`.
- `sh scripts/check-ts.sh` before parity flip: exit 0; `549 pass, 4 todo, 0 fail; 1659 expect() calls; Ran 553 tests across 32 files`.
- Targeted tests including the added regression: `23 pass, 0 fail, 48 expect() calls; Ran 23 tests across 2 files`.
- Final scoped Biome run: `Checked 2 files in 7ms. No fixes applied.`
- `git diff --stat`, `git diff --` shared task files, `git status --short`, and test-title searches reviewed scope; no staging, commits, or pushes.
- `sh scripts/check-ts.sh` after parity flip and again after writing this report: exit 0; `550 pass, 4 todo, 0 fail; 1666 expect() calls; Ran 554 tests across 32 files`.

## Limits and concerns

No carried test is impossible in TypeScript, and no assertion was weakened.
Python dataclass checks become discriminant checks, tuples become readonly arrays, sets become readonly sets, and lookups use maps.
No additional packages, network access, or changes to earlier task implementations were needed.
No module or test needed splitting.
Knip reports no unused exports, with two existing configuration hints for script globs without matches.
Four pre-existing TODO cases remain.
No unresolved implementation concerns.
The coordinator still runs `sh scripts/check.sh` outside the sandbox.
