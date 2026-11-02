# Plan fix round 1: lodge server core

Answers `plan-review-correctness.md` (0 Blocking, 7 Important, 13 Minor) and `plan-review-practice.md` (0 Blocking, 11 Important, 9 Minor) of the plan at `c3320a4`.
Line numbers are those of the plan after this round.
New probes are items 15 to 20 of `probes.md`, their sources in `probes/fix1/`.
Rulings made in this round, scope `process`, work item the plan: d-bkc7md (replaces d-458jhp), d-s2rdn2 (narrows d-4psbdv), d-x6f9za, d-mfayy5, d-jtxwg3, d-xph4ac (replaces d-03xx0a), and d-0qmd10 (replaces d-g3mbmc).

## Correctness

| Finding | What changed |
|---|---|
| I-1 `test.each` unwraps list cases | Line 29: one parameter is `test.each(cases.map((c) => [c]))`, several are `[[a, b], …]` (probe 15 confirms the wrapped form hands `[1]` whole); Review Focus 1 (line 75) names a list-valued case handed unwrapped. |
| I-2 text operations and `re.MULTILINE` | Line 37: `rstrip`, `isdigit`, `casefold`, and `repr`/`!r` (`pyRepr`) go through `text.ts`, and `lower()` is `toLowerCase()` (probe 17: 0 differences, final sigma too); line 39: `^` and `$` under `re.MULTILINE`, `$` outside it, and `.` with and without `DOTALL`; Task 4's interface (lines 413 to 432) adds `rstrip`, `isDigit` (the 128 digits of probe 16), `casefold` (`toUpperCase().toLowerCase()` with `ς` made `σ`, 174 known differences, none giving a letter of `author`, probe 16), and `pyRepr` (9,988 known differences, all characters Unicode 15.1 leaves unassigned, probe 18), with tests (line 444); Task 5a line 465 (`document.py`'s `rstrip`), Task 8a line 567 (`casefold`), Task 9b line 644 (`isdigit`); new tests `escape_breaks_lines_at_newline_only` (Task 6, line 508) and `heading_line_breaks_at_newline_only` (Task 9b, line 647); Review Focus 2 (line 76). |
| I-3 collection keys and key order | d-bkc7md replaces d-458jhp; line 436: `loadYaml` walks the nodes, never `toJS()`, gives a `Map` in the text's order, refuses a non-scalar key with `found unhashable key`, and writes nothing through `console`; Task 5a's readers read the `Map`s (line 462); tests `collection_key_is_refused` and `integer_like_keys_keep_their_order` (line 446). |
| I-4 knip fails on `yaml` and `@noble/hashes` | Line 317: Task 2's `knip.json` has `ignoreDependencies` `["yaml", "@noble/hashes"]`, named in the ledger line; Task 4 takes `yaml` out (lines 402, 448, and 449) and Task 5a `@noble/hashes` (lines 457, 470, and 471), each step checking that knip reports no unused dependency. |
| I-5 structure rows have no stated status | Line 383: the seven structure rows are `changed` from the start, with plan 1, task 3, their files, and their `why`; line 384 says why they are not carried test by test; the rows (lines 231 to 238) name their files one by one instead of a glob; line 391: `ported_files_exist` covers `changed` rows of plan 1, and the name and todo checks cover `ported` rows only; Task 11's "no plan 1 row is `planned`" then holds. |
| I-6 no `ValueError` class | Lines 34 and 35: `errors.ts` holds `ValueError` and `LookupError`; `YamlError` and `SettingsError` extend `ValueError`, `AmbiguousRef` `LookupError`, `FormatError` `Error`, as in Python; `except E` becomes a `catch` that rethrows anything else; Task 4 creates `errors.ts` (line 401); Tasks 5a (line 466), 7b, 9b, and 11 (line 687) use it. |
| I-7 local time zone in `stamps.ts` | Line 41: `core` never uses `Date`, and `stamps.ts` uses integer arithmetic alone, since `Date.UTC` also reads years 0 to 99 as 1900 to 1999 (checked: `Date.UTC(1, 0, 1)` prints 1901); line 376: `callViolations` flags `Intl`, `Date` with more than one argument, `getTimezoneOffset`, the local getters and setters, and the `toLocale…` and `to…String` calls in `core` and `app`, and line 377 any `Date` in `core`; tests `local_time_in_core_and_app`, `core_may_not_use_date`, and `app_may_parse_a_stamp` (line 388), and `stamp_check_ignores_the_local_time_zone` (line 445); Review Focus 4 and 5. |
| M-1 nesting bound | d-bkc7md: nesting beyond 100 gets Python's message `the header is nested too deeply` and no line, named as a narrowing of lodge 0.2 (line 438); test `nesting_beyond_the_bound_has_no_line` (line 446). |
| M-2 offsets | Line 433: `isStamp` takes what `datetime.fromisoformat` takes, year 0001 or later and hours × 60 + minutes below 1,440 (probe 19); test `offset_is_read_as_python_reads_it` and the year cases (line 445). |
| M-3 two signatures | Line 587: `checkChange(published, after, settings, now, current: Snapshot \| null = null)`; line 686: `applyDrafts(current, tree, drafts, newDecisionIds, date, importing)`, `date` as Python has it. |
| M-4 knip and the front doors | d-s2rdn2 (narrows d-4psbdv): front doors are exempt from knip in this plan and checked against `__all__` by Task 11's `front-door.test.ts` (line 688); the third plan turns on `includeEntryExports`; line 44. |
| M-5 rule scope and the `node:` prefix | d-x6f9za; line 363: every rule but `front-door`, `no-circular`, and `not-to-unresolvable` has `from: { path: "^src/" }`, and each built-in name matches with and without `node:`; test `tests_and_scripts_may_use_files` (line 387). |
| M-6 `plant` has no `node_modules` | Line 360: `plant` links `node_modules` to `ts/node_modules` and writes `ts/tsconfig.json`'s options; line 361: `cruise` runs with the planted root as `baseDir`. |
| M-7 Biome refuses control-character classes | Line 40: control-character sets are code-point checks, not regular expressions; line 436 says the same for `loadYaml`'s character check. |
| M-8 Task 2's `package.json` fails `biome check` | Line 330: Step 1 ends with `bun x biome format --write .`; the JSON is printed "before Biome formats it". The deprecation notice for `"recommended": true` did not reproduce: Biome 2.5.15 in the probe folder prints only lint findings with that setting. |
| M-9 `Bun.TOML.parse` and `5.0` | Plan 3's paragraph (line 94) says the third plan settles how the command refuses `80.0`; Task 12 (line 713) notes it, and that this repository's `.lodge.toml` has no `[length]`; line 440 says no carried settings case holds a float. |
| M-10 Task 12's counts | Line 720: the counts are reported as printed, the numbers at `c3320a4` given (192 and 137), and the store has no threads, so the thread code rests on the carried tests and Task 6's new test; d-0qmd10 carries the corrected counts. |
| M-11 Task 1's verify | Line 281: the eight are dated at the add, after the newest decision, and `lodge show <id> --provenance` gives each quote's minute. |
| M-12 the authenticator fails strict `tsc` | Line 113: as committed it fails with two `TS2345` errors (probe 20 reproduces them), and when carried its buffers are built as `new Uint8Array(new ArrayBuffer(n))`. |
| M-13 the tag `!` | d-bkc7md and line 436: `!` is allowed, and `!!str`, `!!seq`, and `!!map` only on the node kind they name; tests `non_specific_tag_is_text` and `str_tag_on_a_mapping_is_refused` (line 446). |

## Practice

| Finding | What changed |
|---|---|
| P-I1 `plant` and `node_modules` | As M-6 (lines 360 and 361). |
| P-I2 where the rules bind | As M-5; d-x6f9za; lines 42 and 363. |
| P-I3 no allowed case for confined I/O | Tests `confined_io_is_allowed_where_ruled` (imports, line 387) and `confined_calls_are_allowed_where_ruled` (calls, line 388); `file-confinement` now leaves out `store` (line 372, d-x6f9za), and `file_reading_outside_git_and_cli` and `file_writing_outside_git` refuse in `store` and `cli` (line 388). |
| P-I4 structure rows | As I-5 (lines 231 to 238, 383, 384, and 391). |
| P-I5 knip and entry exports | As M-4; d-s2rdn2 keeps `includeEntryExports` off until the third plan, since 13 front-door names have no reader before then, and adds the `__all__` test (line 688). |
| P-I6 `ValueError` and `LookupError` | As I-6 (lines 34 and 35). |
| P-I7 `repr` in messages | As I-2: `pyRepr` in `text.ts` with `py_repr_matches_python` (line 444), and `!r` becomes `pyRepr` (line 37; Tasks 5a, 8a, and 8b). |
| P-I8 `re.MULTILINE` | As I-2 (line 39, Tasks 6 and 9b); Review Focus 2 names U+2028 and a lone CR (line 76). |
| P-I9 tasks too large | d-mfayy5: Task 5 into 5a and 5b (lines 452 and 474), Task 7 into 7a and 7b (516 and 536), Task 8 into 8a, 8b, and 8c (555, 576, and 596), Task 9 into 9a and 9b (613 and 632), each cut where the imports let a reviewer reject one half and accept the other; the carried files over code an earlier half ported (5b's `fileformat-text`, 8c's three) are seen failing against a named mutation (lines 25, 486, and 605); the parity rows and the `test.todo` hand-offs follow the new numbers. |
| P-I10 the differential run skips the writers | d-0qmd10 replaces d-g3mbmc; a fifth key `rewrite` compares a hash of each writer's text for every parsed record and area file (line 711); Review Focus 7 (line 81). |
| P-I11 no page for passkeys | d-jtxwg3: the third plan's last task serves one minimal page from `api` (register with the setup code, sign in, issue and revoke agent tokens, approve drafted decisions), tested through the handler with the software authenticator and once by the coordinator in a real browser before the third plan merges; Plan 3's paragraph (lines 91 to 95) and the passkeys bullet (lines 110 to 115). It sits in plan 3 because plan 3 builds `api`, passkeys, and tokens, plan 2 ends with no HTTP, and plan 4 is the importer and the export; a command on the server's machine was rejected because a passkey is made only through `navigator.credentials` in a page, and an approval from a machine an agent may run on would not enforce SRV-2. |
| P-M1 the brief names the local folder | `planner-brief.md` names "the plan's worktree" instead. |
| P-M2 counts | As M-10. |
| P-M3 Node runs the gate's tools | d-xph4ac replaces d-03xx0a: `scripts/check-ts.sh` runs `bun --bun run check` (line 326, line 22); probe 20 shows `tsc`, dependency-cruiser, and knip running on Bun. |
| P-M4 the authenticator and strict `tsc` | As M-12 (line 113). |
| P-M5 nesting | As M-1. |
| P-M6 TOML floats | As M-9; line 440 names `Bun.TOML.parse` for the carried settings tests. |
| P-M7 Task 1's `where` | Line 265: a coordinator that did not hold the conversation asks the author for the session's name before Step 1. |
| P-M8 d-k5swcq and the author's call | d-x6f9za: each adapter keeps the permissions of the lodge 0.2 package it replaces (`git` from `gitstore`, `cli` from `cli`, `api` from the viewer, `hook` from `hook`, per LODGE-5 and `tests/structure_imports.py:92-98`), so the table is a renaming; `store` loses the file access the plan had given it and keeps only `bun:sqlite`, which ARCH-3 requires; a file need of the store goes to the author. |
| P-M9 Review Focus has nothing on the gate | Review Focus 6 (line 80), with the test `a_ported_file_losing_a_name_fails` (line 391). |

## Not changed

- d-k5swcq's own text: its reasoning stands; d-x6f9za adds the scope and permissions without replacing it, and the "looks related" question was answered no.
- The design and `lodge spec`: no finding asks for a change to either.
