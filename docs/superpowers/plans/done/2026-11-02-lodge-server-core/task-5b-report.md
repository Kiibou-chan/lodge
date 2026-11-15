# Task 5b report

Implemented the draft port and carried the record text tests.
No commits, staging, pushes, package installation, Python changes, or reviewer-file edits were made.

## Changes per file

- `ts/src/core/drafts.ts`: ported draft parsing, key validation, record construction, caller-supplied IDs, dates, and area names, with source and key-line problems.
  `Draft.headerText` is required, and the interface has no default-filling function.
  A private value formatter preserves Python representations for non-string IDs.
- `ts/src/core/index.ts`: exported `Draft`, `parseDraft`, and `recordFromDraft`.
- `ts/tests/core/drafts.test.ts`: ported every Python draft test and parameter case, plus two non-string ID cases.
- `ts/tests/core/fileformat-text.test.ts`: carried every Python record text test and parameter case.
- `ts/knip.json`: removed `src/core/headers.ts` from `entry`, while retaining `document.ts` and `fields.ts` for Task 6.
- `ts/tests/parity.json`: changed both assigned Python test files to `ported` after the first successful full gate.
- This report records verification and differences.

Task 5a's implementation files needed no permanent changes.
The temporary mutations of `fileformat.ts` were restored after every run.
No module or test file needed splitting.

## Test-first evidence

All Python draft tests were written before `drafts.ts` or its exports existed.
Their first run, `cd ts && bun test tests/core/drafts.test.ts`, ended with:

```text
SyntaxError: Export named 'parseDraft' not found in module 'ts/src/core/index.ts'.
0 pass
1 fail
1 error
```

This missing-export failure covers these tests, including all eight syntax cases:

- `draft_without_id_or_date`.
- `draft_keeps_header_and_body`.
- `record_from_draft_fills_id_date_area`.
- `existing_entry_takes_its_area_from_the_caller`.
- `draft_carries_base_and_area`.
- `area_draft`.
- `draft_non_utf8_is_problem`.
- `draft_syntax_problems`.
- `draft_may_not_set_a_date_unless_imported`.
- `draft_missing_a_required_field_is_a_problem`.
- `draft_id_must_match_the_given_one`.
- `spec_draft_without_an_area_is_a_problem`.
- `deep_nesting_in_a_draft_is_a_problem`.
- `problem_from_a_draft_carries_the_key_line`.
- `draft_keeps_the_indentation_of_its_first_line`.
- `draft_with_a_blank_title_is_a_problem`.

The added `draft_non_string_id_is_reported %p %p` cases were first run against the initial implementation, which passed an array or mapping to the string-only `pyRepr`.
Both failed with `TypeError: s.includes is not a function`.
A recursive private formatter fixed both cases.

For each carried test below, the mutation inserted an unconditional `throw new ValueError("mutation: FUNCTION unavailable")` at the start of the named `fileformat.ts` function.
These are broad function-disablement mutations, rather than narrowly targeted character mutations.
The mutation was restored in a `finally` block after each command.
The command was `cd ts && bun test tests/core/fileformat-text.test.ts --test-name-pattern NAME`.
Every case selected by each name failed:

| Test name | Disabled function | First result |
| --- | --- | --- |
| `deep_nesting_is_problem_1` | `parseRecord` | 1 fail |
| `indentation_of_the_first_line_is_kept` | `parseRecord` | 1 fail |
| `blank_lines_around_a_block_are_dropped` | `parseRecord` | 1 fail |
| `blank_required_string_is_problem_1` | `parseRecord` | 2 fail |
| `quote_text_keeps_line_breaks_and_tabs` | `writeRecord` | 1 fail |
| `other_quote_parts_keep_the_control_character_ban` | `writeRecord` | 2 fail |
| `quote_text_still_refuses_other_control_characters` | `writeRecord` | 1 fail |
| `json_dumps_default_escapes_read_back_as_emoji` | `parseRecord` | 1 fail |
| `lone_surrogate_escape_is_problem_1` | `parseRecord` | 1 fail |
| `write_names_the_field_that_would_read_back_differently` | `writeRecord` | 1 fail |
| `slug_is_capped_at_a_word_boundary` | `slug` | 1 fail |
| `slug_cut_never_splits_a_word_unless_one_word_is_too_long` | `slug` | 1 fail |
| `new_record_path_stays_short_for_long_titles` | `newRecordPath` | 1 fail |

An incidental additional mutation run with pattern `title` also failed, then restored the same source.

## Commands and results

- `uv run --frozen --quiet lodge waiting`: exited 0, with nothing waiting for an agent or the author.
- The draft red command and each carried-test mutation command are recorded above.
- `cd ts && bun test tests/core/drafts.test.ts tests/core/fileformat-text.test.ts`: initially 38 pass, 0 fail, and 136 assertions before the two additional ID cases.
- `cd ts && bun test tests/core/drafts.test.ts --test-name-pattern draft_non_string_id`: initially 0 pass and 2 fail.
- `cd ts && bunx --no-install biome check --write ...`: formatted the changed TypeScript files and configuration using existing dependencies.
  The last formatting run checked two files and fixed two files.
- First `sh scripts/check-ts.sh`: failed at `drafts.ts` with TS2345, because an unknown ID value was passed to `pyRepr`.
- Second `sh scripts/check-ts.sh`: exited 0, with no dependency violations, 419 pass, 0 fail, and 1,329 assertions across 18 files.
- Final `sh scripts/check-ts.sh`, after parity updates: exited 0, with 419 pass, 0 fail, and 1,333 assertions across 18 files.
  Its last summary line was `Ran 419 tests across 18 files` (timing varies).

## TypeScript differences and concerns

`json_dumps_default_escapes_read_back_as_emoji` cannot assert Python's default ASCII escaping through JavaScript's `JSON.stringify`, which emits literal emoji.
The retained test title asserts JavaScript's behaviour and explicitly supplies the identical escaped surrogate pair that Python produces, then verifies the original parsing and quote-equality assertions.

`draft_non_utf8_is_problem` uses an explicit U+DCFF surrogate in the input string to represent Python's `surrogateescape` result, because JavaScript's normal UTF-8 decoder does not expose that error mode.
The original problem, source, check, and message assertions hold.

No other carried assertion was weakened or requires a TypeScript exception.
Existing Biome warnings and knip unmatched-script-pattern hints remain non-fatal.
The added text tests also use three non-null assertions for single-parameter case typing, which Biome warns about.
The mutation checks demonstrate that every carried test detects disabled behaviour, but their breadth offers less precision than targeted mutations.
No other uncertainties remain.
