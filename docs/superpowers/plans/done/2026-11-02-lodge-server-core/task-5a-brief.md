# Brief: Task 5a of `docs/superpowers/plans/2026-11-02-lodge-server-core.md`

You build Task 5a of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
You have no network: never run `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-5a-report.md`: what you changed per file, each test you added or carried with its first failing output (or the mutation it failed against), the commands you ran and their last lines, every test that cannot hold in TypeScript with the reason, and anything you were unsure of.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## From the coordinator

- Tasks 1 to 4 are done: Task 4's modules are in `ts/src/core/` (`errors.ts`, `text.ts`, `stamps.ts`, `yamlio.ts`, `ids.ts`, `settings.ts`, `model.ts`) and its report is `docs/superpowers/plans/2026-11-02-lodge-server-core/task-4-report.md`; Task 4 is still under review, so a later fix round may touch its files.
- Task 3's structure rules now also refuse `Date(…)` without `new` in `core` and `app`, every file-writing call outside `git` (d-mfskz3), and `fetch` outside `api`, `cli`, and `hook` (d-s5s2c3).
- The probes the brief names are items of `docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md`, their sources in `probes/` beside it.

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

### Task 5a: Record files

**Files:**
- Port: `src/lodge/core/fields.py`, `document.py`, `headers.py`, `fileformat.py`
- Create: `ts/src/core/fields.ts`, `ts/src/core/document.ts`, `ts/src/core/headers.ts`, `ts/src/core/fileformat.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`, `ts/knip.json` (`@noble/hashes` leaves `ignoreDependencies`; `src/core/yamlio.ts` leaves `entry`, and `src/core/headers.ts`, `src/core/document.ts`, and `src/core/fields.ts` go into it, d-tha8st)
- Test: `ts/tests/core/samples.ts`, `ts/tests/core/fileformat.test.ts`, `ts/tests/core/fileformat-problems.test.ts` (carried)

**Interfaces:**
- Consumes: Task 4.
- Produces, through `#core`: `areaPath`, `contentHash`, `newRecordPath`, `parseArea`, `parseRecord`, `slug`, `writeArea`, `writeRecord`; module-internal: `FormatError` (extending `Error`, as Python's extends `Exception`) and the readers of `fields.py`, which read the `Map`s `loadYaml` gives, so an unknown key is named in the text's order.
- Module-internal and first read in a later task (Global Constraints, "Exports read in a later task"): `AREA_KEYS`, `DECISION_KEYS`, and `SPEC_KEYS` of `headers.ts` and `splitDocument`, `problemFor`, and `loadHeader` of `document.ts` (Task 5b), and `keyLine` of `document.ts` and `readStamp` of `fields.ts` (Task 6); the three files are in knip's `entry` until then.
- `contentHash`: the first 12 hex characters of `@noble/hashes`' SHA-256 of the text's UTF-8 bytes, its line ends normalised first as Python's `normalise_newlines` does (probe 8); a lone surrogate, which Python encodes with `surrogateescape`, is listed in the report as a difference.
- Dates go through `stamps.ts`: `read_date` and `read_stamp` accept exactly what they accept in Python (`src/lodge/core/fields.py:121-163`), with the same messages.
- `document.py`'s `rstrip` (lines 44, 52, and 59) is `rstrip` of `text.ts`, so a line `## Reasoning` followed by U+FEFF does not start the reasoning, as in Python; every `!r` in a message is `pyRepr`.
- `writeRecord` and `writeArea` throw the `ValueError` of `errors.ts`, as Python's raise `ValueError`, when a text would not read back unchanged.

- [ ] **Step 1: Write the failing tests:** every test of `test_fileformat.py` and `test_fileformat_problems.py`, by name, with `samples.ts` from `samples.py`.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; take `@noble/hashes` out of `ts/knip.json`'s `ignoreDependencies` and `src/core/yamlio.ts` out of its `entry`, and add `src/core/headers.ts`, `src/core/document.ts`, and `src/core/fields.ts` to its `entry`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green, knip reports no unused dependency and no unused export, and `ts/knip.json`'s `entry` no longer names `src/core/yamlio.ts`; flip `samples.py` and the two test files to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
