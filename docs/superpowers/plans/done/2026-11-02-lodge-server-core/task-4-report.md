# Task 4 report

Implemented the Task 4 brief on the current branch, without committing, staging, installing packages, or using the network.
The reviewer-owned `task-3-review.md` was not opened or edited.
The existing progress ledger and the brief were left untouched.

## Changes per file

| File | Change |
| --- | --- |
| `ts/src/core/errors.ts` | Added named `ValueError` and `LookupError` classes extending `Error`. |
| `ts/src/core/model.ts` | Ported every enum and dataclass into const unions and readonly interfaces, with kind discriminants, nullable fields, and the five required default-filling functions. |
| `ts/src/core/ids.ts` | Ported full identifier validation and six-byte Crockford minting, with caller-supplied entropy and `ValueError`. |
| `ts/src/core/settings.ts` | Ported settings defaults, TOML key translation, validation, unknown-key errors, ignored package sections, and named `SettingsError`. |
| `ts/src/core/text.ts` | Added all required Python text helpers, whitespace and word classes, the 20 additional digit ranges, code-point ordering, and repr escaping. |
| `ts/src/core/stamps.ts` | Added real day and timestamp validation, offset normalisation, integer civil-date arithmetic, epoch milliseconds, and instant comparison without `Date`. |
| `ts/src/core/yamlio.ts` | Ported quoting and character checks, named `YamlError`, failsafe document parsing, ordered `Map` construction, text scalars, aliases, tags, duplicate keys, diagnostic lines, and the 100-level collection bound. |
| `ts/src/core/index.ts` | Replaced the placeholder with the required public exports, keeping YAML internals private to the package. |
| `ts/knip.json` | Removed `yaml` from ignored dependencies and added `src/core/yamlio.ts` as an entry until Task 5a reads its internal exports. |
| `ts/tests/core/ids.test.ts` | Carried all identifier tests and every parametrised case. |
| `ts/tests/core/settings.test.ts` | Carried all settings tests and cases, using `Bun.TOML.parse` for TOML input. |
| `ts/tests/core/yamlio.test.ts` | Carried all YAML tests and cases, added the five brief cases, and added three alias and depth regressions. |
| `ts/tests/core/text.test.ts` | Added all 12 required text tests, including exhaustive whitespace-class comparison over all code points. |
| `ts/tests/core/stamps.test.ts` | Added all eight required timestamp tests and invalid-input `ValueError` coverage. |
| `ts/tests/core/toolchain.test.ts` | Deleted the placeholder test. |
| `ts/tests/parity.json` | Changed only the three carried Python test entries from `planned` to `ported`. |
| This report | Recorded changes, red evidence, verification, and known differences. |

No module needed splitting, and every new source and test file remains below 300 lines.
No Python source, Python tests, dependencies, or lockfiles changed.

## Test-first evidence

Before implementation, `cd ts && bun test tests/core` failed to import each new test file because the placeholder front door lacked the required exports.
Its final summary was `1 pass`, `5 fail`, `5 errors`, and `Ran 6 tests across 6 files`.
The one passing test was the old placeholder, which was subsequently deleted as required.
Each test below was present in this initial failing run, except the three explicitly labelled later regressions.
A missing export counts as the initial failure under the brief.
No carried test covered an earlier task's implementation, so no mutation was needed.
All single-parameter cases use `cases.map((c) => [c])`, including list-valued settings cases.
Exception tests assert the named class and the message pattern where Python asserts both.

### Carried `ids.test.ts`

First failure for every title and all its cases: `SyntaxError: Export named 'mintId' not found in module …/ts/src/core/index.ts`.

- `mint_id`.
- `mint_id_reads_six_bytes_into_the_alphabet`.
- `mint_id_needs_six_bytes`.
- `excluded_letters_are_not_ids`; all cases: ['i', 'l', 'o', 'u'].
- `wrong_shapes_are_not_ids`; all cases: ['d-3m8qk', 'd-3m8qk22', 'd-3M8QK2', 'd-3m8qk2\n', ' d-3m8qk2', 'd3m8qk2'].

### Carried `settings.test.ts`

First failure for every title and all its cases: `SyntaxError: Export named 'SettingsError' not found in module …/ts/src/core/index.ts`.

- `settings_defaults_when_empty`.
- `settings_reads_every_key`.
- `settings_keeps_the_defaults_of_keys_left_out`.
- `settings_rejects_unknown_key_naming_it`.
- `settings_rejects_unknown_import_key_and_section`.
- `settings_leaves_the_tables_of_other_packages_alone`.
- `settings_rejects_a_length_that_is_not_a_positive_integer`; all cases: [0, -3, True, '80', 1.5].
- `settings_rejects_sources_that_are_not_a_list_of_strings`; all cases: ['docs/a.md', [1], [''], 7].
- `settings_rejects_a_section_that_is_not_a_table`.

### Carried `yamlio.test.ts`

First failure for every title and all its cases: `SyntaxError: Export named 'loadYaml' not found in module …/ts/src/core/index.ts`.

- `yaml_scalars_stay_strings`; all cases: ['yes', 'no', 'on', '~', 'null', '14:14', '2026-10-29', '1234', '0x10', '1.5', 'true'].
- `empty_value_is_an_empty_string`.
- `nested_flow_and_block_collections_load`.
- `explicit_tags_beyond_text_are_refused`; all cases: ['key: !!int 5\n', 'key: !!set {a}\n', 'key: !!python/name:os.system\n'].
- `bad_yaml_carries_the_line`.
- `duplicate_key_is_an_error_naming_it`.
- `unreadable_character_carries_the_line`.
- `two_documents_are_an_error`.
- `deep_nesting_is_an_error_not_a_crash`.
- `surrogate_pair_escapes_join_into_one_character`.
- `lone_surrogate_escape_stays_lone`.

### New `text.test.ts`

First failure for every title: `SyntaxError: Export named 'isDigit' not found in module …/ts/src/core/index.ts`.

- `is_py_space_matches_python`.
- `strip_removes_python_whitespace_only`.
- `rstrip_like_python`.
- `split_words_like_python`.
- `split_lines_like_python`.
- `is_digit_like_python`.
- `casefold_like_python`.
- `py_repr_matches_python`.
- `code_point_length_counts_astral_once`.
- `word_class_matches_python_w`.
- `py_space_class_matches_is_py_space`.
- `by_code_point_orders_astral_after_bmp`.

### New `stamps.test.ts`

First failure for every title: `SyntaxError: Export named 'isStamp' not found in module …/ts/src/core/index.ts`.

- `stamp_with_offset_is_a_stamp`.
- `stamp_without_offset_or_seconds_is_not`.
- `impossible_date_is_not_a_stamp`.
- `offset_is_read_as_python_reads_it`.
- `instant_respects_the_offset`.
- `compare_orders_by_instant`.
- `day_must_be_real`.
- `stamp_check_ignores_the_local_time_zone`.
- `instant_refuses_non_stamp`.

### Additional YAML tests

These brief cases were also in the initial missing-`loadYaml` failure:

- `collection_key_is_refused`, with all three collection-key cases.
- `integer_like_keys_keep_their_order`.
- `non_specific_tag_is_text`.
- `str_tag_on_a_mapping_is_refused`.
- `nesting_beyond_the_bound_has_no_line`.

After implementation, `nesting_beyond_the_bound_has_no_line` also caught the initial depth off-by-one: the expected exception was absent, so the helper failed with `error: accepted YAML`.
The later regression tests were each run red before their fixes:

- `aliases_resolve_to_text_collections`: `YamlError: tag or alias cannot be constructed`; the run ended with `29 pass`, `2 fail`, including the outstanding brief depth case.
- `one_hundred_collection_levels_are_allowed`: `YamlError: the header is nested too deeply`; the run ended with `31 pass`, `1 fail`.
- `scalar_alias_keys_are_allowed`: `YamlError: found unhashable key`; the run ended with `32 pass`, `1 fail`.

The last regression checks both spaced and unspaced scalar alias keys and confirms that quoted and block scalar text resembling an alias is unchanged.
The package lexer treats `*key:` as one alias token, whereas PyYAML treats the colon as a mapping separator.
A token-aware compatibility pass inserts a space before that colon, preserving scalar contents and line numbers, before `parseAllDocuments` and the node walk.
All three later regressions now pass.

## Commands and results

Read-only inspection included `cat`, `rg`, `head`, `sed`, `wc -l`, `git status --short`, and scoped `git diff` commands over the brief, `CLAUDE.md`, the runtime skill, named Python modules and tests, probes, TypeScript configuration, and the installed YAML declarations.
These established that required dependencies were present, no sub-agents were required, no source file exceeded 300 lines, and the only parity edits were the three required status changes.
The cloud runtime skill was read, but no environment status tool was available, and no network operations were attempted.

| Command | Result or final output |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | `waiting for the author` followed by `nothing`; nothing was waiting for an agent either. |
| Python scripts under `/tmp` to write tests, generate model interfaces, update configuration, and write this report | Exit 0, no output. |
| Initial `cd ts && bun test tests/core` | `1 pass`, `5 fail`, `5 errors`, `1 expect() calls`; missing exports before implementation. |
| First implementation `bun test tests/core` | `79 pass`, `1 fail`, `207 expect() calls`; exposed the 101-level depth boundary. |
| Targeted YAML red runs | Alias-value run: `29 pass`, `2 fail`; 100-level run: `31 pass`, `1 fail`; alias-key runs: `32 pass`, `1 fail`. |
| `bun --bun x biome check --write src/core tests/core …` | Applied formatting and import ordering; intermediate runs reported informational suggestions subsequently addressed. |
| `bun --bun x tsc --noEmit -p .` | Initial runs exposed TOML return-type and tuple/narrowing issues; the final standalone run exited 0 with no output. |
| First `sh scripts/check-ts.sh`, before parity changes | Exit 0; `223 pass`, `0 fail`, `614 expect() calls`, `Ran 223 tests across 10 files`. |
| Latest standalone `cd ts && bun test tests/core` | `83 pass`, `0 fail`, `315 expect() calls`, `Ran 83 tests across 5 files`. |
| `cd ts && bun run test:structure`, after marking parity ported | `142 pass`, `0 fail`, `410 expect() calls`, `Ran 142 tests across 5 files`. |
| Synthetic `uv run --frozen python` and `bun -e` YAML comparisons | Confirmed empty text and comments become null, explicit empty documents become empty text, and identified the alias-key syntax difference subsequently fixed. |
| `bun -e` inspecting YAML lexer tokens and parser versions | Confirmed quoted and block scalars are distinguishable from alias tokens, and changing the YAML version alone does not fix unspaced alias keys. |

The required final `sh scripts/check-ts.sh` is run after writing this report, and its result is appended below.
The full Python/coordinator gate was not run, as the brief reserves it for the coordinator outside the sandbox.
No `bun install`, `bun add`, staging, commit, or push command was run.

## TypeScript differences and concerns

All carried tests hold in TypeScript, using `Map` for Python mappings and readonly arrays for tuples as required.
No carried title was removed, weakened, or changed to assert a different result.
The required helper examples all hold as specified.

The brief explicitly accepts these differences:

- `isDigit` accepts 90 additional code points through Bun's newer Unicode `Nd` property, beginning at U+10D40, which Python 3.13's Unicode 15.1 database leaves unassigned.
- `casefold` has the probe's 174 single-code-point differences from Python, including dotless i and Cherokee letters; none yields a letter of `author`, and the final sigma is explicitly normalised to `σ`.
- `pyRepr` differs at the probe's 9,988 characters assigned by Bun's newer Unicode database but left unassigned by Python's Unicode 15.1 database; examples begin U+088F, U+0897, U+0C5C, U+0CDC, U+1ACF, and U+1AD0.
- `WORD_CLASS` follows the required Unicode property class, whose broader Unicode assignment coverage is documented in probe 14.
- YAML nesting is bounded at 100 collection levels, with deeper input raising `YamlError("the header is nested too deeply")` and `line === null`, narrowing lodge 0.2's recursion-dependent limit.

The Unicode counts are the brief's documented probe results, not new exhaustive cross-runtime measurements in this task.
The whitespace-class test does exhaustively compare all code points locally.
The earlier unspaced alias-key concern was resolved rather than retained as an additional narrowing.
Knip's unmatched future `scripts` patterns are configuration hints already present in the scaffold, not unused dependencies or exports.
No further uncertainty remains from this implementation.

## Final gate

`sh scripts/check-ts.sh` exited 0.

```text
Configuration hints (2)
scripts/*.ts       knip.json  Refine entry pattern (no matches)  
scripts/**/*.ts    knip.json  Refine project pattern (no matches)
bun test v1.3.14 (0d9b296a)

 225 pass
 0 fail
 725 expect() calls
Ran 225 tests across 10 files. [863.00ms]
```
