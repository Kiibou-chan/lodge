# Plan review: correctness

Plan: `docs/superpowers/plans/2026-11-02-lodge-server-core.md` at `c3320a4` (branch `server-core`).
Angle: correctness; does each task, built as written, behave as the authority says, and do the tasks fit together.
Reviewer: `reviewer` agent, 2026-11-02.

## Findings

### I-1 (Important): `test.each(cases)` spreads a list case into arguments, so carried cases change silently

Handle: plan line 29 ("a parametrised test becomes `test.each(cases)("name %p", …)` … with every case of the Python list"); `tests/core/test_settings.py` (`@pytest.mark.parametrize("value", ["docs/a.md", [1], [""], 7])`).
Probe, Bun 1.3.14, in a scratch folder: `test.each(["docs/a.md", [1], [""], 7])("sources %p", (value) => console.log(JSON.stringify(value)))` prints `"docs/a.md"`, `1`, `""`, `7`.
Failure: a builder following line 29 to the letter carries `[1]` as `1` and `[""]` as `""`; the test still passes, but the cases "a list holding a non-string" and "a list holding an empty string" are no longer tested, which is Review Focus 1's failure with no reviewer able to see it from the titles (the `%p` title prints `1`, not `[1]`).
Fix: line 29 says a single-argument case list is passed as `cases.map((c) => [c])` (or as objects with `test.each(cases)("name %p", ({ value }) => …)`), and a multi-argument Python case `(a, b)` as `[a, b]`; and add to Review Focus 1: "a list-valued case passed to `test.each` unwrapped".

### I-2 (Important): the text rules miss Python operations the core uses, so the port diverges on the very characters Review Focus 2 names

Handles: plan lines 35 and 36 (the operations `text.ts` covers: `strip`, `split()`, `splitlines`, `isspace`, `len`; the regex rules); plan lines 391 to 398 (`text.ts`'s interface).
Python operations in `src/lodge/core` with a JavaScript namesake that differs and no rule in the plan:
- `str.rstrip()` at `src/lodge/core/document.py:44`, `:52`, and `:59` (`trim_block` and the `## Reasoning` line test); JavaScript's `trimEnd()` strips U+FEFF and keeps U+001C to U+001F and U+0085 (probe 12), so a statement ending in U+0085 is stored differently, and a line `## Reasoning` followed by U+FEFF splits the body in TypeScript and not in Python.
- `re.MULTILINE` at `src/lodge/core/render.py:11` and `src/lodge/core/threads.py:25-26`: Python's `^` and `$` there break only at `\n`, JavaScript's `m` flag also at `\r`, U+2028, and U+2029; so a message body holding U+2028 followed by `## Message 1` is escaped by the TypeScript `writeThread` and not by Python, and the thread file text differs.
- `repr()` and `!r` in messages (15 uses: `fields.py` 8, `yamlio.py` 2, `drafts.py` 2, `apply.py` 2, `fileformat.py` 1): Python picks double quotes for a text holding `'` and escapes non-printable characters (`repr("it's")` is `"it's"`, `repr` of "a", U+200B, "b" is `'a` backslash `u200bb'`, `repr("\x01")` is `'\x01'`, checked with Python 3.13.5); Task 8 line 491 promises "every check message is Python's, character for character", and the `unreadable character …` message of `yamlio.py:64` is always a repr of a non-printable character.
- `str.casefold()` at `src/lodge/core/check_state.py:101` and `:124` (the "author" test on `decided_by`), and `str.isdigit()` at `src/lodge/core/search.py:79` (true for `²`, which `\p{Nd}` does not match).
Failure: the builder of Task 4 or 5 writes `trimEnd()`, `/m`, and `'${x}'`, the carried tests (ASCII fixtures) pass, and the differential run (valid records only) prints no difference, so the divergence reaches the server unseen.
Fix: add to `text.ts`'s interface `rstrip`, `pyRepr` (quote choice, `\\`, `\t`, `\n`, `\r`, `\xNN`, `\uNNNN`, `\UNNNNNNNN` for characters `str.isprintable()` refuses), `casefold` (at least the full case folding of `ß`, `ſ`, ligatures, and final sigma, or a stated limit), and `isDigit`; add to line 36 "`re.MULTILINE` becomes a split on `\n` or the lookarounds `(?<=^|\n)` and `(?=\n|$)` without `m`, and `.` without `DOTALL` becomes `[^\n]`"; add text tests for each, U+0085, U+FEFF, and U+2028 included.

### I-3 (Important): the YAML layer's refusal list misses collection keys, and the `yaml` package's objects reorder keys

Handles: plan line 406 (`loadYaml`'s refusals), d-458jhp; `src/lodge/core/yamlio.py:38-46` and `:53-64`.
Probe, PyYAML through `uv run python` with `lodge.core.load_yaml`: `[title]: x`, `{a: b}: c`, and `? [a, b]\n: c` each raise `YamlError("found unhashable key", line 1)`.
Probe, `yaml` 2.9.1 under Bun with `parseAllDocuments(t, {schema: "failsafe", uniqueKeys: true})` and `toJS()`: the same three texts load with no error and no warning in `errors` or `warnings`, as keys `"[ title ]"`, `"{ a: b }"`, and `"[ a, b ]"`, and the package writes `Warning: Keys with collection values will be stringified …` through `console`, from inside `core`; and `zz: a\n1: b\n` loads with keys in the order `1`, `zz`, where Python's dict keeps `zz`, `1`.
Failure: a header with a collection key is refused with `unknown key '[ title ]'` on the key's line instead of `the header is not valid YAML: found unhashable key`, and `check_keys` (`fields.py:27-33`) and `read_map` (`fields.py:76-80`) name a different first unknown key when one is integer-like; a console line appears in the server's output for a malformed draft.
Fix: line 406 adds "a mapping key that is not a scalar (message `found unhashable key`)" to the refusals, and says `loadYaml` walks the parsed `Document`'s nodes itself (never `toJS()`), returning a `Map` for a mapping so that key order is the text's; Task 4's text test gains `collection_key_is_refused` and `integer_like_keys_keep_their_order`.

### I-4 (Important): knip fails the gate of Tasks 2, 3, and 4 on `yaml` and `@noble/hashes`, which no code imports until Tasks 4 and 5

Handles: plan line 292 (`dependencies`: `@noble/hashes`, `yaml`), line 304 (the only remedy: a dev dependency the gate uses goes into `ignoreDependencies`), line 318 (Task 2's verify: `sh scripts/check-ts.sh` exits 0), lines 375 and 415 (Tasks 3 and 4: green), line 429 (`@noble/hashes` first used by `contentHash`, Task 5).
Probe: Task 2's files written as the plan gives them in a scratch folder (`package.json` verbatim, `tsconfig.json`, `biome.json`, `knip.json`, the two-rule `.dependency-cruiser.cjs`, the placeholder and its test), `bun install`, `bun run check`: Biome, `tsc`, and dependency-cruiser pass, then knip prints `Unused dependencies (2)` `@noble/hashes` and `yaml` and exits 1, so `bun test` never runs.
Failure: Task 2's Step 2 fails as written; the coordinator can improvise, but Tasks 3 and 4 are builder tasks whose gate stays red for a reason outside their files (`ts/knip.json` is in neither task's Files), and a builder told never to touch `ts/package.json` either stops BLOCKED or edits `knip.json` unasked.
Fix: Task 2's `knip.json` gets `"ignoreDependencies": ["yaml", "@noble/hashes"]`, said in the ledger line; Task 4 removes `yaml` from it and Task 5 removes `@noble/hashes`, each with `ts/knip.json` in its Modify list and a step "knip reports no unused dependency".

### I-5 (Important): the structure rows of the parity table have no stated status, and both readings break a later step

Handles: plan lines 218 to 225 (seven rows "Plan 1, Task 3, changed", `ts/tests/structure/*.test.ts`); line 365 ("every plan 1 row starts `planned`, and each task flips its rows to `ported` in its last step"); Task 3's steps (lines 367 to 376), which flip nothing; line 556 (Task 11: "no plan 1 row is `planned`").
If the seven rows start `planned` (line 365), nothing flips them and Task 11's Step 4 fails.
If they become `ported`, `ported_files_keep_every_python_test_name` (line 372) fails: `tests/test_structure.py` and `tests/test_structure_io.py` hold 38 test names, and Task 3's titles (line 368 to 371) do not include `submodule_through_front_door`, `from_lodge_import_package`, `import_statement_form`, `import_inside_function`, `source_that_is_not_utf8_names_the_file`, `syntax_error_is_reported`, `real_tree_is_clean`, `open_outside_gitstore_and_cli`, `webbrowser_open_is_not_a_file_open`, and others (`grep -n 'def test_' tests/test_structure.py tests/test_structure_io.py`); and `ported_files_exist` cannot check the glob `ts/tests/structure/*.test.ts`.
Failure: the Task 3 builder picks a status the plan does not give, and either its own parity test or Task 11's check goes red.
Fix: line 365 says rows marked "changed" in the table, the seven structure rows included, are `changed` from the start with `plan` and `task` kept and the design line as `why`; the seven rows list the four test files of Task 3 by name instead of the glob; Task 11's Step 4 reads "no plan 1 row is `planned`" as it does now.

### I-6 (Important): Python's `ValueError` has no TypeScript class, though 17 carried tests expect it and the core catches it

Handles: plan line 33 ("an exception becomes a class extending `Error` with the Python name"), line 431 ("an `Error` named `ValueError`", for `writeRecord` and `writeArea` only); `src/lodge/core/yamlio.py:19` (`class YamlError(ValueError)`), `src/lodge/core/settings.py:7` (`class SettingsError(ValueError)`); raise sites `ids.py:14`, `confirmation.py:43`, `fileformat.py:44-68` and `:120`, `threads.py:103` and `:127`, `yamlio.py:81`, `apply.py:57`; catch sites `apply.py:189`, `apply.py:233`, `fileformat.py:119`, `threads.py:102`, and in plan 2's `app/threads.py:82` and `app/confirm.py:76`; `pytest.raises(ValueError` 17 times in `tests/core` (`test_ids.py:19`, `test_confirmation.py:112`, `test_apply_refusals.py:27`, `test_fileformat.py`, `test_fileformat_text.py`, `test_thread_files.py`).
Failure: an `Error` whose `name` is `"ValueError"` cannot be named in `toThrow(ValueError)`, so the carried assertions weaken to a pattern only (Review Focus 1); Task 4's `mintId`, Task 5's `writeRecord`, and Task 6's `writeThread` each invent their own form; and Task 11's port of `except ValueError` becomes a bare `catch`, which turns a `TypeError` from a bug in `writeRecord` into an add refusal with the bug's message.
Fix: Task 4 adds `ts/src/core/errors.ts` with `class ValueError extends Error` (exported through `#core`), and `YamlError` and `SettingsError` extend it as in Python; line 33 says a built-in Python exception the core raises gets one such class, and an `except E` becomes `catch (e) { if (!(e instanceof E)) throw e; … }`.

### I-7 (Important): nothing stops `stamps.ts` from reading the machine's time zone, and a local-time date check refuses real stamps

Handles: plan line 37 (`stamps.ts` parses and compares stamps), line 360 (`callViolations` flags `Date.now`, and `new Date()` and `Date()` with no argument only), line 369 (`new_date_with_an_argument_is_allowed`), line 412 (`impossible_date_is_not_a_stamp`), Review Focus 5.
Probe, Bun 1.3.14: `process.env.TZ = "Europe/Berlin"; new Date(2026, 2, 29, 2, 30, 0).getHours()` prints `3` (the hour falls in the clock change), and with `TZ` set to `UTC` it prints `2`.
Failure: a builder checks "a real date and time" the usual way, by building a local `Date` from the fields and comparing them back; every listed stamps test passes on a machine in UTC, and on a server in Europe/Berlin `isStamp("2026-03-29T02:30:00+01:00")` is false, so a decision dated in that hour is refused, and the core's answer depends on the machine it runs on, against the pure `core` of design line 58 and Review Focus 5.
Fix: line 400 says `isStamp`, `isDay`, and `instant` compute with `Date.UTC` and integer arithmetic only; `callViolations` also flags, in `core` and `app`, `Intl`, `new Date(…)` or `Date(…)` with more than one argument, and calls of `getTimezoneOffset`, the local getters (`getHours`, `getDate`, and the like), and `toLocale…`; `stamps.test.ts` gains `stamp_check_ignores_the_local_time_zone`, which sets `process.env.TZ` to `Europe/Berlin` and checks the stamp above.

### M-1 (Minor): the nesting limit of 100 refuses headers lodge 0.2 reads, and gives a line where Python gives none

Handles: plan lines 62 and 406, d-458jhp ("refuses what PyYAML refuses … nesting deeper than 100, each as a `YamlError` with its line"); `src/lodge/core/yamlio.py:61-62` (a `RecursionError` becomes `YamlError("the header is nested too deeply")` with no line).
Probe, `lodge.core.load_yaml` on `a: ` followed by N brackets, Python 3.13.5: N = 101, 150, 200, 300, and 400 load; N = 500 and 900 raise with line `None`.
Failure: a header nested 101 to about 450 deep, which lodge 0.2 stores, is refused after import; no carried test sees it (the tests use 1,000 and 5,000).
Fix: keep 100 as a fixed limit, since Python's threshold follows its recursion limit, but say in d-458jhp's statement and line 406 that it narrows lodge 0.2 by design, with the message `the header is nested too deeply` and no line, as Python gives.

### M-2 (Minor): `isStamp`'s "offset within ±23:59" is not what `datetime.fromisoformat` accepts

Handles: plan line 400; `src/lodge/core/fields.py:13` and `:155-163`.
Probe, Python 3.13.5: `datetime.fromisoformat` accepts `+00:60` (as +01:00), `+00:99` (+01:39), and `+22:99` (+23:39), and refuses `+23:60`, `+24:00`, and `-23:99`; year `0000` is refused and `0001-01-01T00:00:00+01:00` accepted.
Failure: a stamp such as `2026-10-29T12:00:00+00:60` is a valid date in lodge 0.2 and a refused one in TypeScript.
Fix: line 400 says the offset is accepted when its hours and minutes are two digits each and hours × 60 + minutes is below 1,440, the year is 0001 or later, and `stamps.test.ts` gains these cases.

### M-3 (Minor): two signatures differ from the Python they port

Handles: plan line 490 (`checkChange(published, after, settings, now, snapshot?)`) against `src/lodge/core/check_change.py:21-27` (`current: Snapshot | None = None`); plan line 551 ("`applyDrafts` takes `now` as a stamp") against `src/lodge/core/apply.py:41-48` (`date: str`, no `now`).
Failure: the optional parameter `snapshot?` is `undefined`, against line 33 (`X | None` becomes `X | null`), and its name hides that it is the state the change starts from; a builder adds a `now` to `applyDrafts` that the Python does not have, against line 27.
Fix: line 490 reads `checkChange(published, after, settings, now, current: Snapshot | null = null)`; line 551 reads "`applyDrafts` takes `date` as a stamp, as Python does".

### M-4 (Minor): knip does not check the front doors' exports, so line 40 is not enforced there

Handles: plan line 40 ("every export of a module is read by another module or by a test"), line 304 (`knip.json`).
Probe, knip 6.42.0 with Task 2's `knip.json`: an `export { NEVER_READ } from "./other.ts"` and an `export type { NeverType }` in `src/core/index.ts` are not reported, since knip takes the `#core` target of `package.json`'s `imports` as an entry; with `--include-entry-exports` both are reported.
And with that switch on, 13 names that the Tasks' Produces lists put through `#core` are named by no carried core test (`ATTACHMENTS`, `MINUTE_FORMAT`, `THREADS`, `VIEWER`, `Branch`, `Derived`, `Files`, `Placed`, `Placement`, `SpecArea`, `attachment_path`, `clean_text`, `head_parts`; computed over `tests/core` against `lodge.core.__all__`).
Failure: an unused export through a front door passes the gate unseen; switching the check on later fails Tasks 6, 7, and 9 at once.
Fix: either say in line 40 that front doors are exempt until their consumers exist (plan 2), or set `includeEntryExports: true` and name, in Tasks 6, 7, and 9, a test reading each of the 13 names.

### M-5 (Minor): the confinement rules must be limited to `src`, and dependency-cruiser drops the `node:` prefix

Handles: plan lines 352 to 357 (`file-confinement`: "`node:fs` or `node:fs/promises` imported outside `git`, `store`, and `cli`"), line 290 (`depcruise src tests`), line 563 (Task 12 adds `scripts`).
`parity.test.ts` reads `../tests`, `plant.ts` writes temporary trees, and `ts/scripts/differential.ts` reads the records, so each needs file access from outside the three packages.
Probe, dependency-cruiser 18.6.0 on a planted `src/core/index.ts` importing `node:fs`: the dependency's `module` is `fs`, type `core`.
Failure: a rule written over every module, or matching `^node:fs` only, either fails `repository_has_no_violations` on the tests and scripts or misses the import it is for.
Fix: line 348 says every confinement rule's `from` is `^src/`, and each `to` matches the name with and without `node:` (`^(node:)?fs(/promises)?$`).

### M-6 (Minor): `plant` needs `ts/node_modules` in the planted tree

Handles: plan line 336 (`plant` writes `package.json`, `tsconfig.json`, and the files), line 368 (`core_may_import_yaml_and_noble_hashes`, `core_importing_other_npm_package`).
Probe, dependency-cruiser 18.6.0 on a planted tree with no `node_modules`: `yaml` and `@noble/hashes/sha2.js` come back with type `unknown` and `couldNotResolve: true`.
Failure: `core_may_import_yaml_and_noble_hashes` sees `not-to-unresolvable`, and `core_importing_other_npm_package` sees no `npm` dependency for `core-imports` to match.
Fix: line 336 says `plant` links `ts/node_modules` into the planted folder, and the planted `tsconfig.json` is `ts/tsconfig.json`'s options.

### M-7 (Minor): Biome's recommended rules refuse the control-character classes the port needs

Handles: plan line 303 (Biome's recommended lint rules), line 406 (the PyYAML reader's character set), `src/lodge/core/yamlio.py:12` (`_UNREADABLE`).
Probe, Biome 2.5.15 on `/[\x00-\x1f\x7f-\x9f…]/u` and `/[^\x09\x0A\x0D\x20-\x7E\x85…]/u`: `lint/suspicious/noControlCharactersInRegex` errors at each control-character escape (five errors).
Failure: the Task 4 builder meets a red gate on the most direct port and either loosens `biome.json`, which `CLAUDE.md` forbids, or improvises.
Fix: line 406 says the character sets are written as code-point range checks in `text.ts` or `yamlio.ts`, not as regular expressions (or with a `biome-ignore` comment giving the reason, if the coordinator rules that acceptable).

### M-8 (Minor): Task 2's `package.json`, as printed, does not pass `biome check`

Handles: plan lines 282 to 301 and line 303 (Biome checks the JSON files).
Probe: the `package.json` of lines 282 to 301 written verbatim fails `biome check .` with `Formatter would have printed the following content`, expanding `"imports"` and `"dependencies"` onto several lines; `"recommended": true` in `biome.json` draws a deprecation notice in 2.5.15.
Failure: Task 2's Step 2 is red on formatting before any real check runs.
Fix: Task 2's Step 1 ends with `bunx biome format --write .` in `ts/`, or prints the files in Biome's layout.

### M-9 (Minor): TOML read by `Bun.TOML.parse` cannot tell `80.0` from `80`

Handles: plan line 574 (Task 12 parses `.lodge.toml` with `Bun.TOML.parse`); `src/lodge/core/settings.py:55` (`isinstance(value, int)`).
Probe: `Bun.TOML.parse("[length]\ntitle = 5.0\n")` gives the number `5`, and `Number.isInteger` is true; Python's `tomllib` gives a `float`, which `parse_core_settings` refuses.
Failure: none in this plan's carried tests (they pass Python values); the differential run and plan 3's command accept `title_chars = 80.0`, which lodge 0.2 refuses.
Fix: note it in Task 12's report and in plan 3's paragraph, where the command reads `.lodge.toml`.

### M-10 (Minor): Task 12's expected counts do not match the store

Handles: plan line 581 ("about 175 decisions, 155 files under `lodge/spec/`, the threads, and every area").
Probe on `server-core` at `c3320a4`: `ls lodge/decisions | wc -l` is 192 (200 once Task 1 adds eight), `find lodge/spec -type f | wc -l` is 137, and `lodge/threads` does not exist.
Failure: the verify step's counts look wrong to the builder and the reviewer, and the run compares no thread at all, so `threads.ts` and the thread checks get no differential coverage.
Fix: line 581 gives the counts as read at the time of the run, and says the store holds no threads, so the thread code rests on the carried tests alone.

### M-11 (Minor): Task 1's verify expects the eight at "their minutes", which `lodge add` does not give

Handles: plan line 268; `src/lodge/app/writes.py:142-149` (an add dates its decisions at the time of the add, after the newest decision).
Failure: `lodge search --by author` lists the eight at the day of the add, and their minutes appear only in `quote.when`, so the coordinator may think the add went wrong.
Fix: line 268 reads "lists the eight; `lodge show <id> --provenance` gives each quote's minute".

### M-12 (Minor): the probe's software authenticator does not pass strict `tsc`

Handles: plan line 101 (the later plans' tests use `probes/tests/passkey.test.ts`), line 302 (strict `tsc`).
Probe: `tsc -p .` over the probe folder prints two `TS2345` errors at `tests/passkey.test.ts:11` and `:37` (`Uint8Array<ArrayBufferLike>` is not assignable to `Uint8Array<ArrayBuffer>`); `bun test` passes it.
Failure: plan 3's builder copies the authenticator and meets a red gate.
Fix: plan 3's paragraph says the authenticator is typed for strict `tsc` (its buffers built as `new Uint8Array(new ArrayBuffer(n))`) when carried.

### M-13 (Minor): the tag rule refuses the non-specific tag `!`, which PyYAML reads as text

Handles: plan line 406 ("any tag other than `!!str`, `!!seq`, and `!!map`"); `src/lodge/core/yamlio.py:11` (`_KEPT_TAGS` holds `None`), PyYAML's composer resolving `!` as an untagged node.
Probe: `lodge.core.load_yaml("a: ! b\n")` and `load_yaml("! a: b\n")` give `{'a': 'b'}`; under Bun, `yaml` 2.9.1's node for `a: ! b` has the tag `"!"` and no warning, and `!<tag:yaml.org,2002:str>` comes back as `tag:yaml.org,2002:str`.
Failure: a header with `!` before a value is refused by TypeScript and read by lodge 0.2.
Fix: line 406 reads "any tag other than `!`, `!!str`, `!!seq`, and `!!map`, the last three on the node kind they name (a `!!str` on a mapping is refused, as PyYAML refuses it)"; a carried-style case joins `text.test.ts` or `yamlio.test.ts`.

## Checked and found sound

- The parity table: its 126 Python paths equal `git ls-files tests` exactly (`diff` empty), and the folder holds no untracked file outside `__pycache__` (`find tests -type f -not -path '*/__pycache__/*'`, 126).
- Task order against the Python imports: every module a task ports imports only modules of earlier tasks or its own (checked from the `from lodge.core.…` lines of all 27 modules), and the 27 modules are each ported by exactly one task.
- The `test.todo` list: an AST walk of `tests/core` finds exactly the five tests that call a later task's name (`test_snapshot.py::test_duplicate_id_marks_kept_record_failing`, `test_thread_files.py::test_thread_id_is_not_number_feedback`, `test_doubts.py::test_confirmed_decision_shows_confirmation_and_keeps_decided_by` and `::test_flag_order`, `test_check_threads.py::test_thread_problems_are_visible_in_reads`), as Tasks 6 to 10 name them; no helper file (`builders.py`, `checks.py`, `derivation.py`, `samples.py`, `applying.py`) reaches past its task.
- The flips: Tasks 4 to 11 flip 3, 5, 2, 6, 8, 8, 5, and 3 rows, 40 in all, the 40 files of `tests/core`.
- The Produces lists of Tasks 4 to 11 together hold all 91 names of `lodge.core.__all__`; no default-filling function clashes with a function of the same name (`Feedback`, `Level1`, and `Level3` have no defaults).
- Cited lines: `derive.py:101-102`, `fields.py:121-163`, `search.py:13`, `apply.py:14`, `check_change.py:21` and `:71`, `checks.py:23` (`NOW`), design lines 3, 55, 58, 72, 75, 77, 78, 79, 196, 275, 282 to 285, 289, 290, and 298, and the viewer plan's line 21 all say what the plan says they say; `lodge guide`'s last line gives the exit codes of line 96.
- Sandbox limits: no builder task stages, commits, pushes, installs, binds a socket, or uses the network; Task 1 and Task 2 are the coordinator's; Task 12's `uv run --frozen` and `.drafts/` write stay inside the worktree.
- `scripts/check.sh` is `set -eu` from the repository root, so the added last line runs the TypeScript gate only after lodge 0.2's passes.

## Probes rerun

- Probes 1 and 2: `bun test tests` over a copy of `probes/` (packages from Bun's cache): `3 pass, 0 fail`.
- Probe 5: the committed `probes/src` gives `no dependency violations found`, since the violating files are not kept; with a cycle, a `#app` import from `core`, a `node:fs` import in `core`, and a relative import past a front door planted, `depcruise` reports `no-cycles`, `allowed-imports`, `core-no-node`, and `front-door`, one each, as the probe says.
- Probe 6: in the same run, `#core` imports carry the types `aliased` and `aliased-subpath-import`, and `bun:sqlite` is of type `core`.
- Probes 7 and 8: `bun yprobe.ts` and `bun h.ts` print what `probes.md` quotes.
- Probe 11's dates were not rechecked (no network used).
- New probes, each cited at its finding: Task 2's gate (I-4, M-8), `test.each` (I-1), PyYAML and `yaml` edge cases (I-3, M-13), `TZ` (I-7), nesting and offsets (M-1, M-2), knip's front doors (M-4), dependency-cruiser on a planted tree (M-5, M-6), Biome on control characters (M-7), TOML (M-9), strict `tsc` over the probes (M-12).

## Read and not read

Read: the plan in full, its ledger, `planner-brief.md`, `probes.md`, `planner-report.md`, every file of `probes/`; `CLAUDE.md`; the design's lines cited above and 50 to 62; the rulings d-458jhp, d-k5swcq, d-4psbdv, d-g7ynw0, d-smx3xf, d-g3mbmc, d-88p8h9, and d-j3z85y through `lodge show`; `lodge guide`'s last lines; in `src/lodge/core`, `yamlio.py`, `fields.py`, `ids.py`, `settings.py`, and the parts of `check_change.py`, `snapshot.py`, `apply.py`, `derive.py`, `search.py`, `document.py`, `fileformat.py`, `threads.py`, and `feedback.py` cited above, and the import lines, regular expressions, and string operations of every core module; `src/lodge/app/lodge.py`'s method list and `writes.py`'s date lines; `tests/core/test_yamlio.py`, `test_settings.py`, `test_ids.py`, the nesting tests of `test_fileformat_text.py` and `test_drafts.py`, the `pytest.raises` lines of `tests/core`; `tests/structure_tables.py`; the test names of `tests/test_structure.py` and `tests/test_structure_io.py`; `scripts/check.sh`; the tool tables of `pyproject.toml`; `.lodge.toml`.
Not read: `lodge spec` in full (only through the rulings and `lodge guide`); the other design documents, the architecture options, and the research notes; the bodies of most core modules beyond the lines cited (`views.py`, `render.py`, `order.py`, `confirmation.py`, `doubts.py`, `headers.py`, `drafts.py`, `check_*.py` other than `check_change.py`); the carried test files other than those named; `src/lodge/app` beyond the two files named, `cli`, `gitstore`, `viewer`, and `hook`; the viewer plan beyond its line 21.

## Counts

Blocking 0, Important 7, Minor 13.
