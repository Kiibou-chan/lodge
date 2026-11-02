# Task 4 review

Commit under review: bba4a92 against 471b8ca, `ts/` only.
Scratch worktree for probes: `.claude/worktrees/review-task4` of the main checkout, detached at bba4a92, removed when done.
Passes in order: correctness, practice, design.

## Correctness

### What holds

Every carried test of `tests/core/test_ids.py`, `test_settings.py`, and `test_yamlio.py` is present under its name, with every parametrised case, single-parameter lists wrapped as `cases.map((c) => [c])`, and `toThrow` carrying both the class and Python's pattern; none asserts less than its original.
Every brief-named new test exists, and 29 mutations of the code under them each turned a test red (`collection_key_is_refused`, `non_specific_tag_is_text`, `str_tag_on_a_mapping_is_refused`, both halves of `nesting_beyond_the_bound_has_no_line`, all twelve text tests, the stamp tests except the two in M-1 and M-2 below, and `stamp_check_ignores_the_local_time_zone` against an `instant` built on local `Date`).
The known differences are as stated, measured over all 1,114,112 code points against Python 3.13.5 (Unicode 15.1.0): `isDigit` differs at 90, the first U+10D40; `casefold` at 174, none giving or losing a letter of `author`; `pyRepr` at 9,988, every one of category `Cn` in Python's database; `isPySpace`, `strip`, `rstrip`, `splitWords`, and `splitLines` at none.
`isStamp`, `isDay`, and `instant` agree with `_STAMP` plus `datetime.fromisoformat` and with `int(timestamp()) * 1000` on 60,007 generated stamps (1,716 valid) and 20,000 days, with no difference.
`quoted` agrees with Python's on 24,588 inputs, with and without every refused character in `allowed`.
Nesting of 10,000 to 200,000 levels of `[`, `{a: `, and block sequences ends in the `YamlError`, never a stack overflow.
No `Date`, clock, `process`, or `console` appears in `ts/src/core` (`grep -nE "Date|process|console|Math\.random|Intl|localeCompare" ts/src/core/*.ts`).
A 132-text YAML corpus run through both `load_yaml` and `loadYaml` gives the results below; the corpus and both runners are reproducible from the finding text.

### C-1 · Blocking · an alias header that Python reads at once takes hours in TypeScript

Handle: `ts/src/core/yamlio.ts:98-101` and `:116`.
`walk` follows each alias into its target again, so a header of nine anchors, each a sequence of ten aliases to the one before, costs 10^9 node visits.
Scenario, run: a 511-byte header `a0: &a0 [x, …]` then `a1: &a1 [*a0, …]` up to `a8`; Python's `load_yaml` returns in 0.12 s, sharing the aliased lists as PyYAML's constructor does; `loadYaml` takes 0.12 s at four levels, 1.05 s at five, and 12.2 s at six, and the run was stopped at the 120 s limit before seven.
Plan 2 runs the check on every write, so one draft stalls the server.
Recursive aliases differ too: `a: &x [*x]` gives Python a list holding itself and gives TypeScript `the header is nested too deeply`.
Fix: memoise the walk per node, registering the new array or `Map` before walking its children, as PyYAML's `constructed_objects` does.
Prototype, run: a `built` map checked at the top of `walk` and set before the children; `yamlio.test.ts` 33 pass, and the nine levels finish in 3 ms, with `a: &x [*x]` giving the recursive list Python gives.
Add a test with the nine-level header and a time-bounded expectation.

### C-2 · Important · syntax that PyYAML refuses is read, and syntax it reads is refused

Handle: `ts/src/core/yamlio.ts:80-84` (the `yaml` package's YAML 1.2 parser); d-bkc7md's title and Review Focus item 3 ("every refusal PyYAML makes is a `YamlError` with its line").
Run on the corpus, TypeScript reads what Python refuses: `scope:\tproduct` (Python: `found character '\t' that cannot start any token`), a tab on a line of its own after a mapping, `: v` and `{: v}` (an empty key), and anchors named `a.b` or `a/b` (Python: `expected alphabetic or numeric character`); `a: \x85b` gives `{a: "b"}` where Python fails at line 3.
TypeScript refuses what Python reads: U+0085, U+2028, and U+2029 as line breaks (`a: b\x85c: d` is two keys in Python), a lone CR as a line end (`a: b\rc: d\r`), a double-quoted scalar continued at column 0 (`a: "b\nc"`), and a flow sequence continued at column 0 (`a: [b,\nc]`).
Scenario: a draft with a tab after `scope:` is accepted by the server and refused by lodge 0.2, so Task 12's differential dump disagrees on it, and a record file of lodge 0.2 whose header holds a multi-line quoted value written by hand fails to import.
The brief's enumerated refusals all hold, so this is the plan's claim against its chosen parser rather than the builder's slip.
Fix: a ruling for the coordinator, either narrowing d-bkc7md to the enumerated refusals and listing these as known differences in the report and the decision, or adding pre-checks for the cheap ones (a tab where PyYAML's scanner refuses one, the anchor alphabet `[0-9A-Za-z_-]`, an empty implicit key); in both cases a test pins each chosen behaviour.

### C-3 · Important · the unreadable-character message is not lodge 0.2's

Handle: `ts/src/core/yamlio.ts:55`; the brief's `loadYaml` bullet; `src/lodge/core/yamlio.py:64-66`.
PyYAML's `ReaderError.character` is `ord` of the character, so lodge 0.2 says `unreadable character 1`, and `load_header` makes it `the header is not valid YAML: unreadable character 1` (run: `uv run --frozen python -c` over `a: b\nc: \x01\n`).
TypeScript says `unreadable character '\x01'`, as the brief asks; the brief misreads `{error.character!r}` as the repr of a `str`.
No Python test pins the message, so nothing catches it before Task 12.
Fix: `unreadable character ${cp}` with the decimal code point, after a coordinator ruling that corrects the brief, since this conflicts with it.

### C-4 · Important · package messages carry a second, contradicting line number and the header's text

Handle: `ts/src/core/yamlio.ts:80-84` and `:137`.
The `yaml` package's default `prettyErrors` appends `at line N, column M:` and a source excerpt with a caret, so `a: b\n  c: d` gives `Nested mappings are not allowed in compact mappings at line 1, column 4:\n\na: b\n   ^\n`.
Scenario: `load_header` (Task 5a's port of `src/lodge/core/document.py:36-37`) adds one to `line` for the file, so the problem reads `line 2` while its message says `line 1`, and a one-line problem becomes four lines holding header text.
Fix: `prettyErrors: false` in the options, which gives the bare `Nested mappings are not allowed in compact mappings` (run under Bun 1.3.14), the line still coming from `error.pos`.

### C-5 · Important · a construction error is reported before an earlier parse error

Handle: `ts/src/core/yamlio.ts:82` and `:134-137`.
PyYAML composes the whole document before constructing it, so a syntax error anywhere wins over a tag, duplicate, or key error.
Run: `a: !!int 5\nb: [\n` gives Python `expected the node content, but found '<stream end>'` at line 3 and TypeScript `unsupported tag` at line 1; likewise `a: b\na: c\nd: [\n` (line 4 against 2) and `[a]: b\nc: [\n` (line 3 against 1).
The order exists only for `uniqueKeys: true`, which is redundant: with `uniqueKeys: false` the walk's own check at `:128-129` still kills `duplicate_key_is_an_error_naming_it` (mutation run, test green).
Fix: `uniqueKeys: false`, and throw `doc.errors[0]` before walking; prototype run, `yamlio.test.ts` 33 pass and the three texts above give Python's lines.
The comment at `:134` goes with it.

### C-6 · Important · the environment reaches `core` through the `yaml` package and writes header text to standard output

Handle: `ts/node_modules/yaml/dist/parse/parser.js:178` and `compose/composer.js:139`; the brief's "nothing reaches `console`"; Review Focus item 5.
Run: `LOG_TOKENS=1 LOG_STREAM=1 bun -e 'import {loadYaml} from "./src/core/index.ts"; loadYaml("title: secret\n")'` prints every token, `"secret"` among them.
Scenario: a server started with either variable set logs every header it reads, decisions' text included, which the structure test cannot see since it scans `ts/src` only.
Fix: a ruling recording the exception, with the server's entry point (Plan 3) deleting `LOG_TOKENS` and `LOG_STREAM` from its environment before serving, and a test there; no option of the package turns the reads off.

### C-7 · Minor · an undefined alias is misnamed

Handle: `ts/src/core/yamlio.ts:100` and `:119-126`.
Run: `*x: y` gives Python `found undefined alias 'x'` and TypeScript `found unhashable key`; `a: *x` gives TypeScript `found undefined alias` without the name.
Fix: check `pair.key` for an unresolved alias before the scalar check, and name the alias as Python does, `found undefined alias ${pyRepr(node.source)}`.

### M-1 · Minor · `compare_orders_by_instant` never asserts a negative

Handle: `ts/tests/core/stamps.test.ts:27-32`.
Mutation run: `compareStamps` returning `instant(a) > instant(b) ? 1 : 0` keeps the test green, and such a comparator sorts wrongly.
Fix: add the reversed pair with `toBeLessThan(0)`.

### M-2 · Minor · `day_must_be_real` does not pin the century rule

Handle: `ts/tests/core/stamps.test.ts:33-37`.
Mutation run: every fourth year a leap year (`y % 100 !== 0 || y % 400 === 0` replaced by `true`) keeps the test green.
Fix: add `1900-02-29` false and `2000-02-29` true.

## Practice

### P-1 · Minor · the whitespace set is written twice and its expressions compiled on every call

Handle: `ts/src/core/text.ts:26-27` against `:28-40`, and `:42`, `:45`, `:49`, `:61`.
`PY_SPACE_CLASS` and `isPySpace` each spell the same 29 code points, tied only by the exhaustive test; `strip`, `rstrip`, and `splitWords` build a `RegExp` per call, and `isPySpace` and `splitLines` allocate an array literal per character.
Scenario: Task 5a's port of `src/lodge/core/document.py:44` and `:59`, which calls `rstrip` on every line of a body, compiles one expression per line.
Fix: module constants `SPACE = new RegExp(PY_SPACE_CLASS, "u")`, `EDGES`, `TRAILING`, and `RUN`, with `isPySpace` as `SPACE.test` on the first code point and the line-break code points in a `ReadonlySet`.

### P-2 · Minor · the identifier alphabet is spelled twice

Handle: `ts/src/core/ids.ts:3` and `:5`.
Python builds `_ID` from `ALPHABET` and `ID_LENGTH` (`src/lodge/core/ids.py:7-8`); the port repeats the 32 characters in the literal, so an edit to one leaves `isId` and `mintId` disagreeing with nothing failing until the shape tests do.
Fix: `const ID = new RegExp(\`^[dsq]-[${ALPHABET}]{6}$\`, "u")` at module level.

### P-3 · Minor · each default-filling function lists its defaulted fields twice

Handle: `ts/src/core/model.ts:42-75`, `:102-105`, `:122-124`, `:138-140`, `:157`.
`decision` names the same twelve fields in `Omit` and in `Pick`; adding a defaulted field means editing both lists and the body.
Fix: one helper type, `type WithDefaults<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>`, used by all five.

### P-4 · Minor · the report says no uncertainty remains

Handle: `task-4-report.md`, "TypeScript differences and concerns", last line.
C-2 to C-6 are differences the report does not list; the report also attributes the three Unicode counts to the probes without checking them, which this review did and found exact.
Fix: the fix round's report lists the rulings' outcomes for C-2, C-3, and C-6 as known differences.

## Design

### What holds

The front door exports what the brief lists and keeps `LINE_BREAKS_AND_TABS`, `quoted`, and `unreadableChar` behind it, with `src/core/yamlio.ts` in knip's `entry` until Task 5a; `yaml` left `ignoreDependencies`.
The alias-key pre-pass at `ts/src/core/yamlio.ts:59-76` preserves the text apart from the intended space: over the corpus and eight alias texts only the six `*name:` texts changed, and an error after a rewritten key keeps Python's line (`a: &k v\n*k: x\nb: [\n`, line 4 in both).
Imports in `core` stay within `core` and `yaml`.

### D-1 · Important · `instant` cannot order the bare days lodge 0.2 orders

Handle: `ts/src/core/stamps.ts:24-25`; `src/lodge/core/derive.py:101-102` (`order_key`), `src/lodge/core/search.py:115-116` (`_when`), and `src/lodge/core/check_change.py:71` and `:88`.
Python orders decisions by `datetime.fromisoformat(d.date)`, and an imported decision may carry a bare day (`fields.py:128-129`); bare days compare among themselves as naive datetimes, while a bare day against a stamp raises `TypeError` (run: `sorted` of one of each, `can't compare offset-naive and offset-aware datetimes`).
`instant` throws a `ValueError` on any day, so when Task 7a ports `order_key` on `compareStamps`, a store whose imported decisions all carry days orders in lodge 0.2 and throws in TypeScript, and Plan 4's importer is the path that brings such stores in.
This is a gap in the plan's interface, not a slip of the builder, who followed the brief.
Fix: a ruling before Task 7a on how a day orders (Python's naive midnight among days, and what replaces the `TypeError` against a stamp), then `stamps.ts` gains that function with tests.

### D-2 · Minor · settings report a different first unknown key for integer-like keys

Handle: `ts/src/core/settings.ts:83` and `:94`.
`parseCoreSettings` takes a plain object, whose integer-like keys come first, where `loadYaml` returns a `Map` for exactly this reason.
Run: `zz = 1\n"1" = 2` gives Python `unknown key zz` and TypeScript `unknown key 1`; `[length]\nfoo = 1\n"7" = 2` gives `length.foo` against `length.7`.
Fix: list it as a known difference, or have Plan 3's TOML reader hand `core` a `ReadonlyMap` in the file's order.

## Counts

Blocking 1 (C-1), Important 6 (C-2, C-3, C-4, C-5, C-6, D-1), Minor 8 (C-7, M-1, M-2, P-1, P-2, P-3, P-4, D-2).
C-2, C-3, C-6, and D-1 conflict with the brief or the plan and need a coordinator ruling before a fix round; C-1, C-4, C-5, C-7, M-1, M-2, and P-1 to P-3 are fixes in Task 4's files.

## Files

Read: `CLAUDE.md`; `task-4-brief.md`, `task-4-report.md`, and `task-4-codex-final.txt`; the plan's Review Focus (`2026-11-02-lodge-server-core.md:94-102`) and its Plan 3 paragraph; `probes.md` items 7 and 12 to 27; d-bkc7md through `lodge show`; every file of the diff under `ts/` (`errors.ts`, `ids.ts`, `index.ts`, `model.ts`, `settings.ts`, `stamps.ts`, `text.ts`, `yamlio.ts`, the five test files, `knip.json`, the `parity.json` hunks); `src/lodge/core/model.py`, `ids.py`, `settings.py`, `yamlio.py`, `fields.py:1-30` and `:121-163`, `document.py:25-60`, `check_change.py:60-92`, `derive.py:95-105`, `search.py:110-118`; `tests/core/test_ids.py`, `test_settings.py`, `test_yamlio.py`; `ts/tests/structure/calls.ts` by grep; `ts/node_modules/yaml/dist` by grep.
Not read: `task-3-review.md` (not this task), the rest of the plan's task sections, `ts/tests/parity.test.ts` and the other structure files, `ts/tsconfig.json` beyond its strictness flags, and the probe sources under `probes/`.
