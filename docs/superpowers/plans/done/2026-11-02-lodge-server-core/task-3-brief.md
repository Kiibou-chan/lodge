# Brief: Task 3 of `docs/superpowers/plans/2026-11-02-lodge-server-core.md`

You build Task 3 of the plan named above, in this repository, on its current branch.
Read `CLAUDE.md` first, then this brief; this brief is your requirements, with the exact values to use verbatim.
Read other parts of the plan only where this brief points to them by name.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Do not commit and do not push: the coordinator stages, runs `sh scripts/check.sh` outside the sandbox, commits, and pushes.
You have no network: never run `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
Your gate is `sh scripts/check-ts.sh`; run it last, and it must exit 0.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-core/task-3-report.md`: what you changed per file, each test you added or carried with its first failing output (or the mutation it failed against), the commands you ran and their last lines, every test that cannot hold in TypeScript with the reason, and anything you were unsure of.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## From the coordinator

- "The parity table above" is the section `## Parity table` of the plan file; read that section whole, since `parity.json` has one entry per row of it.
- Tasks 1 and 2 are done: the toolchain is in `ts/` (`ts/package.json`, `ts/biome.json` with `"preset": "recommended"`, `ts/knip.json`, `ts/.dependency-cruiser.cjs`, `ts/src/core/index.ts`, `ts/tests/core/toolchain.test.ts`) and `sh scripts/check-ts.sh` is green; `ts/node_modules` is installed.

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

### Task 3: The structure rules and the parity table

**Files:**
- Modify: `ts/.dependency-cruiser.cjs`, `ts/package.json` (no new dependency)
- Create: `ts/tests/structure/table.ts`, `ts/tests/structure/plant.ts`, `ts/tests/structure/calls.ts`, `ts/tests/structure/imports.test.ts`, `ts/tests/structure/calls.test.ts`, `ts/tests/structure/layout.test.ts`, `ts/tests/structure/repository.test.ts`, `ts/tests/parity.json`, `ts/tests/parity-names.ts`, `ts/tests/parity.test.ts`

**Interfaces:**
- Consumes: Task 2's toolchain; `tests/structure_*.py` and `tests/test_structure*.py` as the rules to carry; the parity table above.
- Produces:
  ```ts
  // table.ts
  export const PACKAGES: ReadonlyMap<string, readonly string[]>  // package -> packages it may import
  export const CORE_NPM: readonly string[]                       // ["yaml", "@noble/hashes"]
  export const MAX_LINES = 300
  // plant.ts
  export function plant(files: Record<string, string>): string   // a temporary folder holding the tree described below
  export function cruise(root: string): Promise<string[]>        // dependency-cruiser's violations, as "rule: from -> to"
  // calls.ts
  export function callViolations(root: string): string[]         // "src/<pkg>/<file>:<line>: <message>"
  export function sizeViolations(root: string): string[]
  export function layoutViolations(root: string): string[]
  // parity-names.ts
  export function pythonTestNames(text: string): string[]        // names of `def test_…` and `async def test_…`, without test_
  export function typescriptTestTitles(text: string): string[]   // titles of test(…), it(…), test.each(…)(…), and test.todo(…)
  export function todoTitles(text: string): string[]
  ```
- `plant` makes a folder with `mkdtempSync` under the system's temporary folder and writes into it `package.json` (with the `#name` imports of the planted packages and a copy of `ts/package.json`'s `dependencies`, d-bxcave), a `tsconfig.json` with `ts/tsconfig.json`'s compiler options, a symbolic link `node_modules` to `ts/node_modules`, so that `yaml`, `@noble/hashes`, and every planted npm import resolve (`plan-review-practice.md`, P-I1), and the files at their paths under `src/`, `tests/`, or `scripts/`.
- `cruise` runs dependency-cruiser's `cruise` in process with the planted root as its base folder (`baseDir`), since the rules' paths are relative to it, and with `preserveSymlinks: true`, so that `yaml` resolves to `node_modules/yaml/dist/index.js` with dependency type `npm`, as it does in `ts/`, rather than through the link to a path outside the tree with type `npm-no-pkg` (probe 24, d-bxcave).
- `PACKAGES` (d-k5swcq): `core` none; `app` `core`; `store`, `git`, `api`, `cli`, and `hook` each `app` and `core`; `main` (the file `src/main.ts`) all.
- dependency-cruiser rules, each an error with this name; `front-door`, `no-circular`, and `not-to-unresolvable` bind `src`, `tests`, and `scripts`, and every other rule has `from: { path: "^src/" }`, so tests and scripts may read and write files (d-x6f9za).
  dependency-cruiser reports `node:fs` as the module `fs` of type `core` (`plan-review-correctness.md`, M-5), so each built-in name below matches with and without `node:`, as in `^(node:)?fs(/promises)?$`:
  - `allowed-imports`: a module of package P importing a module of package Q not in `PACKAGES[P]`;
  - `front-door`: an import of another package's module other than its `index.ts`, or one not written as `#name` (dependency type `aliased-subpath-import`);
  - `no-circular`: any cycle, within a package too;
  - `core-imports`: `core` importing an npm package outside `CORE_NPM`, or any built-in (dependency type `core`, so `node:` and `bun:` modules);
  - `app-imports`: `app` importing any built-in or npm package;
  - `process-confinement`: `child_process` imported outside `git`;
  - `sqlite-confinement`: `bun:sqlite` imported outside `store`;
  - `file-confinement`: `fs` or `fs/promises` imported outside `git` and `cli` (d-x6f9za: `git` has `gitstore`'s file access, `cli` reads the drafts it is given, and `store` has none);
  - `network-confinement`: `net`, `http`, `https`, `tls`, or `dgram` imported outside `api`;
  - `not-to-unresolvable`.
- `callViolations` walks every `.ts` file under `src` with TypeScript's parser (`ts.createSourceFile`, typescript 6.0.3) and reports:
  - in `core` and `app`: `Date.now`, `new Date()` and `Date()` with no argument or with more than one, `Intl`, `performance`, `Math.random`, `crypto`, `process`, `Bun`, `fetch`, `console`, `setTimeout`, `setInterval`, `queueMicrotask`, `navigator`, and `globalThis`, as `<pkg> may not use <name>`; a call of a property named `getTimezoneOffset`, `toLocaleString`, `toLocaleDateString`, `toLocaleTimeString`, `toDateString`, or `toTimeString`, or of a `get` or `set` of `FullYear`, `Month`, `Date`, `Day`, `Hours`, `Minutes`, `Seconds`, or `Milliseconds` without `UTC`, as `<pkg> may not use local time: <name>`;
  - in `core` also any use of `Date` (`core may not use Date`), and any call of a property named `now`, `today`, or `utcnow` on any receiver (`core may not use x.now`), while `app` may call `clock.now()` on its port;
  - everywhere: `eval`, `Function` and `new Function`, a dynamic `import(…)`, and `require(…)`, as `dynamic code` or `dynamic import`;
  - `Bun.spawn`, `Bun.spawnSync`, and `Bun.$` outside `git`, as `process spawning outside git`; `Bun.file` outside `git` and `cli`, as `file reading outside git and cli`; `Bun.write`, and a call of a function or property named `writeFile`, `appendFile`, `mkdir`, `rm`, `rmdir`, `unlink`, `rename`, `copyFile`, `cp`, `symlink`, or `truncate`, or of one of these with `Sync` after it, outside `git`, as `file writing outside git`; `Bun.serve`, `Bun.listen`, and `Bun.connect` outside `api`, as `sockets outside api` (d-x6f9za; `tests/structure_calls.py:109-140`).
- `sizeViolations`: each `.ts` file under `src`, `tests`, and `scripts` over `MAX_LINES` lines, as `<path>: <n> lines (limit 300)`.
- `layoutViolations`: a folder under `src` that is not a package of `PACKAGES` (`unknown package <name>`); a package without `index.ts` (`missing front door`); a folder inside a package (`nested folder`); an entry of `package.json`'s `imports` that is not `#<pkg>` to `./src/<pkg>/index.ts` for an existing package, or an existing package without one (`imports does not match the packages`).
- `parity.json`: one entry per row of the parity table, keyed by the Python path: `{"status": "planned" | "ported" | "changed" | "later", "plan": 1 to 4 (absent for "later" and for "changed" without a plan), "task": ["3", "5a", …] (plan 1 only), "ts": [paths under ts/], "why": "<design line …>" (for "changed" and "later")}`.
  A plan 1 row the table marks "changed" (the seven structure rows) is `changed` from the start, with its plan, its task, its files named one by one, and its `why`; every other plan 1 row starts `planned`, and each task flips its rows to `ported` in its last step; rows of plans 2 to 4 are `planned` (with a `why` where the table gives one), `changed`, or `later` as the table says.
- The structure rows are `changed` because the rules are carried as rules, not test by test: of the 38 test names of `tests/test_structure.py` and `tests/test_structure_io.py`, those that test Python's own forms (`import_inside_function`, `source_that_is_not_utf8_names_the_file`, and the like) have no TypeScript counterpart.

- [ ] **Step 1: Write the failing tests.**
  - `imports.test.ts`, each planting a tree with `plant` and asserting the one violation named (the Python test it carries in brackets): `core_importing_app` (`test_core_importing_app`); `adapter_importing_adapter` (`cli` importing `#store`); `import_past_front_door` (`#core` is fine, `../core/check.ts` from `app` is `front-door`); `relative_import_leaving_its_package`; `test_importing_past_front_door` (a file under `tests/` importing `../src/core/x.ts`); `cycle_between_modules`; `cycle_within_a_package`; `core_importing_node_builtin` (`node:fs`, and `fs` without the prefix); `core_importing_bun_builtin` (`bun:sqlite`); `core_importing_other_npm_package`; `core_may_import_yaml_and_noble_hashes`; `app_importing_builtin`; `child_process_outside_git`; `sqlite_outside_store`; `fs_outside_git_and_cli` (in `store` and in `api`); `http_outside_api`; `main_may_import_every_package`; `unresolvable_import`; `confined_io_is_allowed_where_ruled` (`test_confined_io_is_allowed_where_ruled`: one tree with `node:fs` and `node:child_process` in `git`, `fs` in `cli`, `bun:sqlite` in `store`, `node:http` in `api`, `yaml` and `@noble/hashes/sha2.js` in `core`, and `src/main.ts` importing every package, with no violation); `tests_and_scripts_may_use_files` (`node:fs` in a planted `tests/core/a.test.ts` and `scripts/a.ts`: no violation).
  - `calls.test.ts`, each with `callViolations` on a planted tree: `core_disallowed_global` (each of the names above, in `core` and in `app`, `test.each`); `local_time_in_core_and_app` (each local-time name and `new Date(2026, 2, 29)`, in `core` and in `app`, `test.each`); `core_may_not_use_date` (`new Date("2026-10-29T12:00:00+01:00")` and `Date.UTC(2026, 9, 29)` in `core`); `core_names_the_clock_on_any_receiver` (`d.now()`, `d.today()`, `d.utcnow()` in `core`); `clock_port_call_is_not_a_clock_read` (`clock.now()` in `app`: no violation); `app_may_parse_a_stamp` (`new Date("2026-10-29T12:00:00+01:00")` and `getUTCHours()` in `app`: no violation); `dynamic_code_anywhere` (`eval`, `new Function`, `import(x)`, `require(x)` in `cli`); `spawn_outside_git`; `file_reading_outside_git_and_cli` (`Bun.file` in `store`); `file_writing_outside_git` (`Bun.write` and `writeFileSync` in `cli`); `sockets_outside_api`; `confined_calls_are_allowed_where_ruled` (`Bun.spawn`, `Bun.write`, and `writeFileSync` in `git`, `Bun.file` in `cli`, and `Bun.serve` in `api`: no violation).
  - `layout.test.ts`: `unknown_package`; `missing_front_door`; `nested_folder`; `imports_must_match_packages`; `oversized_module` (301 lines in `src/core`); `oversized_test` (301 lines in `tests/core`); `module_at_the_limit_passes` (300 lines).
  - `repository.test.ts`: `repository_has_no_violations` (`cruise`, `callViolations`, `sizeViolations`, and `layoutViolations` on `ts/` itself are all empty).
  - `parity.test.ts`: `every_python_test_file_is_in_the_table` (the keys equal the files under `../tests`, skipping `__pycache__` folders, 126 now); `statuses_are_known`; `changed_and_later_give_a_why`; `planned_rows_name_a_plan`; `ported_files_exist` (every file of a `ported` row, and of a `changed` row of plan 1); `ported_files_keep_every_python_test_name` (for `ported` rows: each name from `pythonTestNames` is a title from `typescriptTestTitles` of one of the row's files, or begins one followed by a space); `ported_files_hold_no_todo` (for `ported` rows); `a_ported_file_losing_a_name_fails` (the check on a made-up row whose TypeScript text lacks one Python name reports that name); and `parity_names_read_both_languages` (the two readers on a short Python and a short TypeScript text, `test.each` and a multi-line call included).
- [ ] **Step 2: Run** `cd ts && bun test tests/structure tests/parity.test.ts`; expected: the new tests FAIL.
- [ ] **Step 3: Implement** the interfaces above; cruise once per test file where one planted tree can hold several cases, to keep the gate fast.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.
