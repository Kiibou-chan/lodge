Task 9b implemented on the current branch.
No staging, commits, pushes, package installation, or network calls were performed.

Files changed:

- `ts/src/core/render.ts`: ported the readonly `Placed` and `SpecArea` interfaces, `specView`, dependency placements, cross-area links, heading escaping, and byte-for-byte Markdown rendering.
- `ts/src/core/search.ts`: ported `Filters`, its default-filling `filters` function, `AmbiguousRef` extending `LookupError`, reference resolution, filtered and counted search, weighted ranking, newest-first ties, and related decisions.
  The undated sentinel is the integer instant for `0001-01-01T00:00:00+00:00`, and numeric related-search terms use `isDigit`.
- `ts/src/core/words.ts`: ported Unicode letter-or-number tokenisation and every Python function word unchanged.
- `ts/src/core/index.ts`: added only Task 9b's public exports.
- `ts/tests/core/render.test.ts`: carried all 13 Python rendering tests, with their names and assertions.
- `ts/tests/core/search.test.ts`: carried all 17 Python search tests, with their names and assertions, including both the ambiguity exception class and its message pattern.
- `ts/tests/core/render-text.test.ts`: added the required newline-only heading test, covering U+2028, U+2029, lone CR, CRLF underline text, LF headings, and a final newline.
- `ts/tests/parity.json`: changed only the render and search rows from `planned` to `ported`.
- `docs/superpowers/plans/2026-11-02-lodge-server-core/task-9b-report.md`: this report.

All source and test files remain below 300 lines, so no split or knip entry change was necessary.
No existing implementation or test file was changed beyond the authorised front door and parity rows.
The supplied brief was already untracked when work began and was left untouched.

Test-first evidence:

All 31 tests were written before the three implementation modules or their front-door exports existed.
The first `cd ts && bun test tests/core` exited 1 with `547 pass`, `1 todo`, `3 fail`, and `3 errors`, ending `Ran 551 tests across 40 files. [995.00ms]`.
The failures were module-loading errors, which the brief explicitly accepts as first failures.
No earlier-task mutation was necessary because these tests exercise the newly ported modules.
Each test below maps to its file's first failure.

`ts/tests/core/render.test.ts` first failed with `SyntaxError: Export named 'specView' not found in module` at the core front door:

- `render_spec_skips_retired_follows_order`
- `render_spec_entry_without_area_file_and_empty_store`
- `render_spec_marks_flagged_failing_and_imported_entries`
- `spec_view_gives_areas_with_level_one_entries_in_order`
- `render_spec_escapes_lines_that_start_with_a_hash`
- `render_spec_escapes_indented_hashes_and_underline_headings`
- `render_spec_follows_rank_then_derived_order`
- `render_spec_lists_cross_area_targets`
- `spec_view_places_with_depth_under_and_also`
- `cross_area_target_is_across_not_also`
- `retired_same_area_target_is_not_also`
- `retired_cross_area_target_remains_across`
- `duplicate_targets_are_shown_once`

`ts/tests/core/search.test.ts` first failed with `SyntaxError: Export named 'AmbiguousRef' not found in module` at the core front door:

- `resolve_case_insensitive`
- `resolve_ambiguous_code_raises`
- `search_title_over_statement`
- `search_exact_id_or_code_first_then_ties_newest_first`
- `search_words_split_on_non_letters_and_limit`
- `search_empty_query_lists_what_the_filters_allow`
- `search_each_filter`
- `search_hides_replaced_unless_asked`
- `related_shared_entry_first`
- `search_without_words_returns_exact_match_only`
- `search_ties_larger_id_first`
- `search_ignores_function_words`
- `related_ignores_function_words_and_numbers`
- `search_area_matches_decisions_changing_its_entries`
- `related_needs_two_shared_words_not_one`
- `related_ignores_a_word_most_decisions_carry`
- `search_reports_how_many_matched_beyond_the_limit`

`ts/tests/core/render-text.test.ts` first failed with `SyntaxError: Export named 'renderSpec' not found in module` at the core front door:

- `heading_line_breaks_at_newline_only`

Commands and outcomes:

- Read the requested brief, `CLAUDE.md`, the cloud runtime skill, the three Python modules, both Python test files, the TypeScript builders, order, stamps, views, errors, text exports, front door, package metadata, knip configuration, parity helpers, and check script with `cat`, `rg`, and `sed`.
  These were local inspections only.
  The `AGENTS.md` search returned no paths.
  Two speculative inspection paths, `ts/tests/core/api.test.ts` and `ts/tests/core/front-door.test.ts`, did not exist, ending with `No such file or directory`; no task input was missing.
- `uv run --frozen --quiet lodge waiting`: exited 0, ending `waiting for the author` and `nothing`; there was also nothing waiting for an agent.
- `python /tmp/port9b.py`: generated the initial carried tests from the Python AST and exited 0 without output.
  Subsequent local Python edits corrected JavaScript reserved names, keyword arguments, camelCase, readonly indexing, and fixture construction before implementation.
- Initial `cd ts && bun test tests/core`: exited 1 with the missing-export failures described above.
- Local heredoc writes and Python generation created the three implementation modules and exports without adding dependencies.
- `cd ts && bun test tests/core` after implementation: exited 0, ending `578 pass`, `1 todo`, `0 fail`, `1523 expect() calls`, and `Ran 579 tests across 40 files. [1012.00ms]`.
- First `cd ts && bun --bun run biome check --write` over the seven task TypeScript files: exited 1, ending `error: "biome" exited with code 1`.
  It found `lint/correctness/noUnsafeOptionalChaining` in the generated common-word fixture, which was rewritten as a direct map without disabling any rule.
- The same targeted `biome check --write`, followed by `bun --bun run tsc --noEmit -p .`: exited 0, ending `Checked 7 files in 15ms. Fixed 1 file.`; TypeScript emitted no diagnostics.
- `sh scripts/check-ts.sh` before parity updates: exited 0.
  Biome checked 95 files, dependency-cruiser reported no violations across 103 modules and 332 dependencies, knip passed, and Bun ended with `755 pass`, `1 todo`, `0 fail`, `2029 expect() calls`, and `Ran 756 tests across 47 files. [2.91s]`.
- A local Python edit changed only the two required parity statuses.
- `uv run --frozen --quiet python` with an inline assertion against Python render's `_escaped`: exited 0, ending `Python heading-escape oracle matches the new TypeScript fixture`.
- `git diff --check`: exited 0 without output, both before and after parity updates.
- `wc -l` over the six new source/test files: reported 81, 133, 87, 212, 264, and 15 lines respectively, ending `792 total`.
- Final `sh scripts/check-ts.sh`: exited 0 after both parity rows were marked `ported`.
  Biome checked 95 files without fixes, TypeScript passed, dependency-cruiser reported no violations across 103 modules and 332 dependencies, and knip passed with the same existing hints.
  Bun ended with `755 pass`, `1 todo`, `0 fail`, `2033 expect() calls`, and `Ran 756 tests across 47 files. [1.91s]`.
  The additional four assertions come from parity checking every carried render and search test name.
  This was the final validation command; only its result was recorded in this report afterwards.

TypeScript exceptions and concerns:

Every carried Python test holds in TypeScript; there are no omitted, weakened, or incompatible tests to refer for a ruling.
The existing suite has one todo, and knip prints two non-failing configuration hints for unmatched existing `scripts/*.ts` and `scripts/**/*.ts` patterns.
Neither required a change within this task's lane.
The cloud runtime skill's environment-status tool is unavailable in this session; the task remained entirely local as required.
No unresolved implementation uncertainty remains.
The coordinator still owns the whole-repository gate, staging, commit, and push.
