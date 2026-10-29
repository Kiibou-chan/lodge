# Task 3 report: records, identifiers, settings, and the file format

## Failing output before the code

`uv run pytest tests/core -q` before any implementation: 6 collection errors, one per test file (every test in a file fails at import, so the failing line is the file's):

- `tests/core/test_ids.py` (5 tests): `ImportError: cannot import name 'is_id' from 'lodge.core'`
- `tests/core/test_settings.py` (9): `ImportError: cannot import name 'CoreSettings' from 'lodge.core'`
- `tests/core/test_yamlio.py` (8): `ImportError: cannot import name 'YamlError' from 'lodge.core'`
- `tests/core/test_fileformat.py` (18): `ImportError: cannot import name 'Action' from 'lodge.core'`
- `tests/core/test_fileformat_problems.py` (22): same `Action` ImportError
- `tests/core/test_drafts.py` (12): same `Action` ImportError

(Counts are test functions; parametrised ones expand further.)

## What was built

Modules in `src/lodge/core/`, exported through `lodge.core`:
`model.py`, `ids.py`, `settings.py`, `yamlio.py`, `fileformat.py`, `drafts.py` (the brief's six), plus four helpers that the 300-line limit and the shared rules called for:
`fields.py` (typed header readers, `FormatError`), `document.py` (fences, reasoning split, `read_with`), `headers.py` (decision, specification, and area built from a header mapping, the one home of the field rules, shared by files and drafts).
Tests in `tests/core/` (`test_ids`, `test_settings`, `test_yamlio`, `test_fileformat`, `test_fileformat_problems`, `test_drafts`, and `samples.py`), each under 300 lines.
`vulture_allow.py` gained one line for PyYAML's `yaml_implicit_resolvers` class attribute.

Decisions inside the brief's gaps:
- `write_record` and `write_area` parse their own output and raise `ValueError` unless it reads back equal, so the writer never emits a file the parser rejects.
- Header strings holding C0, C1, U+2028, U+2029, lone surrogates, U+FFFE, or U+FFFF are problem 1 (YAML cannot read them back from a quoted string).
- `load_yaml` raises `YamlError(ValueError)` with a `line`; it also refuses explicit tags beyond text (`!!int`) and duplicate keys.
- `decided_by` is written plain when it matches `[A-Za-z0-9][A-Za-z0-9._-]*`, else as a JSON string; `attachments` and `imported_from.file` are JSON strings (the brief does not say).
- `record_from_draft`: `date` given means a new record (a draft date is refused unless `imported_from`, which keeps the draft's date); `date=None` means an existing record, whose draft must carry its date. A draft `id` must equal the given one; a draft `area`/`name` must equal a given `area`.
- `area_path(name)` is exported beyond the brief's list (later tasks place area files).
- `parse_core_settings` rejects unknown sections other than `store` and `hook` (owned by `gitstore` and `hook`), so the plan's "unknown section is an error" lives in core.
- Link and change IDs must carry the right prefix (`d-` for decisions, `s-` for entries); a spec entry's area is the folder name and must be lower-case words joined by hyphens.

## Final gate

`sh scripts/check.sh`: ruff format clean (38 files), ruff clean, mypy strict clean (32 source files), vulture clean, `388 passed in 0.60s` (structure test included).

## Concerns

- `slug` is exactly as briefed (at most six words, no length cap), so a title of very long words could exceed a file-name limit; a cap is a spec change, left to the author.
- Task 8 (edits) must pass `date=None` and the existing `area` for existing records; the rule is in `record_from_draft`'s docstring.
- `lodge.core.__init__` exports 30 names; the helper modules (`fields`, `document`, `headers`) stay private to core.

## Fix round 1

Findings and where each is fixed (all in `src/lodge/core/`), with its covering tests:

- I1 deep nesting: `load_yaml` catches `RecursionError` and raises `YamlError("the header is nested too deeply")`; tests `test_yamlio.py::test_deep_nesting_is_an_error_not_a_crash`, `test_fileformat_text.py::test_deep_nesting_is_problem_1`, `test_drafts.py::test_deep_nesting_in_a_draft_is_a_problem` (1,000 deep).
- I2 slug: capped at 60 characters, cut at the last hyphen at or before position 60, one over-long first word cut at 60, computed once in `new_record_path`; tests `test_slug_is_capped_at_a_word_boundary`, `test_slug_cut_never_splits_a_word_unless_one_word_is_too_long`, `test_new_record_path_stays_short_for_long_titles`.
- M1 first-line indentation: new `trim_block` (drops leading blank lines and trailing whitespace) used for statements, reasoning, intros, and draft bodies; tests `test_indentation_of_the_first_line_is_kept`, `test_blank_lines_around_a_block_are_dropped`, `test_draft_keeps_the_indentation_of_its_first_line`.
- M2 blank strings: `read_str` refuses whitespace-only values; tests `test_blank_required_string_is_problem_1` (`title`, `decided_by`), `test_draft_with_a_blank_title_is_a_problem`.
- M3 (ledger ruling) quote text: `quote.text` alone may hold tab, newline, and carriage return, written as JSON escapes; `quote.where`, `quote.when`, and every other header string keep the ban; tests `test_quote_text_keeps_line_breaks_and_tabs`, `test_other_quote_parts_keep_the_control_character_ban`, `test_quote_text_still_refuses_other_control_characters`.
- M4 (ledger ruling) surrogate pairs: the loader joins escaped pairs into the character they encode in every scalar, keys included; a lone surrogate stays problem 1; tests `test_surrogate_pair_escapes_join_into_one_character`, `test_lone_surrogate_escape_stays_lone`, `test_json_dumps_default_escapes_read_back_as_emoji`, `test_lone_surrogate_escape_is_problem_1`.
- M5 wrong cause: `write_record` and `write_area` name the first field that reads back differently; test `test_write_names_the_field_that_would_read_back_differently` (date normalisation, CRLF, trailing blank line).
- M6 draft lines: `Draft` gained a last field `header_text: str = ""`, so `record_from_draft` problems carry the key's line (the plan's `Draft` signature gains one defaulted field, to be noted in the ledger); test `test_problem_from_a_draft_carries_the_key_line`.
- M7: `settings.py` branches once on the table-or-key case; `ids.py` builds its pattern from `ALPHABET` and `ID_LENGTH`; behaviour unchanged, covered by the existing settings and id tests.
- M8: no change; per the ledger ruling core keeps accepting `store` and `hook`, and the point goes to Task 9's brief.

New tests that failed before the code (17 failures against the unfixed code, pytest `FAILED` lines):

- test_drafts.py::test_deep_nesting_in_a_draft_is_a_problem
- test_drafts.py::test_problem_from_a_draft_carries_the_key_line
- test_drafts.py::test_draft_keeps_the_indentation_of_its_first_line
- test_drafts.py::test_draft_with_a_blank_title_is_a_problem
- test_fileformat_text.py::test_deep_nesting_is_problem_1
- test_fileformat_text.py::test_indentation_of_the_first_line_is_kept
- test_fileformat_text.py::test_blank_lines_around_a_block_are_dropped
- test_fileformat_text.py::test_blank_required_string_is_problem_1[title]
- test_fileformat_text.py::test_blank_required_string_is_problem_1[decided_by]
- test_fileformat_text.py::test_quote_text_keeps_line_breaks_and_tabs
- test_fileformat_text.py::test_json_dumps_default_escapes_read_back_as_emoji
- test_fileformat_text.py::test_write_names_the_field_that_would_read_back_differently
- test_fileformat_text.py::test_slug_is_capped_at_a_word_boundary
- test_fileformat_text.py::test_slug_cut_never_splits_a_word_unless_one_word_is_too_long
- test_fileformat_text.py::test_new_record_path_stays_short_for_long_titles
- test_yamlio.py::test_deep_nesting_is_an_error_not_a_crash
- test_yamlio.py::test_surrogate_pair_escapes_join_into_one_character

Command: `sh scripts/check.sh`; output: ruff format 39 files clean, ruff clean, mypy strict clean (33 source files), vulture clean, `410 passed in 1.89s`.
