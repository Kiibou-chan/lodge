# Task 5a fix round 1 report

Implemented the review findings and the three parked items on the current branch, without committing, pushing, installing dependencies, or changing Python.
The reviewer-owned `task-5b-review.md` was left untouched.

## Findings and failing evidence

### D-1: Python whitespace regression tests

Added four tests in `ts/tests/core/fileformat-edges.test.ts`.
The three statements round-trip through `writeRecord` and `parseRecord`, including the reasoning, and the title test checks the non-empty-string diagnostic.
Each mutation below was applied individually and restored in a `finally` block.
The final isolated runs used `cd ts && bun test tests/core/fileformat-edges.test.ts -t 'feff|python_whitespace'`.
Each exited 1 with `3 pass`, `4 filtered out`, `1 fail`, and `Ran 4 tests across 1 file`.

| Mutation | Failing test | Failing output |
| --- | --- | --- |
| `hasReasoningHeading`: `rstrip(line)` becomes `line.trimEnd()` | `feff_after_reasoning_heading_round_trips` | `ValueError: the statement holds a line reading '## Reasoning'` |
| `splitReasoning`: `rstrip(line)` becomes `line.trimEnd()` | `feff_after_reasoning_heading_round_trips` | `ValueError: the record would not read back unchanged: statement reads back as 'A'` |
| `trimBlock`: `rstrip(lines.join("\n"))` becomes `lines.join("\n").trimEnd()` | `trailing_feff_round_trips` | `ValueError: the record would not read back unchanged: statement reads back as 'S.'` |
| `trimBlock`: `strip(lines[0])` becomes `lines[0].trim()` | `opening_feff_line_round_trips` | `ValueError: the record would not read back unchanged: statement reads back as 'S.'` |
| `readStr`: `strip(value)` becomes `value.trim()` | `python_whitespace_title_is_empty` | `Expected to contain: "non-empty"`, received `"title holds U+001C, which a header cannot carry"` |

All five mutants were killed, both before the implementation changes and again against the final implementation.
The original `lines[0]!` spelling lost its assertion during the warning cleanup; the final mutation uses the narrowed `lines[0]` spelling.

### C-1: safe ranks

`fields.ts` now refuses a rank unless `Number.isSafeInteger(Number(value))` holds, using the existing format message and `rank` key.
`rank_safe_integer_boundary` reads `2 ** 53 - 1` exactly.
`unsafe_rank_is_problem` refuses both `12345678901234567890` and `9007199254740992`, and checks that the problem names `rank` at line 4.
Before the fix, `cd ts && bun test tests/core/fileformat-edges.test.ts` exited 1 with `5 pass`, `3 fail`, and `Ran 8 tests across 1 file`.
Both unsafe-rank cases failed with `Expected: "problem"`, `Received: "area"`.
The third failure was C-2 below.
A separate boundary mutation, `return Number(value) - 1`, failed the boundary test with expected `9007199254740991`, received `9007199254740990`, ending `0 pass`, `7 filtered out`, `1 fail`.
This narrowing is a known difference from Python, authorised by d-4m6m35.

### C-2: nested representations

`fileformat.ts` now represents Change, Quote, NumberHandle, and Imported values by their field sets, with Python's class names and Action enum representation.
`nested_change_read_back_repr` pins the change-entry case with a trailing space.
Its first run, before the fix, failed with:

```text
Expected message: "the record would not read back unchanged: changes reads back as (Change(entry='s-4kq1zm', action=<Action.EDIT: 'edit'>),)"
Received message: "the record would not read back unchanged: changes reads back as ([object Object],)"
```

### C-3: surrogate decoding follow-up

No encoding or decoding behaviour changed, as directed by d-0q54zn.
The ledger now names the first stored-byte decoder in plan 2's store or plan 4's importer and the corresponding hash change.
Both surrogate cases and the reach of `bad_utf8_is_problem_1` are listed below.
This documentation change has no new executable test.

### C-4: Python escape forms

`control_character_is_problem_1` retains its title and seven character cases, but now supplies exactly `\\x01`, `\\x7f`, `\\x85`, `\\u2028`, `\\ufffe`, `\\t`, and `\\n` to YAML.
The test's map keeps the escaped form beside its character.
For each escape individually, a temporary `document.ts` loader mutation replaced that escape in `headerText` with `z` before calling `loadYaml`, simulating failure to decode that escape.
Each `cd ts && bun test tests/core/fileformat.test.ts -t control_character_is_problem_1` run exited 1 with expected `"problem"`, received `"decision"`, ending `6 pass`, `33 filtered out`, `1 fail`, and `Ran 7 tests across 1 file`.
All seven mutations were restored.

### P-1: module constants

Added unexported `ID_KIND` and `CODE` in `fields.ts`, and `PLAIN`, `SLUG_WORDS`, and `SLUG_CHARS` in `fileformat.ts`.
The ID map is constructed once, and the patterns and slug limits have the Python constant names.
Existing code, slug, ID, and writer tests exercise these refactorings; no new test was needed.

### P-2: retained facts

Added comments for `trimBlock` preserving indentation, `keyLine` using the first dotted component and the opening fence, `readMap` allowing breaks and tabs only in its multiline key, `readDate` accepting a bare day only when imported, and `writeRecord` raising ValueError on failed read-back.
No executable behaviour changed.

### P-3: duplication

`fileformat-write.test.ts` now uses one `refused(write, pattern)` helper that catches once, checks ValueError and the message, and fails when no exception is thrown.
Each formerly duplicated record construction and writer invocation is now supplied once.
Dropped the identity map in `samples.ts`, and used `bytesToHex(sha256(bytes)).slice(0, 12)` in `fileformat.ts`.
The existing writer and hash tests pass; no new assertions were added for these refactorings.

### D-2: complete read-back field lists

Extracted the existing message-ordered lists into `ts/src/core/read-back-fields.ts`, imported by `fileformat.ts`.
`read-back-fields.test.ts` reads that constant with the TypeScript syntax parser and compares each list to `Object.keys` of its default-filled model, excluding `kind`.
It constructs the models through `#core`, preserving the front-door rule.
Removing `reasoning` from the decision list, `restsOn` from the spec list, and `rank` from the area list individually made `read_back_fields_cover_model` fail with `expect(received).toEqual(expected)` and the missing field in the expected array.
Each `cd ts && bun test tests/core/read-back-fields.test.ts` mutation run exited 1 with `0 pass`, `1 fail`, and `Ran 1 test across 1 file`.
The final test was rerun against all three mutants after changing its source inspection method.

### D-3: alias follow-up

Added a Task 6 brief instruction to the ledger: import `require as requireField` and call `requireField`, because calls named `require` are refused by the existing dynamic-code rule.
No rule was loosened, and no executable test was needed.

### d-f18pz7: warnings fail the gate

`package.json` now runs `biome check --error-on-warnings .`.
Fixed all warnings in code without disabling any rule.
`document.ts` uses an explicit code-point guard and a narrowed first line.
`headers.ts` uses `mapString` to narrow the values already validated by `readMap`.
`fields.ts` uses optional access on the code point of the known non-empty bad character.
The problem tests use a slice for the key and an explicit imported header, and the text tests use readonly parameter tuples.
`samples.ts` and the text tests use template strings where required.
The first Biome fix pass ended `Checked 45 files in 19ms. Fixed 9 files. Found 15 warnings.`
The remaining warnings were corrected manually; the final check reports no warnings.

### Parked Task 3: literal structure table

Added `ts/tests/structure/table.test.ts`, pinning every PACKAGES row and CORE_NPM to d-k5swcq's literal values.
Giving core an app edge failed with expected `["core", []]`, received `["core", ["app"]]`.
Removing `@noble/hashes` from CORE_NPM failed with that dependency missing from the received array.
Each `cd ts && bun test tests/structure/table.test.ts` mutation run exited 1 with `0 pass`, `1 fail`, and `Ran 1 test across 1 file`.
Both mutations were restored.

## Known TypeScript differences and tests that cannot hold

- `bad_code_is_problem_1`, case `a\n`, retains its title and escaped-newline YAML input.
Python's test places a literal newline inside the quoted scalar, which YAML folds to a space; the TypeScript YAML layer refuses the column-zero continuation instead.
The TypeScript test exercises a decoded newline via an escape, as noted in Task 4 N-1, under ruling d-p48gr1.
- `hash_covers_undecodable_bytes` retains the TypeScript assertion that `a\udcffb` hashes as `a�b`.
Python re-encodes U+DC80 to U+DCFF as their original bytes under `surrogateescape`; TextEncoder replaces them with U+FFFD.
- For U+D800 to U+DC7F and U+DD00 to U+DFFF, Python raises UnicodeEncodeError, while TypeScript hashes the replacement character U+FFFD.
This second surrogate case was missing from the earlier report.
No input of this plan decodes stored bytes, and no TypeScript writer stores lone surrogates, so stored-file reach waits for d-0q54zn's later decoding work.
`bad_utf8_is_problem_1` currently proves refusal of a synthetic surrogate, not the correctness of a stored-byte decoder.
- Python accepts arbitrary-precision ranks; TypeScript now refuses all values beyond the safe-integer range as a format problem naming `rank`, under d-4m6m35.

## Commands and validation

Read the requirements first, then CLAUDE.md, the Task 5a brief, review, prior report, relevant source and tests, and ledger using `cat`, `sed`, `rg`, `head`, and `tail`.
`uv run --frozen --quiet lodge waiting` exited 0, ending `nothing`, with nothing waiting for either an agent or the author.
`uv run --frozen --quiet lodge show <id> --reasoning` read d-4m6m35, d-k5swcq, d-0q54zn, d-p48gr1, and d-f18pz7, all exiting 0.
Temporary Python scripts wrote edits and ran the mutations described above, restoring each original file after its run.
All mutation processes exited 1 because of assertion failures, not compilation errors.

`cd ts && bun test tests/core/fileformat-edges.test.ts tests/core/read-back-fields.test.ts` passed after the functional fixes, ending `9 pass`, `0 fail`, and `Ran 9 tests across 2 files`.
`cd ts && bunx --no-install biome check --write --unsafe .` fixed templates and formatting; the remaining assertions were resolved manually rather than suppressing rules.
Subsequent `bunx --no-install biome check --write .` ended `Checked 45 files in 22ms. Fixed 1 file.`
`bunx --no-install tsc --noEmit -p .` initially caught an overly narrow expected-array type in the field-list test, then exited 0 with no output after correction.
An intermediate whole-suite run caught the field-list test's direct internal import with `front-door: tests/core/read-back-fields.test.ts -> src/core/read-back-fields.ts`; source inspection fixed it without changing the rule.
The subsequent `cd ts && bun test` exited 0 with `429 pass`, `0 fail`, `1352 expect() calls`, and `Ran 429 tests across 21 files`, including Task 5b.

`cd ts && bun --bun run check` exited 0.
Its output included `Checked 45 files in 13ms. No fixes applied.`, `no dependency violations found (52 modules, 115 dependencies cruised)`, and ended:

```text
429 pass
0 fail
1352 expect() calls
Ran 429 tests across 21 files.
```

Knip still gives its two existing unmatched `scripts/*.ts` and `scripts/**/*.ts` configuration hints.
`git diff --check` exited 0 with no output.
`git diff --stat`, `git status --short`, and `wc -l` were used to inspect scope and size without staging files.
The runtime skill was read; its environment-status tool is unavailable, and no network operation was needed.

The required final verification is `sh scripts/check-ts.sh`, run after writing this report, with the same full check and test totals above.
The coordinator retains the whole Python-plus-TypeScript gate and publication steps.
