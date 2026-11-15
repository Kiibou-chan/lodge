# Brief: Task 8c of `docs/superpowers/plans/2026-11-02-lodge-server-core.md`

You build Task 8c of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
You have no network: never run `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-8c-report.md`: what you changed per file, each test you added or carried with its first failing output (or the mutation it failed against), the commands you ran and their last lines, every test that cannot hold in TypeScript with the reason, and anything you were unsure of.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## From the coordinator

- Tasks 1 to 8b, 9a, and 11 are built and merged: the checks (`check-*.ts`, with `ts/tests/core/checks.ts`), confirmations and the order (`confirmation.ts`, `order.ts`), levels (`views.ts`), and applying drafts (`apply.ts`, `apply-areas.ts`, `value-repr.ts`) are in `ts/src/core/`, and `ts/src/core/index.ts` lists what `#core` exports; Tasks 7a to 9a and 11 are still under review, so a later fix round may touch their files.
- `fields.ts` exports a field reader named `require`; the structure rule treats any call named `require` as dynamic code, so import it as `import { require as requireField } from "./fields.ts"` and call `requireField`.
- The gate runs `biome check --error-on-warnings`, so a Biome warning fails it (ruling d-f18pz7); fix warnings in code, never by turning a rule off.
- Stamps: `orderInstant` of `stamps.ts` orders a stamp or a bare day (ruling d-g1hrmn).
- A carried test over an earlier task's code is shown failing against a targeted mutation of the behaviour it names, not a throw at the top of a whole function, which only shows the test calls it (`task-5b-review.md`, C-1).
- The probes the brief names are items of `docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md`, their sources in `probes/` beside it.
- You work in a lane (author decision d-xdqsmf): Task 9b and a fix round of Task 7a run at the same time in other worktrees, and the coordinator merges the lanes. Touch only your task's files, plus `ts/src/core/index.ts`, `ts/tests/parity.json`, and `ts/knip.json` where the brief says, changing only your own lines there.
- Task 9a already created `ts/tests/core/check-threads.test.ts` with its view test only (`task-9a-report.md`, lines 136 onward, names the fifteen Python tests still missing); add the missing tests to that file (or split it by topic if it passes 300 lines, both files listed in `parity.json`), and flip the row to `ported` when every name is there.
- Task 11 left five apply tests without their `checkChange` assertions (`task-11-report.md`, lines 141 to 156); `checkChange` is now in, so restore those five assertions as the Python tests have them, each seen failing against a targeted mutation.

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

### Task 8c: The other check tests

**Files:**
- Modify: `ts/tests/parity.json`, `ts/knip.json` (`tests/core/checks.ts` leaves `entry`, d-tha8st); Task 8a's and 8b's modules only where a carried test finds them wrong
- Test: `ts/tests/core/check-compare.test.ts`, `ts/tests/core/check-links.test.ts`, `ts/tests/core/check-threads.test.ts` (carried)

**Interfaces:**
- Consumes: Task 8b.
- Produces: no new name; the carried tests of check 4's comparisons, the links, and the threads.
- These tests carry over code Tasks 8a and 8b ported, so each is seen failing against a mutation of that code the report names, and the mutation is reverted (d-mfayy5).

- [ ] **Step 1: Write the tests:** every test of `test_check_compare.py`, `test_check_links.py`, and `test_check_threads.py` by name; `thread_problems_are_visible_in_reads` of `check-threads.test.ts` is a `test.todo` until Task 9a.
- [ ] **Step 2: Run** each test against its named mutation and see it fail; revert each mutation.
- [ ] **Step 3: Fix** in Tasks 8a's and 8b's modules what a carried test finds, each fix named in the report with a test that failed before it.
- [ ] **Step 4: Take** `tests/core/checks.ts` out of `ts/knip.json`'s `entry`, now that `check-compare.test.ts` reads `REMEDY_CHECK_4`; **run** `sh scripts/check-ts.sh`; green, knip reports no unused export, and `ts/knip.json`'s `entry` no longer names `tests/core/checks.ts`; flip `test_check_compare.py` and `test_check_links.py` to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
