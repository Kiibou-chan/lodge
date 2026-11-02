# Task 4 fix round 1 report

Implemented the review fixes on the current branch without committing, pushing, installing packages, or editing Python.
The reviewer-owned `task-5a-review.md` was not edited.
Read `CLAUDE.md`, the Task 4 brief, the review, and rulings d-p48gr1, d-fbhdvf, d-v9mw2d, and d-g1hrmn through lodge.
`lodge waiting` reported nothing waiting for either an agent or the author.

## Findings and failing evidence

### C-1

`ts/src/core/yamlio.ts` memoises constructed values by target node before visiting collection children, preserving shared arrays, shared maps, and recursive aliases.
`ts/tests/core/yamlio-fixes.test.ts` adds `nine_shared_anchor_levels_load_within_one_second`, with nine anchors, two references per next level, an elapsed-time bound of 1,000 ms, and reference identity, plus `recursive_alias_shares_its_container`.
Against the original implementation, the former failed with `Received: serializes to the same string` at the identity assertion, and the latter failed with `YamlError: the header is nested too deeply`.
The original two-reference fixture already met the time bound, but failed sharing; the new implementation passes both assertions.

### C-2

No parser refusals were added, per d-p48gr1.
The same test file pins every listed syntax difference with seven `parser_difference_reads` cases and six `parser_difference_refuses` cases.
The U+0085-after-colon expectation was corrected after measurement: the actual result preserves U+0085, rather than stripping it as the review stated.
Its initial output was `Expected: "b"`, `Received: "\u0085b"`.
To demonstrate sensitivity of every final case, temporarily replaced `loadYaml` with an immediate `throw new YamlError("mutation")` for the seven accepted cases, then an immediate `return null` for the six refused cases.
Output: `0 pass, 7 fail` with `YamlError: mutation`, and `0 pass, 6 fail` with `Expected to throw`, respectively.
Both mutations were reverted.
The known differences below enumerate the cases.

### C-3

`checkReader` now reports the decimal code point, per d-fbhdvf.
`unreadable_character_names_decimal_code_point` first failed with `Expected: "unreadable character 1"`, `Received: "unreadable character '\x01'"`.
Task 5a's document reader already propagates this message, so its production code needed no adjustment.

### C-4

Set `prettyErrors: false`.
`parser_message_has_no_excerpt_or_embedded_line` asserts the complete bare message and the separate line number.
Before the fix, it expected `Nested mappings are not allowed in compact mappings` and received that text followed by `at line 1, column 4:`, a source excerpt, and a caret.

This exposed Task 5a's `bad_code_is_problem_1 "a\n"` fixture relying on the excerpt containing the word `code`.
Its failing output after the YAML fix was `Expected to contain: "code"`, `Received: "the header is not valid YAML: Missing closing \"quote"`.
Updated `ts/tests/core/fileformat.test.ts` to encode the code value with `JSON.stringify`, so the newline is a valid quoted scalar and the test exercises code validation.
All original cases and assertions remain.
No Task 5a production code changed.

### C-5

Disabled the package's duplicate-key diagnostic with `uniqueKeys: false`, retained the walk's duplicate check, and check document parse errors before construction.
The three `syntax_precedes_construction` cases first failed with expected/received lines `3/1`, `4/2`, and `3/1`, for an earlier tag, duplicate key, and collection key, respectively.
All now report the later syntax error's line.

### C-6

No core change, per d-v9mw2d.
The environment exception and the future entry-point obligation are recorded below.
No new test belongs in this core fix round under that ruling.

### C-7

Unresolved key aliases are checked before scalar-key validation, and unresolved aliases in either position name their source through `pyRepr`.
Both `undefined_alias_names_source` cases first expected `found undefined alias 'x'` and received `found unhashable key` for a key and `found undefined alias` for a value.
Both now also assert line 1.

### M-1

Strengthened `compare_orders_by_instant` in `ts/tests/core/stamps.test.ts` with the reversed pair and `toBeLessThan(0)`.
Against the review's mutation, `return instant(a) > instant(b) ? 1 : 0`, it failed with `Expected: < 0`, `Received: 0`, and `0 pass, 1 fail`.
Reverted the mutation.

### M-2

Strengthened `day_must_be_real` with 1900-02-29 false and 2000-02-29 true.
Replacing the century condition with `true` failed with `Expected: false`, `Received: true`, and `0 pass, 1 fail`.
Reverted the mutation.

### P-1

`ts/src/core/text.ts` compiles `SPACE`, `EDGES`, `TRAILING`, and `RUN` once from the sole whitespace class, and uses a module-level `ReadonlySet` for line breaks.
`isPySpace` tests only the first code point, preserving its previous behaviour for multi-character inputs.
No tests were added or strengthened for this allocation refactor; the existing exhaustive whitespace-equivalence test and text tests pass.

### P-2

`ts/src/core/ids.ts` derives its module-level identifier expression from `ALPHABET`.
No tests were added or strengthened for this refactor; existing identifier tests pass.

### P-3

`ts/src/core/model.ts` defines `WithDefaults<T, K>` once and applies it to all five default-filling functions.
No runtime behaviour changed, and no tests were added or strengthened for this type refactor.
Type checking and the existing model consumers pass.

### P-4

This report records the rulings and outstanding differences explicitly, including the measured U+0085 correction.
No claim of an independent exhaustive Unicode remeasurement is made here.

### D-1

`ts/src/core/stamps.ts` exports `orderInstant`, which treats a real bare day as midnight UTC and otherwise delegates to the stamp validator and instant calculation.
The existing wildcard export in `#core` exposes it unchanged, per d-hshapm.
`ts/tests/core/order-instant.test.ts` tests a day, a stamp, both directions of the specified day/stamp comparisons, an invalid string, and an impossible day, with `ValueError` for invalid inputs.
Before implementation, the test failed to load with `SyntaxError: Export named 'orderInstant' not found`.

### D-2

Recorded the integer-like settings-key ordering difference below, as the review permits.
No settings API or tests changed.

## Known differences and obligations

- C-2, d-p48gr1: TypeScript accepts a tab after a mapping colon, and a tab-only line after a mapping, where PyYAML refuses them.
- C-2: TypeScript accepts empty implicit keys in both block and flow mappings, where PyYAML refuses them.
- C-2: TypeScript accepts anchor names containing a dot or slash, where PyYAML restricts anchor characters to `[0-9A-Za-z_-]`.
- C-2: `a: \u0085b` loads with the value `\u0085b` in TypeScript, whereas PyYAML refuses the header.
- C-2: TypeScript refuses U+0085, U+2028, and U+2029 as line breaks in the reviewed two-key forms, whereas PyYAML reads them as two keys.
- C-2: TypeScript refuses a lone CR as the line ending in the reviewed two-key form, whereas PyYAML reads it.
- C-2: TypeScript refuses double-quoted and flow-sequence continuations at column zero, whereas PyYAML reads them.
- C-3, d-fbhdvf: the brief's character-repr message is superseded by the decimal-code-point message, restoring lodge 0.2 parity.
- C-6, d-v9mw2d: the `yaml` dependency reads `LOG_TOKENS` and `LOG_STREAM` and can print header text when either is enabled.
  Plan 3's server entry point must delete both environment variables before serving and test this there.
- D-1, d-g1hrmn: TypeScript orders a bare day against a stamp as midnight UTC, replacing lodge 0.2's naive/aware datetime comparison error.
- D-2: plain JavaScript settings objects enumerate integer-like keys before other keys.
  Thus `zz` followed by `"1"` reports `unknown key 1`, and `length.foo` followed by `length."7"` reports `length.7`, rather than Python's first textual key.
- Existing Unicode differences remain as recorded by the review: `isDigit` at 90 code points, `casefold` at 174, and `pyRepr` at 9,988 unassigned Python code points.
  Those counts were independently measured by the reviewer, not remeasured in this round.

## Commands and results

Read-only commands included `cat`, `sed`, `rg`, `git status --short`, and `git diff` for requirements, source, tests, and change inspection.
The lodge commands were `uv run --frozen --quiet lodge waiting` and `uv run --frozen --quiet lodge show <id> --reasoning` for the four rulings above; each exited 0.
Local temporary Python scripts applied edits and ran the reversible mutations; they did not edit Python repository files.

- Initial `cd ts && bun test tests/core/yamlio-fixes.test.ts tests/core/order-instant.test.ts`: `12 pass`, `11 fail`, `1 error`, `Ran 23 tests across 2 files. [74.00ms]`.
- Targeted mutation runs used `bun test tests/core/stamps.test.ts -t <name>` and `bun test tests/core/yamlio-fixes.test.ts -t <name>`.
  Their final counts were `0 pass, 1 fail` for each stamp mutation, `0 pass, 7 fail` for accepted-parser cases, and `0 pass, 6 fail` for refused-parser cases.
- First post-fix `cd ts && bun test tests/core`: `202 pass`, `1 fail`, identifying the Task 5a fixture described above.
- `cd ts && bunx --no-install biome check --write src/core tests/core/yamlio-fixes.test.ts tests/core/order-instant.test.ts tests/core/stamps.test.ts tests/core/fileformat.test.ts`: `Checked 16 files in 12ms. Fixed 4 files. Found 11 warnings.`
- After fixture repair, `cd ts && bun test tests/core`: `203 pass`, `0 fail`, `735 expect() calls`, `Ran 203 tests across 10 files. [380.00ms]`.
- `cd ts && bun --bun run check`: `379 pass`, `0 fail`, `1187 expect() calls`, `Ran 379 tests across 16 files. [1004.00ms]`, exit 0.
  Biome reported non-fatal warnings, and knip reported two existing unmatched script-pattern hints.

The final required gate result is appended below after execution.

`sh scripts/check-ts.sh` exited 0.
Its last lines were:

```text
bun test v1.3.14 (0d9b296a)

 379 pass
 0 fail
 1187 expect() calls
Ran 379 tests across 16 files. [1014.00ms]
```
