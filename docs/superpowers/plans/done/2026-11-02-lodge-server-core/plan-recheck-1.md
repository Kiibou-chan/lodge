# Plan recheck 1: lodge server core

Fix diff: `git diff ad1b09a 5838e7a` on branch `server-core`.
Findings: `plan-review-correctness.md` (I-1 to I-7, M-1 to M-13) and `plan-review-practice.md` (P-I1 to P-I11, P-M1 to P-M9).
Rechecker: `rechecker` agent, 2026-11-02.
Status: done.

## Probes rerun

Run in a scratch worktree of my own at `5838e7a`, with Task 2's files written as the plan gives them (`package.json` verbatim, then `bun install` and `bun x biome format --write .`), Bun 1.3.14.

- Task 2's gate: `bun --bun run check` passes Biome, `tsc`, dependency-cruiser, knip, and `bun test` (`1 pass, 0 fail`), knip printing only configuration hints (`scripts/*.ts` has no match yet), exit 0.
- Under the sandbox's limits: `sh scripts/check-ts.sh` exits 0 with `HOME`, `XDG_CACHE_HOME`, and `TMPDIR` on a folder with mode 555, and exits 0 again under `unshare -rn` (no network); `PATH=/usr/bin:/bin sh scripts/check-ts.sh` prints `bun is not installed` and exits 2.
- knip and the two dependencies: with `yaml` imported and still in `ignoreDependencies`, knip prints the hint `yaml knip.json Remove from ignoreDependencies` and exits 0, so a task that forgets to take the name out stays green; Tasks 4 and 5a's steps take it out, and the hint does not fail the gate.
- knip and a later reader: an export of `src/core/document.ts` read only inside its own file makes knip print `Unused exports (1) splitDocument` and exit 1; an export of a test helper (`NOTES`) read by no test of the task makes knip exit 1 the same way (see N1).
- `test.each`: `test.each(cases.map((c) => [c]))("sources %p", (value) => …)` over `["docs/a.md", [1], [""], 7]` hands the test `"docs/a.md"`, `[1]`, `[""]`, and `7`, and `test.each([["a", 1], ["b", 2]])` hands `["a",1]` and `["b",2]`; `tsc --noEmit` passes both.
- `plant`: a tree under the system's temporary folder with a symbolic link `node_modules` to `ts/node_modules`, cruised in process with `baseDir` set to the tree and the working folder unchanged, resolves `yaml` and `@noble/hashes/sha2.js` (no `not-to-unresolvable`), reports `fs` as type `core`, and reports an absent package as `not-to-unresolvable`; `process.chdir` changes nothing.
  Two details the plan does not give (m2): the npm imports resolve to the link's real path outside the tree (`preserveSymlinks: true` gives `node_modules/yaml/dist/index.js`), and their dependency type is `npm-no-pkg`, since the planted `package.json` lists no dependencies.
- lodge 0.2's thread writer (Task 6's new test): `write_thread` of a message `x` U+2028 `## Message 1` and of `y` CR `## Message 2` adds no backslash, and `parse_thread` reads each back unchanged, while `z` LF `## Message 1` is escaped and read back unchanged, so the test's expectation is lodge 0.2's.
- Biome: `"recommended": true` draws `DEPRECATED … Use preset instead` as an info, exit 0, so the notice does reproduce, against the M-8 row of `plan-fix-1.md`, but it does not fail the gate.

## Findings of the reviews

Plan line numbers are those at `5838e7a`.

### Correctness

| Finding | Verdict | Handle |
|---|---|---|
| I-1 `test.each` unwraps list cases | Closed | Plan line 29 and Review Focus 1 (line 75); probe above. |
| I-2 text operations, `repr`, `re.MULTILINE` | Closed, with one new contradiction (N3) | Lines 37 to 40, 414 to 432, 444, 465, 508, 567, 644, 647; `py_repr_matches_python`'s U+200B case contradicts line 432 (N3); `isDigit`'s 90 extra characters are not listed (m1). |
| I-3 collection keys and key order | Closed | Line 436 and 437, tests line 446, d-bkc7md (`lodge show d-bkc7md`), d-458jhp `replaced by d-bkc7md`. |
| I-4 knip on `yaml` and `@noble/hashes` | Closed | Line 317, Task 4 lines 402 and 448, Task 5a lines 457 and 470; Task 2's gate run green above. |
| I-5 structure rows' status | Closed | Lines 231 to 238 (files named one by one), 383, 384, 391; every named file is in Task 3's Create list (line 338) or is `ts/.dependency-cruiser.cjs`; the 40 core rows are flipped once each across Tasks 4 to 11 (3, 3, 2, 2, 4, 2, 1, 5, 2, 6, 2, 5, 3). |
| I-6 `ValueError` class | Closed | Lines 34 and 35, 401, 411 and 412, 466, 547, 687; `class FormatError(Exception)` is at `src/lodge/core/fields.py:18`, as line 462 says. |
| I-7 local time zone | Closed | Lines 41, 376, 377, 388, 434, 445; Review Focus 4 and 5. |
| M-1 nesting bound | Closed | Line 438, test line 446, d-bkc7md. |
| M-2 offsets | Closed | Line 433, test line 445. |
| M-3 two signatures | Closed | Line 587 against `src/lodge/core/check_change.py:21-27`; line 686 against `src/lodge/core/apply.py:41-48`. |
| M-4 knip and the front doors | Closed by d-s2rdn2, but the new test conflicts with Task 4 (N2) | Line 44, line 688, d-s2rdn2. |
| M-5 rule scope and `node:` | Closed | Lines 363 and 364, test `tests_and_scripts_may_use_files` (line 387), d-x6f9za. |
| M-6 `plant` without `node_modules` | Closed | Lines 360 and 361; probe above (m2 for two details). |
| M-7 control characters in regular expressions | Closed | Lines 40 and 437; one gap for `\s` (m3). |
| M-8 `package.json` and Biome | Closed | Line 330; gate green after `bun x biome format --write .` above. |
| M-9 TOML floats | Closed | Lines 94, 440, 713; `tests/core/test_settings.py` holds no float case. |
| M-10 Task 12's counts | Closed | Line 720. |
| M-11 Task 1's verify | Closed | Line 281. |
| M-12 authenticator and strict `tsc` | Closed | Line 113. |
| M-13 the tag `!` | Closed | Line 437, test line 446, d-bkc7md. |

### Practice

| Finding | Verdict | Handle |
|---|---|---|
| P-I1 `plant` and `node_modules` | Closed | As M-6. |
| P-I2 where the rules bind | Closed | Lines 42 and 363, d-x6f9za. |
| P-I3 allowed cases for confined I/O | Closed | `confined_io_is_allowed_where_ruled` (line 387) and `confined_calls_are_allowed_where_ruled` (line 388). |
| P-I4 structure rows | Closed | As I-5. |
| P-I5 knip and entry exports | Closed for the front doors; the `treeOf` case it raised is a non-entry export, which knip checks with the option off too, and is folded into N1 | Line 44, d-s2rdn2; probe above. |
| P-I6 `ValueError` and `LookupError` | Closed | As I-6. |
| P-I7 `repr` | Closed, with N3 | As I-2. |
| P-I8 `re.MULTILINE` | Closed | Line 39, Tasks 6 (lines 507 and 508) and 9b (lines 645 and 647), Review Focus 2. |
| P-I9 task sizes | Closed as to size and order; the split introduced N1 | d-mfayy5; lines 452 to 653; import order checked below. |
| P-I10 the writers in the differential run | Closed | Line 711, Review Focus 7, d-0qmd10. |
| P-I11 no page for passkeys | Closed | Lines 93, 95, 115, d-jtxwg3; one permission detail for plan 3 (m7). |
| P-M1 the brief's folder | Answered differently but adequately | `planner-brief.md` no longer names it; the review itself still quotes it as its handle (`plan-review-practice.md:103`), which names no person or machine. |
| P-M2 counts | Closed | As M-10. |
| P-M3 Node runs the gate's tools | Closed | Line 326, d-xph4ac; gate run under `bun --bun` above. |
| P-M4 authenticator | Closed | As M-12. |
| P-M5 nesting | Closed | As M-1. |
| P-M6 TOML floats | Closed | As M-9. |
| P-M7 Task 1's `where` | Closed | Line 265. |
| P-M8 d-k5swcq and the author's call | Answered differently but adequately | d-x6f9za maps each adapter to the lodge 0.2 package whose permissions it keeps, which matches `tests/structure_imports.py` (`_outside_edge`: spawning and writing in `gitstore` only, reading in `gitstore` and `cli`); `store`'s one new edge, `bun:sqlite`, rests on her ARCH-3 answer (line 272). |
| P-M9 Review Focus on the gate | Closed | Review Focus 6 (line 80), test `a_ported_file_losing_a_name_fails` (line 391). |

## New problems the fix introduced

### N1 (Important): the splits leave exports whose first reader is the next task, which knip refuses, and the next task may not add them

Handles: line 44 ("every export of a module is read by another module or by a test in the task that adds it"); line 526 (Task 7a: `orderKey`, "which Task 7b's `confirmation.ts` imports"); line 565 (Task 8a: `newDecisions` and `problemAt`, "which Task 8b imports"); line 561 (Task 8a's `checks.ts` holds "all of `checks.py` but `check` and `verdict`"); line 462 (Task 5a: "the readers of `fields.py`"); the Modify lists of Tasks 5b (line 479), 7b (line 541), 8b (line 581), and 8c (line 599).
Evidence: the import names of `src/lodge/core/*.py` (an AST-free scan of the `from lodge.core.X import …` lines) give these names, each outside `__all__`, read by no module of the task that ports them:
- Task 5a to 5b: `document.split_document`, `document.problem_for`, `document.load_header`, `headers.AREA_KEYS`, `headers.DECISION_KEYS`, and `headers.SPEC_KEYS`, read only by `drafts.py`;
- Task 7a to 7b: `derive.order_key`, read only by `confirmation.py` (7b) and `views.py` (9a);
- Task 8a to 8b: `check_state.new_decisions`, `problem_at`, and `sort_key` (the last missing from line 565), read only by `check_entries.py`, `check_immutable.py`, and `check_change.py`.
And of `tests/core/checks.py`'s names, Task 8a's one test file reads only `REMEDY_ATTACH` and `REMEDY_CHECK_3` (`from checks import REMEDY_ATTACH, REMEDY_CHECK_3` in `test_check_state.py`); `NOW`, `SETTINGS`, `LATER`, `NOTES`, `OLD`, `SPEC`, `Item`, `creates`, `published`, `state`, `old_decision`, `REMEDY_CHECK_5`, and `REMEDY_CHECK_5_REASONING` are first read in 8b, and `REMEDY_CHECK_4` only in 8c.
Probe: knip 6.42.0 with Task 2's `knip.json` exits 1 on `Unused exports (1) splitDocument` when the export is read only inside its own file, and on an unread export of a test helper.
Failure: Tasks 5a, 7a, 8a, and 8b each port what their text tells them to and meet a red gate on knip; the builder can drop the `export` keyword, but the next task cannot put it back, since `derive.ts`, `check-state.ts`, `document.ts`, `headers.ts`, and (in 8c) `checks.ts` are not in its Modify list, so it stops BLOCKED, edits a file outside its list, or adds the names to `ignore` in `knip.json`.
These instances are new with the splits; the same mechanism already held at the old boundaries and is worth fixing in the same edit: `yamlio.LINE_BREAKS_AND_TABS` (Task 4, first read in 5a), `document.key_line`, `document.load_header`, and `fields.read_stamp` (5a, first read in 6), and `builders.tree_of` (6, first read in 11, as `plan-review-practice.md` P-I5 noted).
Fix: one Global Constraint: "a name that no module or test of the task reads is not exported yet; the task that first reads it adds the `export`, and lists that file under Modify"; then add the files to the Modify lists (`document.ts` and `headers.ts` to 5b; `derive.ts` to 7b; `check-state.ts` to 8b; `checks.ts` to 8c; `yamlio.ts` to 5a; `document.ts` and `fields.ts` to 6; `builders.ts` to 11), name `sortKey` at line 565, and reword line 561 to "the names of `checks.py` that `test_check_state.py` reads, the rest added by 8b and 8c".

### N2 (Important): Task 11's `front_door_exports_nothing_else` refuses names Task 4 exports through `#core`

Handles: line 688 (`front_door_exports_nothing_else` "finds every other exported name in `errors.ts`, `text.ts`, or `stamps.ts`"); line 408 (Task 4 exports through `#core` the model types "and their default-filling functions", and `quoted` and `unreadableChar`); line 33 (a default-filling function has the class's name in camelCase, `decision({…})`).
Evidence: `src/lodge/core/__init__.py`'s `__all__` (91 names) holds neither `quoted` nor `unreadable_char`, and the dataclasses with defaults in `src/lodge/core/model.py` are `Decision`, `SpecEntry`, `Area`, `Problem`, and `Message`, so `#core` exports `decision`, `specEntry`, `area`, `problem`, `message`, `quoted`, and `unreadableChar`, none in `__all__` and none defined in the three files the test allows.
Failure: Task 11's new test fails on seven names that every later module and test relies on; the builder either drops the default-filling functions from `#core` (breaking the carried tests that build records) or widens the test on its own judgement, which is the ruling d-s2rdn2 was meant to settle.
Fix: line 688 allows also the default-filling function of each dataclass in `__all__` (its PascalCase name with a lower-case first letter, defined in `model.ts`); and Task 11 takes `quoted` and `unreadableChar` out of `index.ts` (by then `fields.ts`, `fileformat.ts`, `threads.ts`, and `confirmation.ts` import them inside the package), or line 408 stops exporting them through `#core` once N1's rule lets them wait for 5a.

### N3 (Important): `py_repr_matches_python` expects U+200B unescaped, against line 432 and Python

Handles: line 444 (`U+200B to` followed by a quote, the raw character U+200B, and a quote: bytes `' 342 200 213 '` by `od -c`); line 432 (`pyRepr` escapes every character of category `Cf`, which U+200B is).
Evidence: `python3 -c "print(repr('​'))"` prints `'​'`.
Failure: the builder writes the test first with the expectation the plan prints, the implementation of line 432 fails it, and the builder either changes the test to Python's value (fine but unguided) or keeps it and leaves `Cf` characters unescaped, so every `unreadable character …` message and every `!r` of a text holding a format character differs from lodge 0.2, the divergence I-2 and P-I7 were raised for.
Fix: line 444 reads "U+200B to `'​'`" (backslash, `u200b`, as six ASCII characters).

## Minor

- m1: `isDigit` is "`\p{Nd}` or one of the 20 ranges" (line 419), and probe 16 says `/\p{Nd}/u` takes 90 characters Python's `isdecimal` refuses; lines 431 and 432 have the report list `casefold`'s and `pyRepr`'s known differences, but nothing lists these 90. Fix: the same sentence for `isDigit`.
- m2: `plant` (line 360) leaves two choices open, seen in the probe above: npm imports resolve through the link to its real path outside the tree, and are of type `npm-no-pkg`; a `core-imports` rule keyed on `npm` or on `^node_modules/` passes the planted tests or the repository, not both. Fix: `cruise` sets `preserveSymlinks: true`, and the planted `package.json` copies `ts/package.json`'s `dependencies`, or the rules match by module name.
- m3: line 38 says `\s` becomes "Python's whitespace set from `text.ts`", but `text.ts` (lines 414 to 424) exports `isPySpace` and no class string, and the one `\s` in the core is in `src/lodge/core/feedback.py:20` (`(?:\s?%)?`, Task 10), whose control-character escapes Biome refuses in a literal (line 40). Fix: `text.ts` exports `PY_SPACE_CLASS` built from code points with `String.fromCodePoint`, used through `new RegExp`, or Task 10 says how `\s?` is matched.
- m4: the characters of line 437's set (`\xA0` to U+D7FF, U+E000 to U+FFFD) and some inputs of line 444 (U+FEFF, U+2028) are written as the raw characters, U+E000 and U+FEFF invisible on screen; write them as `\uXXXX` like the rest.
- m5: the M-8 row of `plan-fix-1.md` says the `recommended` deprecation notice did not reproduce; it does, as an info with exit 0 (probe above), so nothing in the plan needs to change.
- m6: under d-x6f9za `api` has sockets and no file reading (line 379: `Bun.file` in `git` and `cli` only), while lodge 0.2's viewer may read its package data (`tests/structure_imports.py`, `importlib.resources outside cli and viewer`); plan 3's page (d-jtxwg3) then has to be imported as text rather than read at run time, which plan 3's paragraph could say.

## Preflight

Each pair of tasks that share a file or an interface: what the earlier produces against what the later consumes.
Module order was checked from the `from lodge.core.X import` lines of all 27 core modules, and test order from the `from lodge.core import` and helper imports of all 40 files of `tests/core`, against each task's Produces.

| Pair | Shared file or interface | Produced | Consumed | Found |
|---|---|---|---|---|
| 1 and 12 | the store's decision count | eight author decisions | the counts the run prints | Agrees (line 720 adds Task 1's eight). |
| 2 and 3 | `ts/.dependency-cruiser.cjs`, `ts/package.json`, `scripts/check-ts.sh` | two rules, `#core`, the gate | the full table, the gate | Agrees; Task 3's Modify of `package.json` ("no new dependency", line 337) has no stated purpose, harmless. |
| 2 and 4 | `ts/src/core/index.ts`, `toolchain.test.ts`, `ts/knip.json` | placeholder, its test, `ignoreDependencies` `yaml` | removal of both, `yaml` taken out | Agrees (lines 319, 402, 403, 448). |
| 2 and 5a | `ts/knip.json` | `@noble/hashes` in `ignoreDependencies` | taken out with `contentHash` | Agrees (`content_hash` is in `fileformat.py:93`, which 5a ports). |
| 2 and 12 | knip's `scripts` patterns, `depcruise src tests` | hints until a script exists | `scripts` added to the cruise | Agrees; the hints exit 0 (probe). |
| 3 and 4 to 11 | `ts/tests/parity.json`, the rules | statuses, `CORE_NPM`, the call checks | each task flips its rows; `core` imports `yaml` and `@noble/hashes` | Agrees: 40 rows flipped once each, and no plan 1 row stays `planned` at Task 11's Step 4. |
| 3 and 11 | the front-door rule, `front-door.test.ts` | `front-door` binds tests | Task 11's test reads `index.ts` and `__init__.py` as text | Agrees (no import past the front door). |
| 4 and 5a | `errors.ts`, `text.ts`, `stamps.ts`, `yamlio.ts` | `ValueError`, `rstrip`, `pyRepr`, `isStamp`, `quoted`, `unreadableChar`, `loadYaml`'s `Map`s | `writeRecord`'s `ValueError`, `document.py`'s `rstrip`, `read_stamp`, the readers on `Map`s | Agrees on names; `LINE_BREAKS_AND_TABS` is first read in 5a (N1, old boundary). |
| 4 and 11 | `#core`'s exports | default-filling functions, `quoted`, `unreadableChar` | `front_door_exports_nothing_else` | **Mismatch** (N2). |
| 5a and 5b | `document.ts`, `headers.ts`, `fields.ts` | `parseRecord`, `writeRecord`, the readers | `drafts.py`'s `split_document`, `problem_for`, `load_header`, `*_KEYS`; mutations for `fileformat-text` | **Mismatch** (N1): the six names have no reader in 5a, and 5b may modify 5a's modules only "where a carried test finds them wrong". |
| 5a/5b and 6 | `document.ts`, `fields.ts`, `samples.ts` | as above | `threads.py`'s `key_line`, `load_header`, `read_stamp` | Same mechanism as N1, at a boundary the fix did not move. |
| 6 and 7a to 11 | `builders.ts`, `Tree`, `load`, `Snapshot` | `builders.ts` from `builders.py` | every later test file | Agrees, except `treeOf`, first read by `applying.ts` in 11 (N1, old boundary). |
| 6 and 9a, 6 and 10 | `snapshot.test.ts`, `thread-files.test.ts` | one `test.todo` each | 9a and 10 turn them into tests and flip the rows | Agrees (`duplicate_id_marks_kept_record_failing` needs `failing_ids`, `thread_id_is_not_number_feedback` needs `feedback`). |
| 7a and 7b | `derive.ts` | `derive`, `isAuthor`, `orderKey` | `confirmation.py`'s `order_key` | **Mismatch** (N1): `orderKey` has no reader in 7a, and 7b's Modify list lacks `derive.ts`. |
| 7a and 9a | `doubts.test.ts` | two `test.todo`s | 9a turns them into tests (they need `level1`) | Agrees. |
| 5b and 7b | `parseDraft`, `recordFromDraft`, `Draft` | 5b's Produces | `test_confirmation.py` | Agrees. |
| 8a and 8b | `check-state.ts`, `checks.ts` | `checkState`, `CheckResult`, `newDecisions`, `problemAt`; `checks.ts` without `check` and `verdict` | `check_entries.py`, `check_immutable.py`, `check_change.py` (also `sort_key`); 8b's tests' helper names | **Mismatch** (N1): the three names and most of `checks.ts` have no reader in 8a; `sortKey` is not named; 8b's Modify list lacks `check-state.ts`. |
| 8b and 8c | `checks.ts`, `checkChange` | `check`, `verdict` added | `REMEDY_CHECK_4` in `test_check_compare.py`; mutations of 8a's and 8b's code | **Mismatch** (N1): `REMEDY_CHECK_4` has no reader in 8b, and 8c may not add it. |
| 8c and 9a | `check-threads.test.ts` | one `test.todo` | 9a turns it into a test (`unrecorded_problems`) and flips the row | Agrees. |
| 8a/8b and 9a, 9b | `checks.ts`'s `NOTES` | `NOTES` | `test_views.py`, `test_views_trust.py`, `test_render.py` | Agrees once N1 is fixed. |
| 9a and 9b | `views.ts` | `level1`, `level3`, and the rest | `render.py` and `search.py` import `views` | Agrees. |
| 9b and 10 | `search.ts` | `search`, `related` | `feedback.py` imports `search` | Agrees; `\s` in `feedback.py:20` has no helper (m3). |
| 10 and 11 | `feedback.ts`, `index.ts` | `Feedback`, `feedback`, `areaFeedback` | Task 11's front-door test | Agrees apart from N2. |
| 11 and 12 | `#core` | every `__all__` name | `differential.ts` through `#core` | Agrees: Task 12's keys use `renderSpec`, `checkState`, `level1`, `level2`, `level3`, `formatLevel1`, `formatLevel3`, `search`, `parseRecord`, `parseArea`, `writeRecord`, `writeArea`, all in the Produces lists. |

Each task against itself:

| Task | Agrees with itself | Found |
|---|---|---|
| 1 | Yes | Steps match the table and the verify of line 281. |
| 2 | Yes | Built as written, the gate is green (probe). |
| 3 | Yes, with m2 | Rules, tests, and parity schema agree; `plant`'s link and dependency types are left to the builder. |
| 4 | **No** | `py_repr_matches_python`'s U+200B case against line 432 (N3); `isDigit`'s known difference unlisted (m1). |
| 5a | **No** | Produces "the readers of `fields.py`" and ports `document.py` and `headers.py` whole, while line 44 forbids exports no 5a module or test reads (N1). |
| 5b | Yes | Test-first by missing module for `drafts`, by named mutation for `fileformat-text`. |
| 6 | Yes | The new test's expectation is lodge 0.2's (probe). |
| 7a | **No** | Produces `orderKey` for 7b, against line 44 (N1). |
| 7b | Yes, given N1 | Its Modify list would need `derive.ts` under N1's fix. |
| 8a | **No** | `checks.ts` "all of `checks.py` but `check` and `verdict`" and `newDecisions` and `problemAt` against line 44 (N1). |
| 8b | **No** | `checks.ts` keeps `REMEDY_CHECK_4` for 8c (N1). |
| 8c | Yes, given N1 | Mutation-first, no new names. |
| 9a | Yes | Four `test.todo`s, all needing `views.py` names. |
| 9b | Yes | |
| 10 | Yes, with m3 | |
| 11 | **No** | Its new test against the names Task 4 and line 33 export through `#core` (N2). |
| 12 | Yes | |

## Read and not read

Read: `CLAUDE.md`; both reviews; `plan-fix-1.md`; `plan-fix-1-report.md`; `probes.md`; the plan at `5838e7a` in full; the ledger's diff; the seven rulings through `lodge show`, and the status lines of d-458jhp, d-03xx0a, d-g3mbmc, d-4psbdv, and d-k5swcq; the import lines of every core module and core test; `src/lodge/core/yamlio.py` (lines 1 to 20 and 55 to 70), `apply.py:41-48`, `check_change.py:21-27`, the `casefold` lines of `check_state.py`, the `FormatError` and `content_hash` sites, `model.py`'s dataclasses; `tests/core/checks.py`'s names and `builders.py`'s `thread` and `message`; `tests/structure_imports.py:85-140` and `tests/structure_calls.py:100-145`.
Not read: `lodge spec` in full; the design beyond what the plan cites; the probe sources of `probes/fix1/` (their results taken from `probes.md`, apart from the U+200B case checked directly); the casefold, lower, repr, and offset probes were not rerun.

## Counts

Findings of the reviews: 40 (20 correctness, 20 practice); closed 38, answered differently but adequately 2 (P-M1, P-M8), open 0.
New: Blocking 0, Important 3 (N1, N2, N3), Minor 6.
Preflight: mismatches between 5a and 5b, 7a and 7b, 8a and 8b, 8b and 8c (N1), and 4 and 11 (N2); Tasks 4, 5a, 7a, 8a, 8b, and 11 disagree with themselves.

