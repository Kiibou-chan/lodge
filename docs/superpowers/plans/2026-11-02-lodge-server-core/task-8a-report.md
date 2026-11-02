Task 8a report: DONE.

Changed files:

- `ts/src/core/check-state.ts`: ported CheckResult, checks 1, 2, and 3, deterministic problem ordering, and the helpers newDecisions, problemAt, and sortKey for Task 8b.
- `ts/src/core/check-areas.ts`: ported check 7, including current status, duplicate order items, missing area files, and path attribution.
- `ts/src/core/check-cycles.ts`: ported check 8, including transitive reachability, mutual cycle membership, and exclusion of self-only cycles.
- `ts/src/core/index.ts`: exported CheckResult and checkState through the front door.
- `ts/tests/core/checks.ts`: ported all shared fixture helpers and constants except check and verdict, which await check_change in Task 8b.
  NOW is the exact stamp required by the brief.
  key and baseItems remain private.
- `ts/tests/core/check-state.test.ts`: carried all 27 Python test names and all parameter cases, giving 39 carried cases, and added two focused regression tests.
  The file is 281 lines, so no split was needed.
- `ts/tests/parity.json`: marked only test_check_state.py as ported.
  checks.py remains planned because check and verdict are deliberately deferred.
- `ts/knip.json`: added only src/core/check-state.ts and tests/core/checks.ts to entry for future readers.
- This report records the changes and validation.

The reviewer files were not edited.
No dependencies were added, no network access was used, and nothing was staged, committed, or pushed.

Test-first evidence:

The following carried tests were written before the implementation and their first run, `cd ts && bun test tests/core`, failed at module import with `SyntaxError: Export named 'checkState' not found in module '<workspace>/ts/src/core/index.ts'.`.
The missing export prevented collection of every case below, as permitted by the brief.

- `clean_state_passes`.
- `check_1_parse_problem_is_reported`.
- `check_1_file_name_without_the_id`.
- `check_1_file_name_of_the_bare_id_passes`.
- `check_1_file_name_that_only_begins_like_the_id`.
- `check_2_unresolved_link`.
- `check_2_links_that_resolve_pass`.
- `check_2_one_problem_per_unresolved_link`.
- `check_2_duplicate_id_from_load_is_reported`.
- `check_2_codes_compared_without_case`.
- `check_2_distinct_codes_pass`.
- `check_2_listed_attachment_missing`.
- `check_2_listed_attachment_resolves_below_the_decision_folder`.
- `check_2_listed_attachment_elsewhere_does_not_count`.
- `check_2_decision_linking_to_itself`.
- `check_3_author_decision_without_quote`.
- `check_3_empty_where_or_when`.
- `check_3_imported_author_decision_needs_no_quote`.
- `check_3_author_lookalike`.
- `check_3_confirms_on_a_non_author_decision`.
- `check_7_entry_missing_from_the_order`.
- `check_7_order_lists_an_entry_that_is_not_there`.
- `check_7_order_lists_an_entry_of_another_area`.
- `check_7_order_lists_a_retired_entry`.
- `check_7_order_lists_an_entry_twice`.
- `check_7_folder_with_entries_has_no_area_file`.
- `check_7_empty_area_needs_no_entries`.

The first run ended with `350 pass`, `4 todo`, `1 fail`, `1 error`, and `Ran 355 tests across 24 files.`.
The first implemented run ended with `39 pass`, `0 fail`, `47 expect() calls`, and `Ran 39 tests across 1 file.`.

Additional mutation evidence:

- `check_1_parse_problem_is_reported` and `check_2_duplicate_id_from_load_is_reported` also failed with expected problems versus received `[]` when the snapshot problem spread was removed from checkState.
  This verifies that the carried duplicate-ID case observes the existing loader's output rather than merely exercising load.
- `check_8_cycles_include_each_member_and_ignore_self_and_missing_links` was added and failed against omission of checkCycles from the result aggregation, with the two expected cycle problems versus received `[]`.
  It also checks that self-links and missing targets produce check 2 problems without a check 8 problem.
- `check_2_codes_use_unicode_casefold` was added and failed against replacing casefold(r.code) with r.code.toLowerCase(), with both expected duplicate-code problems versus received `[]`.

The mutation run ended with `37 pass`, `4 fail`, `49 expect() calls`, and `Ran 41 tests across 1 file.`.
All mutations were confined to check-state.ts and reverted before subsequent validation.
The supplemental tests were verified against mutations of the implementation; their first failing runs were not against a missing module.

Commands and outcomes:

- Read the brief, CLAUDE.md, the cloud runtime skill, the three named Python modules, both Python fixture/test files, and the existing TypeScript builders, model, snapshot, front door, settings, text, derive, knip, and parity files using cat and rg.
  The runtime status tool was not available in the tool catalogue.
- `uv run --frozen --quiet lodge waiting`: final output `waiting for the author` / `nothing`; nothing waited for an agent either.
- `rg --files -g AGENTS.md -g SKILL.md`: no matches, exit 1.
- Used shell heredocs and small Python scripts to write only task files, and cp to save and restore the temporary mutation.
- `cd ts && bun test tests/core`: initial red result recorded above.
- `cd ts && bunx --no-install biome check --write src/core/check-*.ts tests/core/check*.ts src/core/index.ts knip.json`: `Checked 7 files ... Fixed 6 files.`.
- `cd ts && bun test tests/core/check-state.test.ts`: first green result recorded above.
- `sh scripts/check-ts.sh` before the parity flip: exit 0, `566 pass`, `4 todo`, `0 fail`, `1661 expect() calls`, and `Ran 570 tests across 31 files.`.
- `cd ts && bun test tests/core/check-state.test.ts` with the three mutations: four failures recorded above.
- `cd ts && bunx --no-install biome check --write tests/core/check-state.test.ts tests/parity.json`: formatting completed successfully.
- `wc -l ts/tests/core/check-state.test.ts`: `281`.
- `cd ts && bun test tests/core/check-state.test.ts` after restoration: `41 pass`, `0 fail`, `50 expect() calls`, and `Ran 41 tests across 1 file.`.
- `git status --short`, `git diff --stat`, and rg inspections confirmed the task's changed paths and the four mutation failures.
- `sh scripts/check-ts.sh` after the parity flip: exit 0, Biome clean, TypeScript clean, no dependency violations, knip successful, `568 pass`, `4 todo`, `0 fail`, `1666 expect() calls`, and `Ran 572 tests across 31 files.`.
  The gate is run again as the final command after writing this report.

No carried test cannot hold in TypeScript.
There are no behaviour exceptions requiring a ruling.
The four existing todo cases remain unchanged.
Knip prints its existing configuration hints for unmatched scripts/*.ts and scripts/**/*.ts patterns but exits successfully.
No implementation concerns remain.
Task 7b is not required for this lane, as the coordinator explains in the brief.
The coordinator still owns the full Python and TypeScript gate outside the sandbox, staging, committing, and pushing.
