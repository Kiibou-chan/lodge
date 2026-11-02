# lodge server, build step 1, plan 1: the toolchain and the core in TypeScript

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** lodge 0.2's pure core runs in TypeScript, proved by its carried tests and by a differential run against lodge 0.2 on this repository's records, under a gate that enforces the structure rules over the TypeScript import graph.

**Architecture:** a `ts/` folder beside the Python holds the TypeScript code (d-h1f596).
This plan builds its toolchain and gate, the structure rules for the packages of the whole of build step 1 (d-k5swcq), and one package, `core`, ported module by module from `src/lodge/core` at parity (d-88p8h9).
The core keeps lodge 0.2's view of a state as files, path and text (`Tree`), which is also what a record's event will hold on the server (d-smx3xf).
The later plans of build step 1 build on it: the events store and the operations, the API and the command, then the importer and the export (d-26dx04).

**Tech stack:** Bun 1.3.14 (runtime, `bun test`, and the gate, d-xph4ac); TypeScript 6.0.3 strict; Biome 2.5.15; dependency-cruiser 18.6.0; knip 6.42.0; `@types/bun` 1.4.3; in `core` only `yaml` 2.9.1 and `@noble/hashes` 2.4.0 (d-4psbdv, d-k5swcq).

**Spec:** `lodge spec` and lodge 0.2's tests for what the core does; `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (the design, approved by the author 2026-11-02 13:52) for where it lives and what changes, recorded in lodge by Task 1.
The plan argues from them, never over them; where they disagree with this plan, they win and the builder reports it.
"Design line N" is a line of the design; "probe N" is an item of `docs/superpowers/plans/2026-11-02-lodge-server-core/probes.md`, whose sources are in `probes/` beside it.

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
- Types: a frozen dataclass becomes an `interface` with `readonly` fields and, where Python fills defaults, a function of the same name in camelCase that fills them (`decision({…})`); `X | None` becomes `X | null`, never `undefined`; a tuple becomes `readonly T[]`, a `Mapping` a `ReadonlyMap`, a `frozenset` a `ReadonlySet`; a `StrEnum` becomes a `const` object and a union type of its values (`Action.CREATE === "create"`); a record, an area, a thread, and a problem each carry `kind` (`"decision"`, `"spec"`, `"area"`, `"thread"`, `"problem"`) where Python tells them apart with `isinstance`.
- Exceptions keep their Python names and base classes: `ts/src/core/errors.ts` (Task 4) holds `ValueError` and `LookupError`, each extending `Error`; `YamlError` and `SettingsError` extend `ValueError`, `AmbiguousRef` extends `LookupError`, and `FormatError` extends `Error`, as in Python (`grep -n '^class' src/lodge/core/*.py`); each sets `name` to its class name.
  `raise ValueError(m)` becomes `throw new ValueError(m)`, and `except E` becomes `catch (e) { if (!(e instanceof E)) throw e; … }`, never a bare `catch`.
- Names: functions and fields in camelCase, types in PascalCase, module constants as in Python (`MINUTE_FORMAT`); the record file format keeps its keys (`decided_by`, `rests_on`, `work_item`, `imported_from`), since the export must write it unchanged (design line 284).
- Text (probes 12, 14, 16, 17, and 18): a Python string operation whose JavaScript namesake differs goes through `ts/src/core/text.ts` (Task 4): `strip`, `rstrip`, `split()` without arguments, `splitlines`, `isspace`, `isdigit`, `casefold`, `repr` and `!r` (`pyRepr`), and `len` of a string (code points, never `.length`); `str.lower()` is `toLowerCase()`, which agrees with it at every code point and on the final sigma (probe 17); strings are sorted by code point, never with `<` on UTF-16 units.
  In regular expressions, every pattern has the `u` flag; Python's `\w` becomes `[\p{L}\p{N}_]`, `\d` becomes `\p{Nd}`, `\s` becomes Python's whitespace set from `text.ts`, `\b` becomes the lookarounds `(?<![\p{L}\p{N}_])` and `(?![\p{L}\p{N}_])` on the matching side, and `re.fullmatch(p, s)` becomes a test of `^(?:p)$`.
  Under `re.MULTILINE`, `^` becomes `(?<=^|\n)` and `$` becomes `(?=\n|$)`, without the `m` flag, which would also break lines at `\r`, U+2028, and U+2029; outside it, Python's `$` becomes `(?=\n?$)`, since it also matches before a last `\n`; `.` without `re.DOTALL` becomes `[^\n]`, and with it the `s` flag.
  A set of control characters is checked code point by code point in `text.ts` or `yamlio.ts`, not with a regular expression, since Biome's recommended rule `noControlCharactersInRegex` refuses the escapes (`plan-review-correctness.md`, M-7).
- Times cross into `core` as ISO 8601 stamps with seconds and an offset (`2026-10-29T12:00:00+01:00`), never as `Date`; `ts/src/core/stamps.ts` (Task 4) parses and compares them with integer arithmetic alone, and `core` never uses `Date`, whose local fields follow the machine's time zone and whose `Date.UTC` reads the years 0 to 99 as 1900 to 1999 (`bun -e 'console.log(new Date(Date.UTC(1, 0, 1)).toISOString())'` prints `1901-01-01T00:00:00.000Z`); ties are broken by ID as in Python.
- Structure (Task 3, d-k5swcq, d-x6f9za, d-4psbdv): allowed imports by the table; another package only as `#name`, which resolves to its `index.ts`, and no relative import leaving its package; no cycles, within a package too; no file over 300 lines in `ts/src`, `ts/tests`, or `ts/scripts`; `core` imports only its own modules, `yaml`, and `@noble/hashes`; `core` and `app` use no clock, randomness, local time, process, network, console, or timer, and `core` no `Date`; dynamic code nowhere; the import and call rules bind `ts/src`, and tests and scripts may read and write files.
- A module nearing 300 lines is split by topic into two modules named in the task's report, each importing the other only one way; a test file likewise, its second file listed with the first in `parity.json`.
- knip runs over `ts/src`, `ts/tests`, and `ts/scripts`: every export of a module is read by another module or by a test in the task that adds it, except the exports of a front door (`index.ts`), which knip takes as an entry; `#core`'s exports are checked against Python's `__all__` by Task 11's test instead, and the third plan turns on knip's `includeEntryExports` (d-s2rdn2).
- Tests never touch a real repository or the network; fixtures are the made-up project of lodge 0.2's tests (the `storage` area, transcripts), never her words or another project's records.
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.

## Calls made

Each is the planner's ruling, recorded in lodge with scope `process` and this plan as its work item; its reasoning there holds a handle per argument and the cost if wrong.
Every task repeats what it needs of them, so no brief needs this section.

1. d-26dx04: build step 1 is four plans, this one the toolchain and the core; the other three are below, under "The rest of build step 1".
2. d-h1f596: the TypeScript code lives in `ts/` with its own `package.json`, `bun.lock`, configuration, `ts/src/<package>/`, and `ts/tests/<package>/`.
3. d-xph4ac: Bun runs the server, the tests, the gate's tools (`bun --bun run check`), and the binaries; Node is used nowhere (probes 1, 3, 4, and 20); it replaces d-03xx0a.
4. d-4psbdv: the TypeScript gate is Biome, `tsc --noEmit` with TypeScript 6.0.3 strict, dependency-cruiser, knip, and `bun test` with a structure test; every dependency pinned to an exact version at least two weeks old (probes 5, 10, and 11); knip's check of the front doors is narrowed by d-s2rdn2 (item 16).
5. d-k5swcq: the packages are `core` (imports nothing), `app` (`core`), the adapters `store`, `git`, `api`, `cli`, and `hook` (each `app` and `core`), and `main` (all); `#name` aliases are the front doors; `core` may import `yaml` and `@noble/hashes` (probes 6 and 8); where the rules bind and what each adapter may do is d-x6f9za (item 17).
6. d-88p8h9: port at parity first, carried tests keeping their Python names, then make the design's changes as tasks of their own with new tests.
7. d-smx3xf: a record's event on the server holds its path and file text as lodge 0.2 writes it, so the core keeps checking states given as files.
8. d-g7ynw0: the parity table is `ts/tests/parity.json`, checked by a test (Task 3).
9. d-j3z85y: Task 1 records her eight answers behind the design as author decisions before the build; the entries they make false wait for the fourth plan's records task.
10. d-xk6qtn: `scripts/check.sh` runs both gates and stops with "bun is not installed" rather than skip one.
11. d-2jk0mw: no project moves to the server during build step 1.
12. d-0qmd10: the core port ends with a differential run against lodge 0.2 on this repository's records, comparing what the two cores derive and what their writers give (Task 12); it replaces d-g3mbmc.
13. d-sry12f, d-yayhct, and d-4k9wcr settle the API's first shape, passkeys, and the query builder for the later plans, and d-jtxwg3 the page the person uses them on; see "Settled for the later plans".
14. d-bkc7md: the TypeScript YAML layer walks the `yaml` package's nodes into `Map`s in the text's key order and refuses what PyYAML refuses and the package lets through (probe 7): more than one document, a tag other than `!`, `!!str`, `!!seq`, and `!!map` or one on another kind of node, a key that is not a scalar, and a character PyYAML's reader refuses, each a `YamlError` with its line; nesting beyond 100 levels gets Python's message and no line; it replaces d-458jhp.
15. d-7tdgs5: Biome formats with an indent of two spaces and a line width of 100, Ruff's width for lodge 0.2.
16. d-s2rdn2: knip checks every export behind the front doors; a test checks `#core`'s exports against `__all__` of `src/lodge/core/__init__.py`, and the third plan turns on `includeEntryExports`.
17. d-x6f9za: the allowed-import, `core`, `app`, and confinement rules and the call checks bind `ts/src` only; each adapter keeps the permissions of the lodge 0.2 package it replaces (`git` those of `gitstore`, `cli` those of `cli`, `api` the viewer's place as the HTTP adapter, `hook` those of `hook`), and `store` may import `bun:sqlite` and has no file access.
18. d-mfayy5: Tasks 5, 7, 8, and 9 are split into 5a and 5b, 7a and 7b, 8a, 8b, and 8c, and 9a and 9b, the numbers kept so the reviews' handles hold.
19. d-jtxwg3: the third plan's `api` serves a minimal page for registering a passkey, signing in, agent tokens, and approving drafted decisions, until step 3's interface replaces it.

## Review Focus

1. A carried test that asserts less than its Python original: a case dropped from a parametrised list, a list-valued case handed to `test.each` unwrapped (probe 15), `toContain` where Python compares whole values, a `toThrow` without the class or the pattern Python matched, or a title that matches the Python name while the body tests something else.
2. Text at the edges (probes 12, 14, 16, and 18): a title or statement holding U+001C, U+0085, U+FEFF, an astral character, a lone surrogate, CRLF line ends, or U+2028 or a lone CR before a line that looks like a heading; length guidance counted in code points; sorting by code point; a message quoting a value as Python's `repr` does.
3. YAML (probe 7, d-bkc7md): every refusal PyYAML makes is a `YamlError` with its line (nesting excepted), nothing PyYAML reads as text is read as a number, a boolean, a null, or a date, and keys keep the text's order.
4. Stamps: an offset other than the local one, `+00:60` accepted and `+23:60` refused (probe 19), two decisions in the same second ordered by ID, `2026-02-30T10:00:00+01:00` refused, a bare day accepted only for an imported record, and no answer changing with `TZ`.
5. Purity: no clock, randomness, local time, or environment reaching `core` through a default parameter, a module-level constant, or a global the structure test does not name.
6. The gate: each structure rule has a refusal and an allowed case, and `parity.test.ts` fails when a ported file loses one Python name.
7. Writers: `writeRecord`, `writeArea`, and `writeThread` give lodge 0.2's text byte for byte, which Task 12 checks on this repository's records.

## The rest of build step 1

Each of the three later plans gets its own brief, planner, and review; each opens with a setup task the coordinator runs outside the sandbox, which adds that plan's dependencies to `ts/package.json` and commits `ts/bun.lock`.

**Plan 2, the events store and the operations.**
The `store` package keeps every write as an event in one append-only SQLite table through Kysely over `bun:sqlite` (d-4k9wcr, probe 1), a record's event holding its path and file text (d-smx3xf), with the current state and the tables for queries rebuilt from the events; `app` is ported from `src/lodge/app` at parity over a storage port whose current and published states are the same state (design line 79), with the app tests carried and `test_reads_published.py` and `test_writes_retry.py` changed as the parity table says; then, as tasks of their own with new tests (d-88p8h9), the design's model changes: `decided_by` names a person or an agent role, a person's decision drafted by a session waits for that person's approval and is not current until then (SRV-2, design line 75), a review flag on a person's decision clears only when that person confirms (design line 77), and the check runs on every write and refuses with `lodge add`'s feedback (design line 79).
It ends when the carried app tests and the new model tests pass in process, with no HTTP.

**Plan 3, the API, sign-in, and the command.**
The `api` package serves the operations as `POST /api/v1/<operation>` with JSON (d-sry12f) through a `fetch` handler that the tests call without a socket (probe 1), behind bearer tokens for agents and, for the one person, passkeys and a session cookie (d-yayhct, probe 2); the `cli` package is the `lodge` command at parity with lodge 0.2, talking to the server, with the command tests carried (each run against an in-process server), and it ships as one binary through `bun build --compile` (design line 55, probe 3); any test that needs a socket is named for the coordinator to run.
Its last task serves one minimal page from `api`, plain HTML with a small script and no framework, where the person registers a passkey with the setup code, signs in, issues and revokes agent tokens, and approves the decisions drafted in their name, so that one person can work with the server before step 3's interface replaces the page (d-jtxwg3, design line 304).
The command reads `.lodge.toml`, and the plan settles how it refuses `title_chars = 80.0` as lodge 0.2 does (`src/lodge/core/settings.py:55`), since `Bun.TOML.parse` gives the whole number 5 for `5.0` (`plan-review-correctness.md`, M-9).
It ends when the carried command tests pass against the server, the compiled binary runs them, and the coordinator has registered, signed in, issued a token, and approved a drafted decision through the page in a real browser.

**Plan 4, the importer, the export, and the design's records.**
The importer reads a lodge 0.2 store from a git repository and writes its records as events, keeping IDs, dates, codes, and `imported_from`, and mapping `decided_by: author` to the project's first owner (design lines 78 and 289); the export writes the records as a lodge 0.2 store into the project's repository or a separate one, one way, at most one commit a minute (design lines 282 to 285); the hook's advice changes for a project that has moved (design line 290), with the hook tests carried; the coordinator imports a scratch copy of lodge's own records and checks that the export reads like the original (d-2jk0mw); then the design goes into lodge as entries, editing or narrowing what the built server makes false (s-a4jfp1, s-07ar34, s-z1zvb4, s-j8tp0n, s-v1sb0j, s-165qfh, s-3xka4c; d-j3z85y), and the design document is frozen.
It ends when a made-up 0.2 store survives import and export unchanged apart from the people in `decided_by`.

## Settled for the later plans

These rulings are made now so that the later plans start from them; their tasks are written in those plans.

- **The API's first shape (d-sry12f).**
  `POST /api/v1/<operation>`, a JSON body and a JSON answer, one operation per operation of lodge 0.2's `Lodge` (`src/lodge/app/lodge.py`): `search`, `show`, `waiting`, `timeline`, `spec`, `problems`, `check`, `draft`, `mint`, `add` (with `dry_run`, the drafts as path and text, and attachments as name and text), `ask`, `reply`, `close`, `threads`, `thread`, `confirm`, and `behind-area`; plus the person's `approve` (a drafted person's decision, SRV-2), and for setup, `project-create`, `token-issue`, and `token-revoke`; plan 4 adds `import` and `export-target`.
  An agent sends `Authorization: Bearer <token>`; the person sends the session cookie.
  An error answers `{"error": {"kind": K, "message": M}}` with `K` one of `usage` (400), `unauthorised` (401), `forbidden` (403), `not-found` (404), `conflict` (409), and `check-failed` (422, with the check's problems and the feedback); the command maps `check-failed` and `conflict` to exit 1 and the rest to exit 2, as lodge 0.2 does (`lodge guide`, last line).
  Enough for the command (every 0.2 command but `view` and `hook`), the importer (`import`), and the tests (the handler called with a `Request`).
- **Passkeys for one person (d-yayhct, d-jtxwg3).**
  `lodge-server setup` prints a one-time setup code; the person's first registration presents it, and it is spent on use and expires after 15 minutes.
  Registration and sign-in run through @simplewebauthn/server 14.0.3 with the server's public name as the relying party, fixed in its settings before the first registration; a sign-in sets an `HttpOnly`, `Secure`, `SameSite=Strict` session cookie, and the passkey's signature counter is checked as @simplewebauthn/server checks it, a synced passkey reporting 0 throughout.
  The tests play the browser with the software authenticator of `probes/tests/passkey.test.ts` (an ES256 key from WebCrypto, attestation `none`, the signature in DER), so no test needs a browser (probe 2); as committed it fails strict `tsc` with two `TS2345` errors at lines 11 and 37 (probe 20), so when carried its buffers are built as `new Uint8Array(new ArrayBuffer(n))`.
  A token for agents is issued by the signed-in person, stored hashed, and revocable.
  The person does all of this on the minimal page of the third plan's last task (d-jtxwg3), since a passkey is created only through `navigator.credentials` in a page on the relying party's origin.
- **The query builder (d-4k9wcr).** Kysely 0.29.7 over `bun:sqlite`, through the adapter of `probes/src/server/db.ts`.

## Parity table

Each of lodge 0.2's 126 test files (`git ls-files tests | wc -l`), with its plan, its TypeScript counterpart under `ts/`, and, where the design changes it, the design line.
"Changed" with no plan means the file has no counterpart, since what it tests does not exist on the server; "later" means outside build step 1.
Task 3 writes this table as `ts/tests/parity.json` (d-g7ynw0).

| Python file | Plan and task | TypeScript counterpart | Why changed or later |
|---|---|---|---|
| `tests/app/conftest.py` | Plan 2 | `ts/tests/app/support.ts` |  |
| `tests/app/fakes.py` | Plan 2 | `ts/tests/app/fakes.ts` |  |
| `tests/app/support.py` | Plan 2 | `ts/tests/app/support.ts` |  |
| `tests/app/test_confirm.py` | Plan 2 | `ts/tests/app/confirm.test.ts` |  |
| `tests/app/test_reads.py` | Plan 2 | `ts/tests/app/reads.test.ts` |  |
| `tests/app/test_reads_published.py` | Plan 2, changed | `ts/tests/app/reads-published.test.ts` | design line 79: the check runs on every write, and the published state becomes the server's current state |
| `tests/app/test_thread_fix_paths.py` | Plan 2 | `ts/tests/app/thread-fix-paths.test.ts` |  |
| `tests/app/test_thread_ops.py` | Plan 2 | `ts/tests/app/thread-ops.test.ts` |  |
| `tests/app/test_writes.py` | Plan 2 | `ts/tests/app/writes.test.ts` |  |
| `tests/app/test_writes_attach.py` | Plan 2 | `ts/tests/app/writes-attach.test.ts` |  |
| `tests/app/test_writes_dates.py` | Plan 2 | `ts/tests/app/writes-dates.test.ts` |  |
| `tests/app/test_writes_retry.py` | Plan 2, changed | `ts/tests/app/writes-retry.test.ts` | design line 72: records live in the server's events, not in files in git; a write that loses a race is retried against the store, not a push |
| `tests/core/applying.py` | Plan 1, Task 11 | `ts/tests/core/applying.ts` |  |
| `tests/core/builders.py` | Plan 1, Task 6 | `ts/tests/core/builders.ts` |  |
| `tests/core/checks.py` | Plan 1, Tasks 8a and 8b  | `ts/tests/core/checks.ts` |  |
| `tests/core/derivation.py` | Plan 1, Task 7a  | `ts/tests/core/derivation.ts` |  |
| `tests/core/samples.py` | Plan 1, Task 5a  | `ts/tests/core/samples.ts` |  |
| `tests/core/test_apply.py` | Plan 1, Task 11 | `ts/tests/core/apply.test.ts` |  |
| `tests/core/test_apply_refusals.py` | Plan 1, Task 11 | `ts/tests/core/apply-refusals.test.ts` |  |
| `tests/core/test_area_feedback.py` | Plan 1, Task 10 | `ts/tests/core/area-feedback.test.ts` |  |
| `tests/core/test_check_change.py` | Plan 1, Task 8b  | `ts/tests/core/check-change.test.ts` |  |
| `tests/core/test_check_compare.py` | Plan 1, Task 8c  | `ts/tests/core/check-compare.test.ts` |  |
| `tests/core/test_check_current.py` | Plan 1, Task 8b  | `ts/tests/core/check-current.test.ts` |  |
| `tests/core/test_check_immutable.py` | Plan 1, Task 8b  | `ts/tests/core/check-immutable.test.ts` |  |
| `tests/core/test_check_links.py` | Plan 1, Task 8c  | `ts/tests/core/check-links.test.ts` |  |
| `tests/core/test_check_retired.py` | Plan 1, Task 8b  | `ts/tests/core/check-retired.test.ts` |  |
| `tests/core/test_check_state.py` | Plan 1, Task 8a  | `ts/tests/core/check-state.test.ts` |  |
| `tests/core/test_check_threads.py` | Plan 1, Tasks 8c and 9a  | `ts/tests/core/check-threads.test.ts` |  |
| `tests/core/test_confirmation.py` | Plan 1, Task 7b  | `ts/tests/core/confirmation.test.ts` |  |
| `tests/core/test_derive.py` | Plan 1, Task 7a  | `ts/tests/core/derive.test.ts` |  |
| `tests/core/test_derive_confirmed_retired.py` | Plan 1, Task 7a  | `ts/tests/core/derive-confirmed-retired.test.ts` |  |
| `tests/core/test_derive_links.py` | Plan 1, Task 7a  | `ts/tests/core/derive-links.test.ts` |  |
| `tests/core/test_doubts.py` | Plan 1, Tasks 7a and 9a  | `ts/tests/core/doubts.test.ts` |  |
| `tests/core/test_drafts.py` | Plan 1, Task 5b  | `ts/tests/core/drafts.test.ts` |  |
| `tests/core/test_feedback.py` | Plan 1, Task 10 | `ts/tests/core/feedback.test.ts` |  |
| `tests/core/test_feedback_links.py` | Plan 1, Task 10 | `ts/tests/core/feedback-links.test.ts` |  |
| `tests/core/test_feedback_revival.py` | Plan 1, Task 10 | `ts/tests/core/feedback-revival.test.ts` |  |
| `tests/core/test_fileformat.py` | Plan 1, Task 5a  | `ts/tests/core/fileformat.test.ts` |  |
| `tests/core/test_fileformat_links.py` | Plan 1, Task 6 | `ts/tests/core/fileformat-links.test.ts` |  |
| `tests/core/test_fileformat_problems.py` | Plan 1, Task 5a  | `ts/tests/core/fileformat-problems.test.ts` |  |
| `tests/core/test_fileformat_text.py` | Plan 1, Task 5b  | `ts/tests/core/fileformat-text.test.ts` |  |
| `tests/core/test_ids.py` | Plan 1, Task 4 | `ts/tests/core/ids.test.ts` |  |
| `tests/core/test_order.py` | Plan 1, Task 7b  | `ts/tests/core/order.test.ts` |  |
| `tests/core/test_render.py` | Plan 1, Task 9b  | `ts/tests/core/render.test.ts` |  |
| `tests/core/test_search.py` | Plan 1, Task 9b  | `ts/tests/core/search.test.ts` |  |
| `tests/core/test_settings.py` | Plan 1, Task 4 | `ts/tests/core/settings.test.ts` |  |
| `tests/core/test_snapshot.py` | Plan 1, Tasks 6 and 9a  | `ts/tests/core/snapshot.test.ts` |  |
| `tests/core/test_thread_files.py` | Plan 1, Tasks 6 and 10 | `ts/tests/core/thread-files.test.ts` |  |
| `tests/core/test_views.py` | Plan 1, Task 9a  | `ts/tests/core/views.test.ts` |  |
| `tests/core/test_views_links.py` | Plan 1, Task 9a  | `ts/tests/core/views-links.test.ts` |  |
| `tests/core/test_views_trust.py` | Plan 1, Task 9a  | `ts/tests/core/views-trust.test.ts` |  |
| `tests/core/test_yamlio.py` | Plan 1, Task 4 | `ts/tests/core/yamlio.test.ts` |  |
| `tests/e2e/__init__.py` | changed |  | a package marker; TypeScript tests need none |
| `tests/e2e/conftest.py` | Plan 3 | `ts/tests/e2e/project.ts` |  |
| `tests/e2e/support.py` | Plan 3 | `ts/tests/e2e/support.ts` |  |
| `tests/e2e/test_add_attach.py` | Plan 3 | `ts/tests/e2e/add-attach.test.ts` |  |
| `tests/e2e/test_add_bad_yaml_exits_2_naming_file_and_line.py` | Plan 3 | `ts/tests/e2e/add-bad-yaml-exits-2-naming-file-and-line.test.ts` |  |
| `tests/e2e/test_add_branch_mode_publishes.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/e2e/test_add_dry_run.py` | Plan 3 | `ts/tests/e2e/add-dry-run.test.ts` |  |
| `tests/e2e/test_add_failing_check_exits_1.py` | Plan 3 | `ts/tests/e2e/add-failing-check-exits-1.test.ts` |  |
| `tests/e2e/test_add_import.py` | Plan 3 | `ts/tests/e2e/add-import.test.ts` |  |
| `tests/e2e/test_add_new_decision_entry_area.py` | Plan 3 | `ts/tests/e2e/add-new-decision-entry-area.test.ts` |  |
| `tests/e2e/test_add_non_string_scalar_exits_2.py` | Plan 3 | `ts/tests/e2e/add-non-string-scalar-exits-2.test.ts` |  |
| `tests/e2e/test_before_init_one_sentence_exit_2.py` | Plan 3 | `ts/tests/e2e/before-init-one-sentence-exit-2.test.ts` |  |
| `tests/e2e/test_broken_agent_decision_warns_above_show.py` | Plan 3 | `ts/tests/e2e/broken-agent-decision-warns-above-show.test.ts` |  |
| `tests/e2e/test_check_and_gate.py` | Plan 3, changed | `ts/tests/e2e/check-and-gate.test.ts` | design line 79: the check runs on every write, and the published state becomes the server's current state |
| `tests/e2e/test_draft_then_add_edit.py` | Plan 3 | `ts/tests/e2e/draft-then-add-edit.test.ts` |  |
| `tests/e2e/test_gate_after_rewrite.py` | changed |  | design line 72: records live in the server's events, not in files in git; no branch to rewrite |
| `tests/e2e/test_gate_checkout_states.py` | changed |  | design line 79: the check runs on every write, and the published state becomes the server's current state |
| `tests/e2e/test_guide.py` | Plan 3 | `ts/tests/e2e/guide.test.ts` |  |
| `tests/e2e/test_help_lists_every_command.py` | Plan 3 | `ts/tests/e2e/help-lists-every-command.test.ts` |  |
| `tests/e2e/test_hook_feedback_after_hand_edits.py` | Plan 4, changed | `ts/tests/hook/hand-edits.test.ts` | design line 290: the hook's advice changes for a project that has moved |
| `tests/e2e/test_hook_outside_repository_exit_0_silent.py` | Plan 4 | `ts/tests/hook/outside-repository.test.ts` | design line 290: the hook's advice changes for a project that has moved |
| `tests/e2e/test_id.py` | Plan 3 | `ts/tests/e2e/id.test.ts` |  |
| `tests/e2e/test_init.py` | Plan 3, changed | `ts/tests/e2e/init.test.ts` | design line 72: records live in the server's events, not in files in git; `init` names the server and the project |
| `tests/e2e/test_init_branch_mode.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/e2e/test_killed_add.py` | changed |  | design line 72: records live in the server's events, not in files in git; `add` runs no git |
| `tests/e2e/test_malformed_settings_one_sentence_exit_2.py` | Plan 3 | `ts/tests/e2e/malformed-settings-one-sentence-exit-2.test.ts` |  |
| `tests/e2e/test_outside_repository_one_sentence_exit_2.py` | Plan 3 | `ts/tests/e2e/outside-repository-one-sentence-exit-2.test.ts` |  |
| `tests/e2e/test_same_second.py` | Plan 3 | `ts/tests/e2e/same-second.test.ts` |  |
| `tests/e2e/test_search.py` | Plan 3 | `ts/tests/e2e/search.test.ts` |  |
| `tests/e2e/test_search_limit.py` | Plan 3 | `ts/tests/e2e/search-limit.test.ts` |  |
| `tests/e2e/test_search_shows_unparsable_file.py` | Plan 3 | `ts/tests/e2e/search-shows-unparsable-file.test.ts` |  |
| `tests/e2e/test_show_ambiguous_code_one_line.py` | Plan 3 | `ts/tests/e2e/show-ambiguous-code-one-line.test.ts` |  |
| `tests/e2e/test_show_levels.py` | Plan 3 | `ts/tests/e2e/show-levels.test.ts` |  |
| `tests/e2e/test_spec.py` | Plan 3 | `ts/tests/e2e/spec.test.ts` |  |
| `tests/e2e/test_threads.py` | Plan 3 | `ts/tests/e2e/threads.test.ts` |  |
| `tests/e2e/test_view.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/e2e/test_waiting.py` | Plan 3 | `ts/tests/e2e/waiting.test.ts` |  |
| `tests/gitstore/__init__.py` | changed |  | a package marker; TypeScript tests need none |
| `tests/gitstore/conftest.py` | Plan 4 | `ts/tests/git/isolated.ts` | isolated git for the importer's and the export's tests |
| `tests/gitstore/fakessh.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/gitstore/repos.py` | Plan 4 | `ts/tests/git/repos.ts` | repositories in a temporary folder for the importer and the export |
| `tests/gitstore/test_branch.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/gitstore/test_branch_rewrite.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/gitstore/test_checkout.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/gitstore/test_checkout_gate.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/gitstore/test_checkout_safety.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/gitstore/test_commit.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/gitstore/test_concurrent.py` | Plan 2, changed | `ts/tests/store/concurrent.test.ts` | design line 72: records live in the server's events, not in files in git; two writers at once against the events store |
| `tests/gitstore/test_exit_request.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/gitstore/test_push_race.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/gitstore/test_setup.py` | changed |  | design line 72: records live in the server's events, not in files in git |
| `tests/hook/__init__.py` | changed |  | a package marker; TypeScript tests need none |
| `tests/hook/test_post_tool_use.py` | Plan 4, changed | `ts/tests/hook/post-tool-use.test.ts` | design line 290: the hook's advice changes for a project that has moved |
| `tests/structure_calls.py` | Plan 1, Task 3, changed | `ts/tests/structure/calls.ts` | design line 58: the rules carry over as rules, enforced over the TypeScript import graph, not test by test |
| `tests/structure_imports.py` | Plan 1, Task 3, changed | `ts/.dependency-cruiser.cjs` | design line 58: the rules carry over as rules, enforced over the TypeScript import graph, not test by test |
| `tests/structure_rules.py` | Plan 1, Task 3, changed | `ts/tests/structure/calls.ts`, `ts/tests/structure/plant.ts` | design line 58: the rules carry over as rules, enforced over the TypeScript import graph, not test by test |
| `tests/structure_tables.py` | Plan 1, Task 3, changed | `ts/tests/structure/table.ts` | design line 58: the rules carry over as rules, enforced over the TypeScript import graph, not test by test |
| `tests/structure_tree.py` | Plan 1, Task 3, changed | `ts/tests/structure/plant.ts` | design line 58: the rules carry over as rules, enforced over the TypeScript import graph, not test by test |
| `tests/test_entry_point.py` | Plan 3 | `ts/tests/e2e/binary.test.ts` | design line 55: the command ships as a binary built with `bun build --compile` |
| `tests/test_structure.py` | Plan 1, Task 3, changed | `ts/tests/structure/imports.test.ts`, `ts/tests/structure/layout.test.ts`, `ts/tests/structure/repository.test.ts` | design line 58: the rules carry over as rules, enforced over the TypeScript import graph, not test by test |
| `tests/test_structure_io.py` | Plan 1, Task 3, changed | `ts/tests/structure/imports.test.ts`, `ts/tests/structure/calls.test.ts` | design line 58: the rules carry over as rules, enforced over the TypeScript import graph, not test by test |
| `tests/test_wheel.py` | Plan 3, changed | `ts/tests/e2e/binary.test.ts` | design line 55: the command ships as a binary built with `bun build --compile`, not a wheel |
| `tests/viewer/__init__.py` | changed |  | a package marker; TypeScript tests need none |
| `tests/viewer/conftest.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/test_forms.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/test_pages.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/test_pages_fix_round.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/test_pages_threads.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/test_post_gate.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/test_post_routes.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/test_request_gate.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/test_server.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/test_spec_outline.py` | later: step 3, the interface (design lines 275 and 298) |  |  |
| `tests/viewer/world.py` | later: step 3, the interface (design lines 275 and 298) |  |  |

---

### Task 1: The author's answers behind the server design into lodge

The coordinator does this task itself, outside the sandbox, before any code (d-j3z85y), since author records are immutable and their place and minute come from its session.

**Files:** eight decision records via `lodge add`; drafts under `.drafts/`.

**Interfaces:**
- Consumes: the design (line 3, line 75, and line 196) and `docs/superpowers/specs/2026-11-02-lodge-server-architecture-options.md` (lines 4, 43, 51, 59, and 64).
- Produces: eight author decisions; later tasks and plans cite them by code.

Each decision: `decided_by: author`, `scope: product`, the code below where there is one, `quote: {text: <her words, verbatim>, where: <the name of the session she answered in>, when: "2026-11-02 HH:MM"}`, the session's name asked of the author before Step 1 by a coordinator that did not hold that conversation (`plan-review-practice.md`, P-M7), reasoning equal to the quote text and nothing else, and a statement saying only what her answer settles, read with the question it answered.
They replace and narrow nothing, and each "looks related" question is answered no; the entries and decisions the built server makes false are edited or narrowed in plan 4 (d-j3z85y).

| Code | When | Her words | Statement | Source |
|---|---|---|---|---|
| ARCH-1 | 00:18 | A | lodge becomes one server that holds the records, serves the interface and the API, and runs the workflows, with a small runner on each machine that may do work. | options line 4 |
| ARCH-2 | 00:34 | Okay then TS sounds fine. I might prefer kotlin personally, but the code reuse point is quite a strong one I think. | The server, the runner, the interface, and the `lodge` command are written in TypeScript. | options line 43 |
| ARCH-3 | 00:38 | A then | lodge keeps its records in one SQLite file, as events in an append-only table behind a storage port. | options line 51 |
| none | 00:38 | That sounds reasonable. It should support a separate repo. | The server writes its records out to git one way, into the project's repository or a separate one. | options line 59 |
| ARCH-4 | 10:44 | C | The interface is an app in the browser, written with Preact and `@preact/signals`, installable on a phone. | options line 64 |
| SRV-1 | 13:34 | C | A session lodge starts is talked to inside lodge, in the thread of its task or artefact. | design line 196 |
| SRV-2 | 13:38 | B | A person's decision is written only through that person: a session drafts it with the person's quote, and it becomes current when that person approves it. | design line 75 |
| none | 13:52 | Approved | The server design of 2 November 2026 is approved. | design line 3 |

- [ ] **Step 1:** Draft the eight decisions; `uv run --frozen --quiet lodge add --dry-run` each; act on any check line; answer each "looks related" question no; give each digit the dry run names a `numbers` handle (the design's path).
- [ ] **Step 2:** `uv run --frozen --quiet lodge add` the eight drafts.
- [ ] **Step 3: Verify** `uv run --frozen --quiet lodge search --by author --limit 60` lists the eight, dated at the add, after the newest decision (`src/lodge/app/writes.py:142-149`); `uv run --frozen --quiet lodge show <id> --provenance` gives each quote's minute; `uv run --frozen --quiet lodge show ARCH-2 --provenance` prints her words; `uv run --frozen --quiet lodge check` prints `ok`.
- [ ] **Step 4:** `git add lodge/`, `sh scripts/check.sh`, commit, push; the ledger line lists the eight IDs.

### Task 2: The TypeScript toolchain and the gate

The coordinator does this task outside the sandbox, since it installs packages (brief; d-xph4ac, d-4psbdv).

**Files:**
- Create: `ts/package.json`, `ts/bun.lock` (by `bun install`), `ts/tsconfig.json`, `ts/biome.json`, `ts/knip.json`, `ts/.dependency-cruiser.cjs`, `ts/src/core/index.ts`, `ts/tests/core/toolchain.test.ts`, `scripts/check-ts.sh`
- Modify: `scripts/check.sh` (one line at the end), `.gitignore` (one line, `ts/node_modules/`)

**Interfaces:**
- Produces: the TypeScript gate, and `#core` resolving to `ts/src/core/index.ts`.
- `ts/package.json`, before Biome formats it (Step 1):
  ```json
  {
    "name": "lodge",
    "private": true,
    "type": "module",
    "packageManager": "bun@1.3.14",
    "imports": { "#core": "./src/core/index.ts" },
    "scripts": {
      "check": "biome check . && tsc --noEmit -p . && depcruise src tests --config .dependency-cruiser.cjs && knip && bun test"
    },
    "dependencies": { "@noble/hashes": "2.4.0", "yaml": "2.9.1" },
    "devDependencies": {
      "@biomejs/biome": "2.5.15",
      "@types/bun": "1.4.3",
      "dependency-cruiser": "18.6.0",
      "knip": "6.42.0",
      "typescript": "6.0.3"
    }
  }
  ```
- `ts/tsconfig.json`, `compilerOptions`: `target` and `lib` `ES2024`, `module` `Preserve`, `moduleResolution` `bundler`, `types` `["bun"]`, `noEmit`, `allowImportingTsExtensions`, `verbatimModuleSyntax`, `isolatedModules`, `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, `noImplicitReturns`, `noFallthroughCasesInSwitch`, `noPropertyAccessFromIndexSignature`, `noUnusedLocals`, `noUnusedParameters`, `forceConsistentCasingInFileNames`, all true; `include` `["src", "tests", "scripts"]`.
- `ts/biome.json`: the recommended lint rules, the formatter with spaces, an indent of 2, and a line width of 100 (d-7tdgs5), over `src`, `tests`, `scripts`, and the JSON files; `node_modules` ignored.
- `ts/knip.json`: `entry` `["tests/**/*.test.ts", "scripts/*.ts"]`, `project` `["src/**/*.ts", "tests/**/*.ts", "scripts/**/*.ts"]`, and `ignoreDependencies` `["yaml", "@noble/hashes"]`, since no code imports them before Tasks 4 and 5a, which each take its name out (`plan-review-correctness.md`, I-4); when knip reports a dev dependency the gate uses as unused, the coordinator adds it to `ignoreDependencies` too, and the ledger line names every entry.
- `ts/.dependency-cruiser.cjs`: for now only `no-circular` and `not-to-unresolvable` as errors, with `tsConfig` `tsconfig.json`; Task 3 writes the table.
- `ts/src/core/index.ts`: `export const CORE_PACKAGE = "core";`, and `ts/tests/core/toolchain.test.ts` imports it from `#core` and asserts it, in a test titled `bun_runs_typescript_tests`; Task 4 removes both.
- `scripts/check-ts.sh`:
  ```sh
  set -eu
  cd "$(dirname "$0")/../ts"
  command -v bun >/dev/null 2>&1 || { echo "bun is not installed" >&2; exit 2; }
  [ -d node_modules ] || { echo "ts/node_modules is missing; run bun install --frozen-lockfile in ts/" >&2; exit 2; }
  bun --bun run check
  ```
- `scripts/check.sh` gains `sh scripts/check-ts.sh` as its last line (d-xk6qtn).

- [ ] **Step 1:** Write the files above; in `ts/`, `bun install`, then `bun install --frozen-lockfile` to confirm the lockfile, then `bun x biome format --write .`, since Biome lays out `package.json`'s short objects over several lines (`plan-review-correctness.md`, M-8).
- [ ] **Step 2: Verify** `sh scripts/check-ts.sh` exits 0; `PATH=/usr/bin:/bin sh scripts/check-ts.sh` (no Bun on the path) prints "bun is not installed" and exits 2; `sh scripts/check.sh` exits 0; `grep -c '"[~^]' ts/package.json` prints 0.
- [ ] **Step 3:** Commit the files above and push; the ledger line names the `ignoreDependencies` entries.

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
- `plant` makes a folder with `mkdtempSync` under the system's temporary folder and writes into it `package.json` (with the `#name` imports of the planted packages), a `tsconfig.json` with `ts/tsconfig.json`'s compiler options, a symbolic link `node_modules` to `ts/node_modules`, so that `yaml`, `@noble/hashes`, and every planted npm import resolve (`plan-review-practice.md`, P-I1), and the files at their paths under `src/`, `tests/`, or `scripts/`.
- `cruise` runs dependency-cruiser's `cruise` in process with the planted root as its base folder (`baseDir`), since the rules' paths are relative to it.
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

### Task 4: Errors, text, YAML, identifiers, dates, settings, and the model

**Files:**
- Port: `src/lodge/core/model.py`, `ids.py`, `settings.py`, `yamlio.py`
- Create: `ts/src/core/errors.ts`, `ts/src/core/model.ts`, `ts/src/core/ids.ts`, `ts/src/core/settings.ts`, `ts/src/core/yamlio.ts`, `ts/src/core/text.ts`, `ts/src/core/stamps.ts`
- Modify: `ts/src/core/index.ts` (the placeholder goes), `ts/tests/parity.json`, `ts/knip.json` (`yaml` leaves `ignoreDependencies`)
- Delete: `ts/tests/core/toolchain.test.ts`
- Test: `ts/tests/core/ids.test.ts`, `ts/tests/core/settings.test.ts`, `ts/tests/core/yamlio.test.ts` (carried), `ts/tests/core/text.test.ts` (new), `ts/tests/core/stamps.test.ts` (new)

**Interfaces:**
- Consumes: Task 3's rules.
- Produces, through `#core`: `ValueError`, `LookupError`; `Scope`, `Action`, `Quote`, `Change`, `NumberHandle`, `Imported`, `Decision`, `SpecEntry`, `Area`, `Record`, `Problem`, `Raises`, `ThreadState`, `Message`, `Thread` (and their default-filling functions); `isId`, `mintId`; `CoreSettings`, `LengthGuidance`, `SettingsError`, `parseCoreSettings`; `YamlError`, `loadYaml`, `quoted`, `unreadableChar`; and:
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
  export function isDigit(s: string): boolean      // str.isdigit(): non-empty, each character \p{Nd} or one of the 20 ranges of probe 16
  export function casefold(s: string): string      // str.casefold(), as toUpperCase().toLowerCase() with "ς" then made "σ"
  export function pyRepr(s: string): string        // repr() of a str
  export function codePointLength(s: string): number
  export function byCodePoint(a: string, b: string): number
  export const WORD_CLASS: string                  // "[\\p{L}\\p{N}_]", Python's \w (probe 14)
  // stamps.ts
  export function isStamp(text: string): boolean   // _STAMP of fields.py and what datetime.fromisoformat accepts
  export function isDay(text: string): boolean     // _DAY, a real date
  export function instant(stamp: string): number   // milliseconds since the epoch; throws a ValueError on a non-stamp
  export function compareStamps(a: string, b: string): number
  ```
- `casefold` differs from Python's at 174 code points, none of them giving a letter of `author`, and maps the final `ς` that `toLowerCase()` makes back to `σ`, as Python's `casefold("ΑΣ")` gives `ασ` (probe 16); its two uses compare codes, which are ASCII (`src/lodge/core/fields.py:11`), and look for `author` in `decided_by` (`src/lodge/core/check_state.py:101` and `:124`), so the report lists the 174 as a known difference.
- `pyRepr` chooses `"` when the text holds `'` and no `"`, and `'` otherwise; escapes `\`, the chosen quote, `\t`, `\n`, and `\r`; and writes every character `str.isprintable()` refuses (general categories `Cc`, `Cf`, `Cs`, `Co`, `Cn`, `Zl`, `Zp`, and `Zs` other than the space) as `\xNN` below U+0100, `\uNNNN` below U+10000, and `\UNNNNNNNN` above; it differs from Python's `repr` only at 9,988 characters that Unicode 15.1 leaves unassigned and Bun's newer Unicode assigns (probe 18), listed in the report.
- `isStamp` accepts what `read_stamp` accepts (`src/lodge/core/fields.py:13` and `:155-163`): the pattern, a real date and time with a year of 0001 or later, and an offset whose hours × 60 + minutes is below 1,440, so `+00:60` and `+22:99` are stamps and `+23:60` and `-23:99` are not (probe 19).
  `isStamp`, `isDay`, `instant`, and `compareStamps` compute with integer arithmetic alone (days from the civil date), never with `Date` (Global Constraints, "Times").
- `mintId(prefix, entropy: Uint8Array)` takes the bytes from the caller, as Python takes `entropy: bytes`.
- `loadYaml` (d-bkc7md, probe 7): `parseAllDocuments` of the `yaml` package with the `failsafe` schema and unique keys, then a walk over the parsed nodes, never `toJS()`, giving a mapping as a `Map` in the text's key order, a sequence as an array, and a scalar as a string; nothing reaches `console`.
  It throws a `YamlError` with its line, never an exception of the `yaml` package, for: any error of the package; a tag other than `!`, `!!str`, `!!seq`, and `!!map`, or `!!str`, `!!seq`, or `!!map` on another kind of node (message holding "tag"); a mapping key that is not a scalar (message `found unhashable key`, as PyYAML's); more than one document; a character PyYAML's reader refuses, which is any outside `\x09`, `\x0A`, `\x0D`, `\x20`-`\x7E`, `\x85`, `\xA0`-`퟿`, ``-`�`, and the astral planes, checked code point by code point (message `unreadable character ` and the character as `pyRepr` gives it, `src/lodge/core/yamlio.py:64`); a duplicate key (message naming the key as `pyRepr` gives it, `'title'`).
  Nesting deeper than 100 levels throws a `YamlError` with Python's message `the header is nested too deeply` and no line (`src/lodge/core/yamlio.py:61-62`), and the report lists the bound as a known narrowing of lodge 0.2 (d-bkc7md).
- `quoted` writes `JSON.stringify(text)`, which escapes as Python's `json.dumps(…, ensure_ascii=False)` does for every character `unreadableChar` lets through; where Python's `quoted` raises `ValueError`, it throws the `ValueError` of `errors.ts`.
- The carried settings tests build their input with `tomllib.loads`; in TypeScript that is `Bun.TOML.parse`, which tests may use (d-x6f9za), and no carried case holds a float, where the two differ (`grep -n toml tests/core/test_settings.py`; `plan-review-correctness.md`, M-9).

- [ ] **Step 1: Write the failing tests.**
  - The carried files, every test of `tests/core/test_ids.py`, `test_settings.py`, and `test_yamlio.py` by name.
  - `text.test.ts`: `is_py_space_matches_python` (each code point of the list above true, and U+FEFF, U+200B, and `a` false); `strip_removes_python_whitespace_only` (`"\x1c a \x85"` to `"a"`, `"﻿a"` unchanged); `rstrip_like_python` (`"a \x85"` to `"a"`, `"a﻿"` unchanged, `"## Reasoning\x1c"` to `"## Reasoning"`); `split_words_like_python` (`" a\x1fb  c "` to `["a", "b", "c"]`); `split_lines_like_python` (`"a\r\nb\x0bc\x1cd e\n"` to five lines, no empty last one); `is_digit_like_python` (`"12"`, `"²"`, and `"①"` true; `""`, `"1a"`, and `"½"` false); `casefold_like_python` (`"Straße"` to `"strasse"`, `"ſ"` to `"s"`, `"ﬆ"` to `"st"`, and `"ΑΣ"` to `"ασ"`); `py_repr_matches_python` (`a` to `'a'`, `it's` to `"it's"`, a text with both quotes, `a\b`, `\x01` to `'\x01'`, `\x85`, U+200B to `'​'`, a lone `\ud83d`, a tab and a newline, and `😀` kept); `code_point_length_counts_astral_once` (`"a😀"` is 2); `by_code_point_orders_astral_after_bmp` (`"￿"` before `"😀"`).
  - `stamps.test.ts`: `stamp_with_offset_is_a_stamp`; `stamp_without_offset_or_seconds_is_not` (`2026-10-29T12:00+01:00`, `2026-10-29T12:00:00`, `2026-10-29T12:00:00Z`); `impossible_date_is_not_a_stamp` (`2026-02-30T10:00:00+01:00`, `2026-10-29T24:00:00+01:00`, `0000-01-01T00:00:00+01:00`); `offset_is_read_as_python_reads_it` (`+00:60` and `+22:99` stamps, `+23:60`, `+24:00`, and `-23:99` not); `instant_respects_the_offset` (`2026-10-29T12:00:00+01:00` equals `2026-10-29T11:00:00+00:00`, and `0001-01-01T00:00:00+00:00` is `-62135596800000`); `compare_orders_by_instant`; `day_must_be_real`; `stamp_check_ignores_the_local_time_zone` (with `process.env.TZ` set to `Europe/Berlin`, `2026-03-29T02:30:00+01:00` is a stamp and its instant is that of `2026-03-29T01:30:00+00:00`).
  - In `yamlio.test.ts`, besides the carried tests: `collection_key_is_refused` (`[title]: x`, `{a: b}: c`, and `? [a, b]\n: c`, each `found unhashable key` at line 1); `integer_like_keys_keep_their_order` (`zz: a\n1: b\n` gives the keys `zz`, then `1`); `non_specific_tag_is_text` (`a: ! b\n` gives `a` to `b`); `str_tag_on_a_mapping_is_refused`; `nesting_beyond_the_bound_has_no_line` (101 nested brackets: the message, and no line).
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement** the interfaces above; delete the placeholder and its test; take `yaml` out of `ts/knip.json`'s `ignoreDependencies`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; expected: green, and knip reports no unused dependency; then flip `test_ids.py`, `test_settings.py`, and `test_yamlio.py` to `ported` and run it again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 5a: Record files

**Files:**
- Port: `src/lodge/core/fields.py`, `document.py`, `headers.py`, `fileformat.py`
- Create: `ts/src/core/fields.ts`, `ts/src/core/document.ts`, `ts/src/core/headers.ts`, `ts/src/core/fileformat.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`, `ts/knip.json` (`@noble/hashes` leaves `ignoreDependencies`)
- Test: `ts/tests/core/samples.ts`, `ts/tests/core/fileformat.test.ts`, `ts/tests/core/fileformat-problems.test.ts` (carried)

**Interfaces:**
- Consumes: Task 4.
- Produces, through `#core`: `areaPath`, `contentHash`, `newRecordPath`, `parseArea`, `parseRecord`, `slug`, `writeArea`, `writeRecord`; module-internal: `FormatError` (extending `Error`, as Python's extends `Exception`) and the readers of `fields.py`, which read the `Map`s `loadYaml` gives, so an unknown key is named in the text's order.
- `contentHash`: the first 12 hex characters of `@noble/hashes`' SHA-256 of the text's UTF-8 bytes, its line ends normalised first as Python's `normalise_newlines` does (probe 8); a lone surrogate, which Python encodes with `surrogateescape`, is listed in the report as a difference.
- Dates go through `stamps.ts`: `read_date` and `read_stamp` accept exactly what they accept in Python (`src/lodge/core/fields.py:121-163`), with the same messages.
- `document.py`'s `rstrip` (lines 44, 52, and 59) is `rstrip` of `text.ts`, so a line `## Reasoning` followed by U+FEFF does not start the reasoning, as in Python; every `!r` in a message is `pyRepr`.
- `writeRecord` and `writeArea` throw the `ValueError` of `errors.ts`, as Python's raise `ValueError`, when a text would not read back unchanged.

- [ ] **Step 1: Write the failing tests:** every test of `test_fileformat.py` and `test_fileformat_problems.py`, by name, with `samples.ts` from `samples.py`.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; take `@noble/hashes` out of `ts/knip.json`'s `ignoreDependencies`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green, and knip reports no unused dependency; flip `samples.py` and the two test files to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 5b: Drafts, and the text tests of record files

**Files:**
- Port: `src/lodge/core/drafts.py`
- Create: `ts/src/core/drafts.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`; Task 5a's modules only where a carried test finds them wrong
- Test: `ts/tests/core/drafts.test.ts`, `ts/tests/core/fileformat-text.test.ts` (carried)

**Interfaces:**
- Consumes: Task 5a.
- Produces, through `#core`: `Draft`, `parseDraft`, `recordFromDraft`.
- `drafts.py` imports only what Task 5a ports (`document`, `fields`, `headers`, and `model`), so its tests are written first and fail on the missing module.
- `fileformat-text.test.ts` carries tests over Task 5a's code, so each of its tests is seen failing against a mutation of that code the report names (such as `rstrip` swapped for `trimEnd`, or `splitLines` for `split("\n")`), and the mutation is reverted (d-mfayy5).

- [ ] **Step 1: Write the failing tests:** every test of `test_drafts.py` and `test_fileformat_text.py`, by name.
- [ ] **Step 2: Run** `cd ts && bun test tests/core/drafts.test.ts`; expected: FAIL; then, for each test of `fileformat-text.test.ts`, apply its named mutation, run it, see it fail, and revert.
- [ ] **Step 3: Implement** `drafts.ts`; fix in Task 5a's modules what a carried text test finds, each fix named in the report.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `test_drafts.py` and `test_fileformat_text.py` to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 6: Thread files and snapshots

**Files:**
- Port: `src/lodge/core/threads.py`, `snapshot.py`
- Create: `ts/src/core/threads.ts`, `ts/src/core/snapshot.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`
- Test: `ts/tests/core/builders.ts`, `ts/tests/core/thread-files.test.ts`, `ts/tests/core/snapshot.test.ts`, `ts/tests/core/fileformat-links.test.ts` (carried); `ts/tests/core/thread-text.test.ts` (new)

**Interfaces:**
- Consumes: Task 5b.
- Produces, through `#core`: `THREADS`, `appended`, `cleanText`, `newestLast`, `parseThread`, `threadPath`, `writeThread`; `ATTACHMENTS`, `Files`, `Snapshot`, `Tree`, `attachmentPath`, `load`.
- `Tree` is `{ rev: string | null; files: ReadonlyMap<string, string>; attachments: ReadonlySet<string> }`, the state the server's events will give (d-smx3xf).
- `newestLast` orders by `instant(opened)`, then by ID.
- `_ESCAPE` and `_UNESCAPE` (`src/lodge/core/threads.py:25-26`) are `re.MULTILINE` patterns, so they follow the Global Constraints' rule: a line starts only after `\n`.
- `thread-text.test.ts`: `escape_breaks_lines_at_newline_only` (a message body holding `x` U+2028 `## Message 1` and `y` CR `## Message 2` is written with no backslash added and reads back unchanged, as lodge 0.2 writes it; `plan-review-correctness.md`, I-2).

- [ ] **Step 1: Write the failing tests:** every test of `test_thread_files.py`, `test_snapshot.py`, and `test_fileformat_links.py` by name, with `builders.ts` from `builders.py`, and `thread-text.test.ts`; `thread_id_is_not_number_feedback` is a `test.todo` until Task 10, and `duplicate_id_marks_kept_record_failing` until Task 9a.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `builders.py` and `test_fileformat_links.py` to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7a: Doubts and derived statuses

**Files:**
- Port: `src/lodge/core/doubts.py`, `derive.py`
- Create: `ts/src/core/doubts.ts`, `ts/src/core/derive.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`
- Test: `ts/tests/core/derivation.ts`, `ts/tests/core/derive.test.ts`, `ts/tests/core/derive-links.test.ts`, `ts/tests/core/derive-confirmed-retired.test.ts`, `ts/tests/core/doubts.test.ts` (carried)

**Interfaces:**
- Consumes: Task 6.
- Produces, through `#core`: `Derived`, `derive`, `isAuthor`; module-internal: `orderKey`, which Task 7b's `confirmation.ts` imports.
- `derive`'s ordering key is `(instant(date), id)`, as `order_key` is `(datetime.fromisoformat(date), id)` (`src/lodge/core/derive.py:101-102`).
- `isAuthor` and every use of `author` stay as lodge 0.2 has them; people in `decided_by` are plan 2's change (d-88p8h9).

- [ ] **Step 1: Write the failing tests:** every test of `test_derive.py`, `test_derive_links.py`, `test_derive_confirmed_retired.py`, and `test_doubts.py` by name, with `derivation.ts` from `derivation.py`; `confirmed_decision_shows_confirmation_and_keeps_decided_by` and `flag_order` of `doubts.test.ts` are `test.todo` until Task 9a.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `derivation.py`, `test_derive.py`, `test_derive_links.py`, and `test_derive_confirmed_retired.py` to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7b: Confirmations and the order

**Files:**
- Port: `src/lodge/core/confirmation.py`, `order.py`
- Create: `ts/src/core/confirmation.ts`, `ts/src/core/order.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`
- Test: `ts/tests/core/confirmation.test.ts`, `ts/tests/core/order.test.ts` (carried)

**Interfaces:**
- Consumes: Task 7a.
- Produces, through `#core`: `MINUTE_FORMAT`, `VIEWER`, `behindArea`, `confirmableIds`, `confirmationDraft`; `Branch`, `Placement`, `areaNames`, `derivedOrder`, `restsOnTree`, `writtenOrder`.
- `confirmationDraft` throws the `ValueError` of `errors.ts` where Python raises `ValueError` (`src/lodge/core/confirmation.py:43`).

- [ ] **Step 1: Write the failing tests:** every test of `test_confirmation.py` and `test_order.py` by name.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `test_confirmation.py` and `test_order.py` to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 8a: The state check

**Files:**
- Port: `src/lodge/core/check_cycles.py`, `check_areas.py`, `check_state.py`
- Create: `ts/src/core/check-cycles.ts`, `ts/src/core/check-areas.ts`, `ts/src/core/check-state.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`
- Test: `ts/tests/core/checks.ts` (all of `checks.py` but `check` and `verdict`, which call `check_change`), `ts/tests/core/check-state.test.ts` (carried)

**Interfaces:**
- Consumes: Task 7b.
- Produces, through `#core`: `CheckResult`, `checkState`; module-internal: `newDecisions` and `problemAt`, which Task 8b imports.
- `checks.ts`'s `NOW` is `"2026-10-29T12:00:00+01:00"`, Python's `datetime(2026, 10, 29, 12, tzinfo=+1)`.
- `_codes` and `_quotes` (`src/lodge/core/check_state.py:101` and `:124`) use `casefold` of `text.ts`.
- Every check message is Python's, character for character, with `pyRepr` for every `!r`; the checks keep their numbers (s-j70a0k).

- [ ] **Step 1: Write the failing tests:** every test of `test_check_state.py` by name, with `checks.ts` as above.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `test_check_state.py` to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 8b: The change check

**Files:**
- Port: `src/lodge/core/check_entries.py`, `check_immutable.py`, `check_change.py`
- Create: `ts/src/core/check-entries.ts`, `ts/src/core/check-immutable.ts`, `ts/src/core/check-change.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`, `ts/tests/core/checks.ts` (gains `check` and `verdict`)
- Test: `ts/tests/core/check-change.test.ts`, `ts/tests/core/check-current.test.ts`, `ts/tests/core/check-retired.test.ts`, `ts/tests/core/check-immutable.test.ts` (carried)

**Interfaces:**
- Consumes: Task 8a.
- Produces, through `#core`: `checkChange`.
- `checkChange(published, after, settings, now, current: Snapshot | null = null)`, as Python's `check_change(published, after, settings, now, current=None)` (`src/lodge/core/check_change.py:21-27`), takes `now` as a stamp (Global Constraints), where Python takes a `datetime` (`:71`).
- Every check message is Python's, character for character, with `pyRepr` for every `!r`.

- [ ] **Step 1: Write the failing tests:** every test of `test_check_change.py`, `test_check_current.py`, `test_check_retired.py`, and `test_check_immutable.py` by name, and `check` and `verdict` in `checks.ts`.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `checks.py` and the four test files to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 8c: The other check tests

**Files:**
- Modify: `ts/tests/parity.json`; Task 8a's and 8b's modules only where a carried test finds them wrong
- Test: `ts/tests/core/check-compare.test.ts`, `ts/tests/core/check-links.test.ts`, `ts/tests/core/check-threads.test.ts` (carried)

**Interfaces:**
- Consumes: Task 8b.
- Produces: no new name; the carried tests of check 4's comparisons, the links, and the threads.
- These tests carry over code Tasks 8a and 8b ported, so each is seen failing against a mutation of that code the report names, and the mutation is reverted (d-mfayy5).

- [ ] **Step 1: Write the tests:** every test of `test_check_compare.py`, `test_check_links.py`, and `test_check_threads.py` by name; `thread_problems_are_visible_in_reads` of `check-threads.test.ts` is a `test.todo` until Task 9a.
- [ ] **Step 2: Run** each test against its named mutation and see it fail; revert each mutation.
- [ ] **Step 3: Fix** in Tasks 8a's and 8b's modules what a carried test finds, each fix named in the report with a test that failed before it.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `test_check_compare.py` and `test_check_links.py` to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 9a: Levels

**Files:**
- Port: `src/lodge/core/views.py`
- Create: `ts/src/core/views.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`, `ts/tests/core/snapshot.test.ts`, `ts/tests/core/doubts.test.ts`, `ts/tests/core/check-threads.test.ts` (their `test.todo`s become tests)
- Test: `ts/tests/core/views.test.ts`, `ts/tests/core/views-links.test.ts`, `ts/tests/core/views-trust.test.ts` (carried)

**Interfaces:**
- Consumes: Task 8c.
- Produces, through `#core`: `Level1`, `Level3`, `failingIds`, `formatLevel1`, `formatLevel3`, `headParts`, `level1`, `level2`, `level2Views`, `level3`, `unrecordedProblems`.
- The four `test.todo`s of Tasks 6, 7a, and 8c call `level1`, `failing_ids`, or `unrecorded_problems` only, all of `views.py`.

- [ ] **Step 1: Write the failing tests:** every test of the three Python files by name, and the four `test.todo`s that wait on this task.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip the three files, `test_snapshot.py`, `test_doubts.py`, and `test_check_threads.py` to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 9b: The rendered specification and search

**Files:**
- Port: `src/lodge/core/render.py`, `search.py`, `words.py`
- Create: `ts/src/core/render.ts`, `ts/src/core/search.ts`, `ts/src/core/words.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`
- Test: `ts/tests/core/render.test.ts`, `ts/tests/core/search.test.ts` (carried); `ts/tests/core/render-text.test.ts` (new)

**Interfaces:**
- Consumes: Task 9a.
- Produces, through `#core`: `Placed`, `SpecArea`, `renderSpec`, `specView`; `AmbiguousRef` (extending `LookupError`), `Filters`, `related`, `resolve`, `search`, `searchCounted`.
- `words.py`'s `[^\W_]+` becomes `[\p{L}\p{N}]+` with the `u` flag; its function words stay as they are.
- `search`'s "never" date is the earliest instant, as Python's `datetime.min` with UTC (`src/lodge/core/search.py:13`); `related`'s `w.isdigit()` (`:79`) is `isDigit` of `text.ts`.
- `_HEADING_LINE` (`src/lodge/core/render.py:11`) is a `re.MULTILINE` pattern with `$`, so it follows the Global Constraints' rule.
- `renderSpec` prints byte for byte what Python's `render_spec` prints for the same snapshot.
- `render-text.test.ts`: `heading_line_breaks_at_newline_only` (a statement holding U+2028 or a lone CR followed by `# x` renders as lodge 0.2 renders it, the line after U+2028 not taken for a heading; `plan-review-correctness.md`, I-2).

- [ ] **Step 1: Write the failing tests:** every test of `test_render.py` and `test_search.py` by name, and `render-text.test.ts`.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip the two files to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 10: Write feedback

**Files:**
- Port: `src/lodge/core/feedback.py`
- Create: `ts/src/core/feedback.ts`
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`, `ts/tests/core/thread-files.test.ts` (its `test.todo` becomes a test)
- Test: `ts/tests/core/feedback.test.ts`, `ts/tests/core/feedback-links.test.ts`, `ts/tests/core/feedback-revival.test.ts`, `ts/tests/core/area-feedback.test.ts` (carried)

**Interfaces:**
- Consumes: Task 9b.
- Produces, through `#core`: `Feedback`, `feedback`, `areaFeedback`.
- The patterns of `src/lodge/core/feedback.py:15-20` follow the Global Constraints' rules for `\b` and `\d`; a word count follows `splitWords`, and the title length `codePointLength`.

- [ ] **Step 1: Write the failing tests:** every test of the four Python files by name, and `thread_id_is_not_number_feedback`.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip the four files and `test_thread_files.py` to `ported`; green again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 11: Applying drafts

**Files:**
- Port: `src/lodge/core/apply.py`
- Create: `ts/src/core/apply.ts` (split by topic if it passes 300 lines, the second module named in the report)
- Modify: `ts/src/core/index.ts`, `ts/tests/parity.json`
- Test: `ts/tests/core/applying.ts`, `ts/tests/core/apply.test.ts`, `ts/tests/core/apply-refusals.test.ts` (carried); `ts/tests/core/front-door.test.ts` (new)

**Interfaces:**
- Consumes: Task 10.
- Produces, through `#core`: `Applied`, `StaleBase`, `applyDrafts`; with it `ts/src/core/index.ts` exports every name `src/lodge/core/__init__.py` exports, in camelCase.
- `StaleBase` is a `Problem` with `stale: true` where Python subclasses `Problem` (`src/lodge/core/apply.py:14`).
- `applyDrafts(current, tree, drafts, newDecisionIds, date, importing)` takes `date` as a stamp, as Python's `apply_drafts` does (`src/lodge/core/apply.py:41-48`).
- `except ValueError` at `src/lodge/core/apply.py:189` and `:233` becomes the Global Constraints' `catch` that throws on anything but a `ValueError`, so a bug in a writer is not turned into an add refusal.
- `front-door.test.ts`: `front_door_exports_every_python_name` reads `__all__` of `../src/lodge/core/__init__.py` and the export names of `ts/src/core/index.ts` with TypeScript's parser, types included, and finds each Python name there, a `snake_case` name in camelCase and an `UPPER_CASE` or `PascalCase` name as it is; and `front_door_exports_nothing_else` finds every other exported name in `errors.ts`, `text.ts`, or `stamps.ts`, which stand in for Python's standard library (d-s2rdn2).

- [ ] **Step 1: Write the failing tests:** every test of the two Python files by name, with `applying.ts` from `applying.py`, and `front-door.test.ts`.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip the three files to `ported`; then `grep -c '"planned"' ts/tests/parity.json` counts only rows of plans 2 to 4, and no plan 1 row is `planned`.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 12: The differential run against lodge 0.2

**Files:**
- Create: `ts/scripts/differential.ts`, `scripts/differential_dump.py`, `scripts/differential.sh`
- Modify: `ts/package.json` (the `check` script's `depcruise` also cruises `scripts`)
- Report: `docs/superpowers/plans/2026-11-02-lodge-server-core/task-12-report.md`

**Interfaces:**
- Consumes: Task 11; lodge 0.2's core (`from lodge.core import …`).
- Produces: a comparison of what the two cores derive and write from one store (d-0qmd10).
- `scripts/differential_dump.py ROOT` reads every file under `ROOT/lodge/` into lodge 0.2's `Tree`, takes `CoreSettings` from `ROOT/.lodge.toml`'s `[length]` and `[import]` tables through `parse_core_settings`, and prints one JSON object:
  - `spec`: `render_spec` of the whole store;
  - `problems`: `check_state`'s problems as `[path, check, line, message]`, sorted;
  - `levels`: for every decision and entry ID, `[format_level1(level1), level2, format_level3(level3)]`;
  - `search`: for the first word of each record's title, the IDs `search` returns with no filters and a limit of 20;
  - `rewrite`: for every record and area file that `parse_record` or `parse_area` reads without a problem, the SHA-256 in hex of the UTF-8 bytes of what `write_record` or `write_area` gives for it, and whether that text equals the file's (d-0qmd10; `plan-review-practice.md`, P-I10).
- `ts/scripts/differential.ts ROOT PYTHON_JSON` computes the same object with the TypeScript core (reading the files and parsing `.lodge.toml` with `Bun.TOML.parse`, outside `src`), compares the two key by key, prints each difference as its key path and both values, and exits 1 on any difference and 0 on none, printing the counts of records, areas, threads, problems, queries, and rewritten files compared.
- `Bun.TOML.parse` gives `5` for `5.0`, where `tomllib` gives a float that `parse_core_settings` refuses (`plan-review-correctness.md`, M-9); this repository's `.lodge.toml` has no `[length]` table, so the run is not affected, and the report says so for the third plan.
- `scripts/differential.sh` runs `uv run --frozen --quiet python scripts/differential_dump.py "$PWD"` into a file under `.drafts/`, then `bun ts/scripts/differential.ts "$PWD" <that file>`.
- The run reads this repository's records in place and writes them nowhere; only the counts and the differences go into the report (d-0qmd10; `CLAUDE.md`, "Hard rules").

- [ ] **Step 1:** Write the three scripts; `uv run ruff format --check scripts/differential_dump.py` and `uv run ruff check scripts/differential_dump.py` pass; `sh scripts/check-ts.sh` is green.
- [ ] **Step 2:** Run `sh scripts/differential.sh`.
- [ ] **Step 3:** For each difference, the report names the record's ID, the key, how the two values differ (without quoting the record), and the TypeScript module at fault; a difference is fixed in that module with a carried-style test that fails first (a test of the made-up project reproducing it, never the record itself), and the run repeats until it prints no difference.
- [ ] **Step 4: Verify** `sh scripts/differential.sh` exits 0 and prints the counts, which the report gives as printed; at `c3320a4` the store held 192 decisions and 137 files under `lodge/spec/` (`ls lodge/decisions | wc -l`, `find lodge/spec -type f | wc -l`), Task 1 adds eight decisions and the plan's rulings more, and the store holds no threads, so the thread code rests on the carried tests and Task 6's new test alone.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, then `sh scripts/differential.sh` outside the sandbox, commit, push.
