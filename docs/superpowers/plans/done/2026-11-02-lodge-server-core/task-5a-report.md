Task 5a is implemented, with concerns listed below.
No commit, staging, push, installation, network call, Python source change, or reviewer-file edit was performed.

Changes per file:

- `ts/src/core/fields.ts`: typed Map readers, ordered unknown-key errors, internal `FormatError`, and date and stamp validation through `stamps.ts`.
- `ts/src/core/document.ts`: CRLF normalisation, lone-surrogate rejection, document fences, YAML header loading, Python whitespace trimming, reasoning sections, and problem line attribution.
- `ts/src/core/headers.ts`: decision, specification entry, and area construction, including all optional fields and allowed-key lists.
- `ts/src/core/fileformat.ts`: record and area parsing and canonical writing, read-back checks, paths, slugs, and SHA-256 hashes using the declared `@noble/hashes` dependency.
- `ts/src/core/index.ts`: exports the eight requested public functions.
- `ts/tests/core/samples.ts`: carries the synthetic shared fixtures and helpers.
- `ts/tests/core/fileformat.test.ts`: carries round trips, canonical output, character handling, hashing, areas, and paths.
- `ts/tests/core/fileformat-write.test.ts`: carries the three write rejection tests, split out because formatting the original test file made it 399 lines.
- `ts/tests/core/fileformat-problems.test.ts`: carries every format-problem test and parameter case.
- `ts/tests/parity.json`: marks the three requested Python files ported and associates the extra write-test file with `test_fileformat.py`.
- `ts/knip.json`: removes `@noble/hashes` from ignored dependencies, removes `yamlio.ts` from entries, and adds `headers.ts`, `document.ts`, and `fields.ts` for their future readers.

The implementation modules are 158, 86, 148, and 197 lines respectively after formatting.
The test files are 296, 104, and 202 lines, and samples is 59 lines.
The final structure gate checks their actual sizes.

Test-first evidence:

The tests carried from `test_fileformat.py` into `fileformat.test.ts and fileformat-write.test.ts` all first failed at module import with `SyntaxError: Export named 'newRecordPath' not found in module`, before any implementation was written.
All parameter cases were carried.


- `decision_round_trips_both_ways`.

- `written_text_matches_example`.

- `written_text_of_every_field`.

- `round_trip_survives_hostile_strings`.

- `round_trip_survives_every_readable_character`.

- `bad_code_is_problem_1`.

- `control_character_is_problem_1`.

- `write_refuses_control_characters`.

- `write_refuses_reasoning_heading_in_statement`.

- `write_refuses_a_record_parse_would_not_read_back`.

- `statement_with_a_lookalike_heading_is_kept`.

- `crlf_text_parses_and_hashes_as_lf`.

- `hash_covers_undecodable_bytes`.

- `spec_entry_takes_area_from_folder`.

- `spec_entry_with_code_and_import_round_trips`.

- `area_file_round_trips`.

- `area_without_entries_or_intro`.

- `paths_and_slugs`.

The tests carried from `test_fileformat_problems.py` into `fileformat-problems.test.ts` all first failed at module import with `SyntaxError: Export named 'parseRecord' not found in module`, before any implementation was written.
All parameter cases were carried.


- `missing_fence`.

- `bad_yaml_with_line`.

- `header_that_is_not_a_mapping`.

- `unknown_key_named`.

- `unknown_kind`.

- `missing_required_field`.

- `empty_statement_is_missing`.

- `empty_title_is_missing`.

- `bad_scope_or_action`.

- `non_string_where_string_expected`.

- `wrong_shapes_name_their_key`.

- `bad_id_shapes`.

- `change_entry_must_be_a_specification_id`.

- `date_without_offset`.

- `date_that_is_not_a_date`.

- `date_only_without_import`.

- `imported_date_only_normalised`.

- `duplicate_key`.

- `spec_entry_outside_an_area_folder`.

- `spec_entry_rejects_decision_keys_and_reasoning`.

- `bad_utf8_is_problem_1`.

- `area_problems`.

The first core run ended `83 pass`, `2 fail`, `2 errors`, and `Ran 85 tests across 7 files`.
The two import errors prevented every new test from loading, including each parameter case.
No earlier-task implementation mutation was needed, because these tests depend on new fileformat exports.
The first successful core run ended `180 pass`, `0 fail`, `700 expect() calls`, and `Ran 180 tests across 7 files`.

Commands and outcomes:

- Read the brief, `CLAUDE.md`, the runtime skill, the four Python source modules, the three Python test/helper files, existing TypeScript foundations, parity configuration, and structure checks with `cat`, `rg`, and `head`.
- `uv run --frozen --quiet lodge waiting`: exited 0, last line `nothing`, with nothing waiting for an agent or the author.
- Used temporary Python scripts to translate the tests, adjust the TypeScript fixtures and types, and update JSON configuration, then inspected the generated tests against the Python assertions.
- `cd ts && bun test tests/core`: initially failed on the missing exports above, then passed with 180 tests.
- One accidental core-test invocation from the repository root failed before the correctly rooted invocation; it supplied no test evidence.
- `cd ts && bun --bun x biome check --write ...`: formatted the changed files and identified narrowing and style issues; subsequent targeted formatting completed successfully.
- `cd ts && bun --bun x tsc --noEmit -p .`: initially reported TS2769 for a potentially undefined split result, then exited 0 after correction.
- `cd ts && bun --bun x knip`: exited 0, with only the existing unmatched `scripts` pattern configuration hints.
- First `sh scripts/check-ts.sh`: the check itself exited 1, ending `355 pass`, `1 fail`, and `error: script "check" exited with code 1`.
- That failure was the structural ban on calls named `require`, which also matched the Python header-reader name; importing its unchanged export as `requireField` fixes the call sites without loosening the rule.
- A temporary experimental test expected escaped CRLF inside a quote to change on read-back and fail, but YAML correctly preserves those escaped characters; the assumption was wrong, and the experimental test was removed without changing implementation.
- Second `sh scripts/check-ts.sh`: exited 0 before the parity flip, ending `356 pass`, `0 fail`, `1144 expect() calls`, and `Ran 356 tests across 14 files`.
- `git diff`, `git status --short`, and `wc -l`: inspected scope and sizes without touching the index.
- Final `sh scripts/check-ts.sh`: exited 0 after the parity update, ending `356 pass`, `0 fail`, `1152 expect() calls`, and `Ran 356 tests across 14 files`.
The gate is rerun as the last verification after recording that result.

TypeScript differences and concerns:

- `hash_covers_undecodable_bytes` cannot preserve Python's surrogateescape byte identity with `TextEncoder`.
The retained test asserts that `a\udcffb` hashes as UTF-8 for `a�b`, because JavaScript replaces the lone surrogate with U+FFFD, rather than hashing Python's original byte 0xFF.
This is the difference explicitly allowed for reporting in the brief.
No other carried assertion needs a TypeScript exception.
- Python's rank is an arbitrary-precision integer, while the existing Task 4 `Area.rank` interface is `number | null`.
`readRank` uses `Number` and can therefore round very large ranks or reach Infinity; this port does not change that earlier interface or silently reject values Python accepts.
The carried tests do not exercise that range, and a coordinator ruling would be needed for exact arbitrary-precision rank parity.
- Task 6 should import the `require` field reader as `requireField` when calling it, because the existing structural rule recognises the literal call name `require` as a dynamic import.
- Biome permits non-null assertion warnings, and knip prints its existing unmatched scripts-pattern hints; neither prevents a successful gate.
- The runtime skill's environment-status tool is unavailable in this session, and no network operation was needed.
The coordinator still owns the outside-sandbox `scripts/check.sh` gate and all git publication steps.
