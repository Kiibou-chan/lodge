# Brief: Task 4 of `docs/superpowers/plans/2026-11-02-lodge-server-core.md`

You build Task 4 of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
You have no network: never run `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-report.md`: what you changed per file, each test you added or carried with its first failing output (or the mutation it failed against), the commands you ran and their last lines, every test that cannot hold in TypeScript with the reason, and anything you were unsure of.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## From the coordinator

- Tasks 1 to 3 are done: the gate in `ts/` holds the structure rules (`ts/tests/structure/`) and the parity table (`ts/tests/parity.json`, checked by `ts/tests/parity.test.ts`); Task 3 is still under review, so a later fix round may touch those files, never yours.
- `bun test` in `ts/` runs every test; `bun run test:structure` runs the structure and parity tests alone.
- The probes the brief names are items of `docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md`, their sources in `probes/` beside it; read an item when the brief cites it.

## Global Constraints

- Builders are Codex (`codex exec`), one task per brief; a brief holds these constraints and its task, and Codex sees only its brief, `CLAUDE.md`, and the repository.
- In Codex's sandbox git's index is read-only, sockets are refused, and there is no network (`docs/superpowers/plans/done/2026-10-31-lodge-viewer.md:21`): the builder never stages, commits, or pushes, and never runs `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
- The builder's gate: `sh scripts/check-ts.sh`, which runs Biome, `tsc`, dependency-cruiser, knip, and `bun test`, all on Bun (`bun --bun run check`, d-xph4ac); none needs a socket or the network, and all run with a read-only home and temporary folder (probe 13).
- The coordinator's gate after every task: `sh scripts/check.sh` green outside the sandbox (lodge 0.2's gate, then the TypeScript gate, d-xk6qtn), then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `server-core` to `origin`; never `main`.
- lodge 0.2 keeps working: `src/`, `tests/`, `pyproject.toml`, and `uv.lock` are not edited; the only Python file this plan adds is `scripts/differential_dump.py` (Task 12).
- Test-first: each carried or new test is written and seen failing before its code (a missing module or export counts as failing); a carried test over code an earlier task already ported is seen failing against a mutation of that code, which the builder names in its report and then reverts (d-mfayy5); every existing test keeps passing, edited only where a task says so.
- Porting (d-88p8h9):
  - each Python module a task names becomes the TypeScript module or modules it names, with the same behaviour; nothing is added that the Python does not do, unless the task says so;
  - each Python test becomes a TypeScript test titled with the Python function's name without `test_` (`test_ranked_areas_first_then_by_name` becomes `test("ranked_areas_first_then_by_name", …)`), in the TypeScript file the parity table names;
  - a parametrised test with one parameter becomes `test.each(cases.map((c) => [c]))("name %p", (value) => …)`, so that a list-valued case such as `[1]` reaches the test whole, where `test.each(cases)` would hand it `1` (probe 15); one with several parameters becomes `test.each([[a, b], …])("name %p %p", (a, b) => …)`; the title is the name, a space, then the case, with every case of the Python list;
  - an assertion asserts what the Python one asserts, no weaker: `==` on values becomes `toEqual` or `toBe`, `pytest.raises(E, match=…)` becomes `toThrow` with the class and the pattern;
  - a test that cannot hold in TypeScript keeps its title, asserts the TypeScript behaviour, and is listed in the task's report with the reason, for the review and a coordinator ruling;
  - the task's last step flips its files in `ts/tests/parity.json` from `planned` to `ported`, and the parity test then checks every name.
- Types: a frozen dataclass becomes an `interface` with `readonly` fields and, where a call in `src/lodge` or `tests` leaves one of its defaulted fields out, a function of the same name in camelCase that fills them, defined beside the type (`decision({…})`; probe 26, d-ca6wbw); `X | None` becomes `X | null`, never `undefined`; a tuple becomes `readonly T[]`, a `Mapping` a `ReadonlyMap`, a `frozenset` a `ReadonlySet`; a `StrEnum` becomes a `const` object and a union type of its values (`Action.CREATE === "create"`); a record, an area, a thread, and a problem each carry `kind` (`"decision"`, `"spec"`, `"area"`, `"thread"`, `"problem"`) where Python tells them apart with `isinstance`.
- Exceptions keep their Python names and base classes: `ts/src/core/errors.ts` (Task 4) holds `ValueError` and `LookupError`, each extending `Error`; `YamlError` and `SettingsError` extend `ValueError`, `AmbiguousRef` extends `LookupError`, and `FormatError` extends `Error`, as in Python (`grep -n '^class' src/lodge/core/*.py`); each sets `name` to its class name.
  `raise ValueError(m)` becomes `throw new ValueError(m)`, and `except E` becomes `catch (e) { if (!(e instanceof E)) throw e; … }`, never a bare `catch`.
- Names: functions and fields in camelCase, types in PascalCase, module constants as in Python (`MINUTE_FORMAT`); the record file format keeps its keys (`decided_by`, `rests_on`, `work_item`, `imported_from`), since the export must write it unchanged (design line 284).
- Text (probes 12, 14, 16, 17, and 18): a Python string operation whose JavaScript namesake differs goes through `ts/src/core/text.ts` (Task 4): `strip`, `rstrip`, `split()` without arguments, `splitlines`, `isspace`, `isdigit`, `casefold`, `repr` and `!r` (`pyRepr`), and `len` of a string (code points, never `.length`); `str.lower()` is `toLowerCase()`, which agrees with it at every code point and on the final sigma (probe 17); strings are sorted by code point, never with `<` on UTF-16 units.
  In regular expressions, every pattern has the `u` flag; Python's `\w` becomes `[\p{L}\p{N}_]` (`WORD_CLASS` of `text.ts`), `\d` becomes `\p{Nd}`, `\s` becomes `PY_SPACE_CLASS` of `text.ts` in a pattern built with `new RegExp` (d-87kzys), `\b` becomes the lookarounds `(?<![\p{L}\p{N}_])` and `(?![\p{L}\p{N}_])` on the matching side, and `re.fullmatch(p, s)` becomes a test of `^(?:p)$`.
  Under `re.MULTILINE`, `^` becomes `(?<=^|\n)` and `$` becomes `(?=\n|$)`, without the `m` flag, which would also break lines at `\r`, U+2028, and U+2029; outside it, Python's `$` becomes `(?=\n?$)`, since it also matches before a last `\n`; `.` without `re.DOTALL` becomes `[^\n]`, and with it the `s` flag.
  A set of control characters is checked code point by code point in `text.ts` or `yamlio.ts`, not with a regular expression, since Biome's recommended rule `noControlCharactersInRegex` refuses the escapes (`plan-review-correctness.md`, M-7).
- Times cross into `core` as ISO 8601 stamps with seconds and an offset (`2026-10-29T12:00:00+01:00`), never as `Date`; `ts/src/core/stamps.ts` (Task 4) parses and compares them with integer arithmetic alone, and `core` never uses `Date`, whose local fields follow the machine's time zone and whose `Date.UTC` reads the years 0 to 99 as 1900 to 1999 (`bun -e 'console.log(new Date(Date.UTC(1, 0, 1)).toISOString())'` prints `1901-01-01T00:00:00.000Z`); ties are broken by ID as in Python.
- Structure (Task 3, d-k5swcq, d-x6f9za, d-4psbdv): allowed imports by the table; another package only as `#name`, which resolves to its `index.ts`, and no relative import leaving its package; no cycles, within a package too; no file over 300 lines in `ts/src`, `ts/tests`, or `ts/scripts`; `core` imports only its own modules, `yaml`, and `@noble/hashes`; `core` and `app` use no clock, randomness, local time, process, network, console, or timer, and `core` no `Date`; dynamic code nowhere; the import and call rules bind `ts/src`, and tests and scripts may read and write files.
- A module nearing 300 lines is split by topic into two modules named in the task's report, each importing the other only one way; a test file likewise, its second file listed with the first in `parity.json`.
- knip runs over `ts/src`, `ts/tests`, and `ts/scripts` and fails on an export that no other file reads, except the exports of a front door (`index.ts`) and of every other file in `ts/knip.json`'s `entry`, which knip leaves alone; `#core`'s exports are checked against Python's `__all__` by Task 11's test instead (d-hshapm), and the third plan turns on knip's `includeEntryExports` (d-s2rdn2).
- Exports read in a later task (d-tha8st): a module or test helper is ported whole, exporting each name another Python file imports from it, and a name no other Python file imports is not exported (`drafted` of `applying.py`, `next_id` of `builders.py`, and `base_items` and `key` of `checks.py`).
  A file with an export whose first reader comes in a later task goes into `ts/knip.json`'s `entry` in the task that creates it, and the task in which the last of those names gets its reader takes it out, so that knip checks every export of the file from then on; both tasks list `ts/knip.json` under Modify (probe 21).
  The files, from the import lines of `src/lodge/core/*.py` and `tests/core/*.py` (`plan-recheck-1.md`, N1):

  | File | Into `entry` | Names and the task that first reads them | Out of `entry` |
  |---|---|---|---|
  | `src/core/yamlio.ts` | Task 4 | `LINE_BREAKS_AND_TABS`, `quoted`, `unreadableChar` (5a) | Task 5a |
  | `src/core/headers.ts` | Task 5a | `AREA_KEYS`, `DECISION_KEYS`, `SPEC_KEYS` (5b) | Task 5b |
  | `src/core/document.ts` | Task 5a | `splitDocument`, `problemFor`, `loadHeader` (5b); `keyLine` (6) | Task 6 |
  | `src/core/fields.ts` | Task 5a | `readStamp` (6) | Task 6 |
  | `tests/core/builders.ts` | Task 6 | `treeOf` (11) | Task 11 |
  | `src/core/derive.ts` | Task 7a | `orderKey` (7b) | Task 7b |
  | `src/core/check-state.ts` | Task 8a | `newDecisions`, `problemAt`, `sortKey` (8b) | Task 8b |
  | `tests/core/checks.ts` | Task 8a | `NOW`, `SETTINGS`, `LATER`, `NOTES`, `OLD`, `SPEC`, `Item`, `creates`, `published`, `state`, `oldDecision`, `REMEDY_CHECK_5`, `REMEDY_CHECK_5_REASONING` (8b); `check` and `verdict`, written in 8b; `REMEDY_CHECK_4` (8c) | Task 8c |

  The names of `errors.ts`, `text.ts`, and `stamps.ts` are exported through `#core` (d-hshapm), so none of these files waits.
- Tests never touch a real repository or the network; fixtures are the made-up project of lodge 0.2's tests (the `storage` area, transcripts), never her words or another project's records.
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.

### Task 4: Errors, text, YAML, identifiers, dates, settings, and the model

**Files:**
- Port: `src/lodge/core/model.py`, `ids.py`, `settings.py`, `yamlio.py`
- Create: `ts/src/core/errors.ts`, `ts/src/core/model.ts`, `ts/src/core/ids.ts`, `ts/src/core/settings.ts`, `ts/src/core/yamlio.ts`, `ts/src/core/text.ts`, `ts/src/core/stamps.ts`
- Modify: `ts/src/core/index.ts` (the placeholder goes), `ts/tests/parity.json`, `ts/knip.json` (`yaml` leaves `ignoreDependencies`, and `src/core/yamlio.ts` goes into `entry`, d-tha8st)
- Delete: `ts/tests/core/toolchain.test.ts`
- Test: `ts/tests/core/ids.test.ts`, `ts/tests/core/settings.test.ts`, `ts/tests/core/yamlio.test.ts` (carried), `ts/tests/core/text.test.ts` (new), `ts/tests/core/stamps.test.ts` (new)

**Interfaces:**
- Consumes: Task 3's rules.
- Produces, through `#core`: `ValueError`, `LookupError`; `Scope`, `Action`, `Quote`, `Change`, `NumberHandle`, `Imported`, `Decision`, `SpecEntry`, `Area`, `Record`, `Problem`, `Raises`, `ThreadState`, `Message`, `Thread`, and the default-filling functions `decision`, `specEntry`, `area`, `problem`, and `message`; `isId`, `mintId`; `CoreSettings`, `LengthGuidance`, `SettingsError`, `parseCoreSettings`, and the default-filling functions `coreSettings` and `lengthGuidance` of `settings.ts`, which `tests/core/test_settings.py:10` needs (d-ca6wbw); `YamlError`, `loadYaml`; and every name of `errors.ts`, `text.ts`, and `stamps.ts` below (d-hshapm):
  ```ts
  // errors.ts (Global Constraints, "Exceptions")
  export class ValueError extends Error {}
  export class LookupError extends Error {}
  // text.ts, Python's str semantics (probes 12, 14, 16, and 18)
  export function isPySpace(ch: string): boolean   // 0x9-0xd, 0x1c-0x1f, 0x20, 0x85, 0xa0, 0x1680, 0x2000-0x200a, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000
  export function strip(s: string): string         // str.strip()
  export function rstrip(s: string): string        // str.rstrip()
  export function splitWords(s: string): string[]  // str.split()
  export function splitLines(s: string): string[]  // str.splitlines()
  export function isDigit(s: string): boolean      // str.isdigit(): non-empty, each character \p{Nd} or one of the 20 ranges of probe 16, Python's 808 characters and the 90 of the isDigit item below (probe 23)
  export function casefold(s: string): string      // str.casefold(), as toUpperCase().toLowerCase() with "ς" then made "σ"
  export function pyRepr(s: string): string        // repr() of a str
  export function codePointLength(s: string): number
  export function byCodePoint(a: string, b: string): number
  export const WORD_CLASS: string                  // "[\\p{L}\\p{N}_]", Python's \w (probe 14)
  export const PY_SPACE_CLASS: string              // "[\\u{9}-\\u{d}…\\u{3000}]", the code points isPySpace takes, as \u{…} escapes (d-87kzys)
  // stamps.ts
  export function isStamp(text: string): boolean   // _STAMP of fields.py and what datetime.fromisoformat accepts
  export function isDay(text: string): boolean     // _DAY, a real date
  export function instant(stamp: string): number   // milliseconds since the epoch; throws a ValueError on a non-stamp
  export function compareStamps(a: string, b: string): number
  ```
- Module-internal, first read by Task 5a: `LINE_BREAKS_AND_TABS`, `quoted`, and `unreadableChar` of `yamlio.ts`, which is in knip's `entry` until then (d-tha8st); they are not exported through `#core`, as `__all__` does not hold them (d-hshapm).
- `isDigit` differs from Python's `isdigit` at 90 code points, which `/\p{Nd}/u` takes and Python 3.13's `isdecimal` refuses, all unassigned in Unicode 15.1 (category `Cn`) and digits in Bun's newer Unicode, the first U+10D40 (probe 23), so the report lists them as a known difference.
- `casefold` differs from Python's at 174 code points, none of them giving a letter of `author`, and maps the final `ς` that `toLowerCase()` makes back to `σ`, as Python's `casefold("ΑΣ")` gives `ασ` (probe 16); its two uses compare codes, which are ASCII (`src/lodge/core/fields.py:11`), and look for `author` in `decided_by` (`src/lodge/core/check_state.py:101` and `:124`), so the report lists the 174 as a known difference.
- `pyRepr` chooses `"` when the text holds `'` and no `"`, and `'` otherwise; escapes `\`, the chosen quote, `\t`, `\n`, and `\r`; and writes every character `str.isprintable()` refuses (general categories `Cc`, `Cf`, `Cs`, `Co`, `Cn`, `Zl`, `Zp`, and `Zs` other than the space) as `\xNN` below U+0100, `\uNNNN` below U+10000, and `\UNNNNNNNN` above; it differs from Python's `repr` only at 9,988 characters that Unicode 15.1 leaves unassigned and Bun's newer Unicode assigns (probe 18), listed in the report.
- `isStamp` accepts what `read_stamp` accepts (`src/lodge/core/fields.py:13` and `:155-163`): the pattern, a real date and time with a year of 0001 or later, and an offset whose hours × 60 + minutes is below 1,440, so `+00:60` and `+22:99` are stamps and `+23:60` and `-23:99` are not (probe 19).
  `isStamp`, `isDay`, `instant`, and `compareStamps` compute with integer arithmetic alone (days from the civil date), never with `Date` (Global Constraints, "Times").
- `mintId(prefix, entropy: Uint8Array)` takes the bytes from the caller, as Python takes `entropy: bytes`.
- `loadYaml` (d-bkc7md, probe 7): `parseAllDocuments` of the `yaml` package with the `failsafe` schema and unique keys, then a walk over the parsed nodes, never `toJS()`, giving a mapping as a `Map` in the text's key order, a sequence as an array, and a scalar as a string; nothing reaches `console`.
  It throws a `YamlError` with its line, never an exception of the `yaml` package, for: any error of the package; a tag other than `!`, `!!str`, `!!seq`, and `!!map`, or `!!str`, `!!seq`, or `!!map` on another kind of node (message holding "tag"); a mapping key that is not a scalar (message `found unhashable key`, as PyYAML's); more than one document; a character PyYAML's reader refuses, which is any outside `\x09`, `\x0A`, `\x0D`, `\x20`-`\x7E`, `\x85`, `\xA0`-`\uD7FF`, `\uE000`-`\uFFFD`, and the astral planes, checked code point by code point (message `unreadable character ` and the character as `pyRepr` gives it, `src/lodge/core/yamlio.py:64`); a duplicate key (message naming the key as `pyRepr` gives it, `'title'`).
  Nesting deeper than 100 levels throws a `YamlError` with Python's message `the header is nested too deeply` and no line (`src/lodge/core/yamlio.py:61-62`), and the report lists the bound as a known narrowing of lodge 0.2 (d-bkc7md).
- `quoted` writes `JSON.stringify(text)`, which escapes as Python's `json.dumps(…, ensure_ascii=False)` does for every character `unreadableChar` lets through; where Python's `quoted` raises `ValueError`, it throws the `ValueError` of `errors.ts`.
- The carried settings tests build their input with `tomllib.loads`; in TypeScript that is `Bun.TOML.parse`, which tests may use (d-x6f9za), and no carried case holds a float, where the two differ (`grep -n toml tests/core/test_settings.py`; `plan-review-correctness.md`, M-9).

- [ ] **Step 1: Write the failing tests.**
  - The carried files, every test of `tests/core/test_ids.py`, `test_settings.py`, and `test_yamlio.py` by name.
  - `text.test.ts`: `is_py_space_matches_python` (each code point of the list above true, and U+FEFF, U+200B, and `a` false); `strip_removes_python_whitespace_only` (`"\x1c a \x85"` to `"a"`, `"\uFEFFa"` unchanged); `rstrip_like_python` (`"a \x85"` to `"a"`, `"a\uFEFF"` unchanged, `"## Reasoning\x1c"` to `"## Reasoning"`); `split_words_like_python` (`" a\x1fb  c "` to `["a", "b", "c"]`); `split_lines_like_python` (`"a\r\nb\x0bc\x1cd\u2028e\n"` to five lines, no empty last one); `is_digit_like_python` (`"12"`, `"²"`, and `"①"` true; `""`, `"1a"`, and `"½"` false); `casefold_like_python` (`"Straße"` to `"strasse"`, `"ſ"` to `"s"`, `"ﬆ"` to `"st"`, and `"ΑΣ"` to `"ασ"`); `py_repr_matches_python` (`a` to `'a'`, `it's` to `"it's"`, a text with both quotes, `a\b`, `\x01` to `'\x01'`, `\x85`, U+200B to `'\u200b'` (a backslash, then `u200b`: Python's `repr`, since U+200B is of category `Cf`), a lone `\ud83d`, a tab and a newline, and `😀` kept); `code_point_length_counts_astral_once` (`"a😀"` is 2); `word_class_matches_python_w` (`a`, `é`, `٣`, and `_` match `WORD_CLASS` with the `u` flag, `-` and a space do not); `py_space_class_matches_is_py_space` (for every code point, `new RegExp(PY_SPACE_CLASS, "u")` matches exactly when `isPySpace` is true); `by_code_point_orders_astral_after_bmp` (`"\uFFFF"` before `"😀"`).
  - `stamps.test.ts`: `stamp_with_offset_is_a_stamp`; `stamp_without_offset_or_seconds_is_not` (`2026-10-29T12:00+01:00`, `2026-10-29T12:00:00`, `2026-10-29T12:00:00Z`); `impossible_date_is_not_a_stamp` (`2026-02-30T10:00:00+01:00`, `2026-10-29T24:00:00+01:00`, `0000-01-01T00:00:00+01:00`); `offset_is_read_as_python_reads_it` (`+00:60` and `+22:99` stamps, `+23:60`, `+24:00`, and `-23:99` not); `instant_respects_the_offset` (`2026-10-29T12:00:00+01:00` equals `2026-10-29T11:00:00+00:00`, and `0001-01-01T00:00:00+00:00` is `-62135596800000`); `compare_orders_by_instant`; `day_must_be_real`; `stamp_check_ignores_the_local_time_zone` (with `process.env.TZ` set to `Europe/Berlin`, `2026-03-29T02:30:00+01:00` is a stamp and its instant is that of `2026-03-29T01:30:00+00:00`).
  - In `yamlio.test.ts`, besides the carried tests: `collection_key_is_refused` (`[title]: x`, `{a: b}: c`, and `? [a, b]\n: c`, each `found unhashable key` at line 1); `integer_like_keys_keep_their_order` (`zz: a\n1: b\n` gives the keys `zz`, then `1`); `non_specific_tag_is_text` (`a: ! b\n` gives `a` to `b`); `str_tag_on_a_mapping_is_refused`; `nesting_beyond_the_bound_has_no_line` (101 nested brackets: the message, and no line).
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement** the interfaces above; delete the placeholder and its test; take `yaml` out of `ts/knip.json`'s `ignoreDependencies`, and add `src/core/yamlio.ts` to its `entry`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green, and knip reports no unused dependency and no unused export; then flip `test_ids.py`, `test_settings.py`, and `test_yamlio.py` to `ported` and run it again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
