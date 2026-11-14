# Plan recheck 2: lodge server core

Fix diff: `git diff b5c8ad5 e057056` on branch `server-core`.
Findings: `plan-recheck-1.md` (N1, N2, N3, m1 to m6, and its preflight mismatch rows); answers in `plan-fix-2.md` and `plan-fix-2-report.md`.
Rulings read: d-tha8st, d-hshapm, d-bxcave, d-87kzys.
Rechecker: `rechecker` agent, 2026-11-02.
Status: done.

## Probes rerun

Run in a detached worktree of my own at `e057056` (removed when done), Bun 1.3.14, knip 6.42.0, Python 3.13.5 with Unicode 15.1.0.

- Probe 21, `probes/fix2/knip/` after `bun install`, the four configurations of its `README.md`:
  A (`entry` the test pattern, no `confirmation.ts`) prints `Unused exports (2)`, `orderKey` and `LATER`, exit 1;
  B (`derive.ts` and `helpers.ts` in `entry`) exits 0;
  C (`confirmation.ts` reads `orderKey`, `derive.ts` out, `helpers.ts` in) exits 0;
  D (both out) prints `Unused exports (1) LATER`, exit 1.
  The probe reproduces as `probes.md` item 21 gives it.
- Two further configurations of the same folder:
  with `derive.ts` left in `entry` after its reader exists, knip exits 0 and prints no hint, so a task that forgets to take a file out stays green, and only Task 11's Step 4 (plan line 719, `entry` back to Task 2's two patterns) catches it;
  with a path in `entry` that matches no file, knip prints the configuration hint `Refine entry pattern (no matches)` and exits 0.
- Dropping `export` from `orderKey` while `confirmation.ts` imports it gives `TS2459 … declares 'orderKey' locally, but it is not exported`, exit 2, as expected; the planner's `TS6133` case (a name its own file never reads) was not rerun.
- Probe 23: `probes/fix2/digits.ts` against Python's `isdecimal` list prints `\p{Nd} 770, more than isdecimal 90, isdecimal not \p{Nd} 0`, first extra `10d40`; Python counts 808 `isdigit` characters and gives U+10D40 the category `Cn`.
- Probe 22: `repr(chr(0x200b))` under `uv run --frozen python` prints `'\u200b'`.
- Probes 24 and 25 were not rerun.

## Escapes and invisible characters

Every file the fix diff touches is clean: a scan by Unicode category (`Cc` but tab, `Cf`, `Cn`, `Co`, `Cs`, `Zl`, `Zp`, and `Zs` but the space) finds nothing in the plan, the ledger, `plan-fix-1.md`, `plan-fix-2.md`, `plan-fix-2-report.md`, `probes.md`, or `probes/fix2/`.
The non-ASCII characters the diff adds are all visible: `…`, `😀`, `①`, `½`, `²`, `٣`, `é`, `ſ`, `ß`, `ﬆ`, `α`, `Α`, `σ`, `Σ`.
The U+200B case of `py_repr_matches_python` (plan line 469) is ASCII by `od -c`: `U + 2 0 0 B   t o   ` ' \ u 2 0 0 b ' ``.
Lines 462 and 469 write U+D7FF, U+E000, U+FFFD, U+FEFF, U+2028, and U+FFFF as `\uXXXX` (`grep -nP '\\u(D7FF|E000|FFFD|FEFF|2028|FFFF)'` matches lines 462 and 469).

Raw invisible characters remain in two files of the folder that the fix did not touch:

```
$ grep -rnP '[\x{200B}\x{2028}\x{2029}\x{FEFF}\x{200C}\x{200D}\x{2060}\x{00AD}\x{E000}-\x{F8FF}\x{FFF0}-\x{FFFF}]' 2026-11-02-lodge-server-core* | cut -d: -f1,2
2026-11-02-lodge-server-core/plan-recheck-1.md:101
2026-11-02-lodge-server-core/plan-recheck-1.md:103
2026-11-02-lodge-server-core/plan-review-practice.md:60
2026-11-02-lodge-server-core/plan-review-practice.md:62
2026-11-02-lodge-server-core/plan-review-practice.md:67
```

`plan-recheck-1.md:101` and `:103` hold a raw U+200B (bytes `342 200 213`), so N3's own evidence and its suggested fix carry the character they warn about; `plan-review-practice.md:60`, `:62`, and `:67` hold a raw U+2028 (bytes `342 200 250`) in quoted test inputs.
Both are review records, not the plan, so no builder reads them as instructions; they are reported, not counted as findings.

## Findings of recheck 1

Plan line numbers are those at `e057056`.

| Finding | Verdict | Handle |
|---|---|---|
| N1 exports first read in a later task | Closed | Global Constraints lines 45 to 60 and d-tha8st; the entry table agrees name for name with my scan below; each task's Modify list and Step 3 name the entries (lines 424, 482, 505, 525, 547, 567, 586, 607, 625, and 705, and each Step 3); Task 11's Step 4 (line 719) checks `entry` is back to Task 2's two patterns; probe 21 reproduces. |
| N2 `front_door_exports_nothing_else` against Task 4's exports | Open, narrowed | Closed for `quoted` and `unreadableChar` (line 454, d-hshapm) and for the five default-filling functions of `model.ts` (lines 430 and 714); still open for the default-filling functions of the other dataclasses with defaults in `__all__` (N2-r below). |
| N3 U+200B in `py_repr_matches_python` | Closed | Line 469 holds `'\u200b'` as ASCII (`od -c` above); probe 22 reruns. |
| m1 `isDigit`'s 90 extra characters | Closed | Line 455; probe 23 reruns (770, 90, U+10D40, `Cn`); a wording residue in the interface comment, line 441, is m-a below. |
| m2 `plant`'s link and dependency types | Closed | Lines 382 and 383, d-bxcave; probe 24 not rerun. |
| m3 `\s` without a helper | Closed | Lines 38, 447, 469 (`py_space_class_matches_is_py_space`), and 692, d-87kzys; `feedback.py:20` is the core's only `\s` (`grep -nE '\\s|\\S' src/lodge/core/*.py`). |
| m4 raw characters | Closed | Lines 462 and 469, and the scan above. |
| m5 Biome's notice | Closed | `plan-fix-1.md`'s M-8 row corrected in place. |
| m6 plan 3's page | Closed | Line 114; probe 25 not rerun. |

### The entry table against a scan of first readers

An AST scan of every `from lodge.core.X import …` and helper import in `src/lodge/core/*.py` and `tests/core/*.py`, each file mapped to its task by the plan's Port and Test lines, leaving out names of `__all__` (which `index.ts` re-exports, and knip does not report: probe 21's `isAuthor`), finds these names whose first reader is in a later task than the module that defines them:

| File | Its task | Names, first reader's task | Table, lines 49 to 58 |
|---|---|---|---|
| `yamlio` | 4 | `LINE_BREAKS_AND_TABS`, `quoted`, `unreadable_char` (5a, `fields.py` and `fileformat.py`) | Agrees |
| `headers` | 5a | `AREA_KEYS`, `DECISION_KEYS`, `SPEC_KEYS` (5b, `drafts.py`) | Agrees |
| `document` | 5a | `split_document`, `problem_for`, `load_header` (5b, `drafts.py`); `key_line` (6, `threads.py`) | Agrees |
| `fields` | 5a | `read_stamp` (6, `threads.py`) | Agrees |
| `builders` (test) | 6 | `tree_of` (11, `applying.py`) | Agrees |
| `derive` | 7a | `order_key` (7b, `confirmation.py`) | Agrees |
| `check_state` | 8a | `new_decisions`, `problem_at`, `sort_key` (8b, `check_change.py`) | Agrees |
| `checks` (test) | 8a | `NOW`, `SETTINGS`, `LATER`, `NOTES`, `OLD`, `SPEC`, `Item`, `creates`, `published`, `state`, `old_decision`, `REMEDY_CHECK_5`, `REMEDY_CHECK_5_REASONING`, `check`, `verdict` (8b); `REMEDY_CHECK_4` (8c, `test_check_compare.py`) | Agrees |

No other module or helper has such a name, and the helper names no other file imports are exactly `next_id` (with the private `_ALPHABET` and `_NUMBERS`) of `builders.py`, `base_items` and `key` of `checks.py`, and `drafted` of `applying.py`, as line 45 says.
No core test imports from a submodule of `lodge.core` (`grep -rn "from lodge.core\.[a-z_]* import" tests/core` prints nothing), and none of `quoted`, `unreadable_char`, or `LINE_BREAKS_AND_TABS` is in `__all__` (91 names), as d-hshapm needs.

## New and remaining problems

### N2-r (Important): six dataclasses with defaults outside `model.py` get default-filling functions that Task 11's test refuses

Handles: plan line 33 (every frozen dataclass "where Python fills defaults" becomes an interface and "a function of the same name in camelCase that fills them"); line 714 (`front_door_exports_nothing_else` allows a default-filling function only when "defined in `model.ts`", and names five); line 430 (Task 4 produces only `decision`, `specEntry`, `area`, `problem`, and `message`); d-hshapm and line 89 ("the default-filling function of each dataclass among them", which is wider than line 714).
Evidence: an AST scan of `src/lodge/core/*.py` for dataclasses with a defaulted field finds, besides the five of `model.py`, `LengthGuidance` and `CoreSettings` (`settings.py`, Task 4), `Tree` and `Snapshot` (`snapshot.py`, Task 6), `Draft` (`drafts.py`, Task 5b), and `Filters` (`search.py`, Task 9b), all six in `__all__`.
The carried tests build five of them with their defaults through `lodge.core`: `LengthGuidance()` and `CoreSettings(length=LengthGuidance(), import_sources=())` at `tests/core/test_settings.py:10`, `CoreSettings()` at `tests/core/test_check_threads.py:29`, `Tree(None, files)` at `tests/core/test_check_threads.py:52` and `tests/core/test_apply.py:61`, `Snapshot(…)` at `tests/core/builders.py:94` (`threads` defaulted, `src/lodge/core/snapshot.py:46`), and `Filters()` at `tests/core/test_search.py:38`.
Since a test reaches `core` only through `#core` (the `front-door` rule binds tests, plan lines 385 and 388, and no core test imports a submodule), `#core` has to export `lengthGuidance`, `coreSettings`, `tree`, `snapshot`, and `filters`.
Failure: Task 4's builder, following line 33 and `test_settings.py:10`, exports `lengthGuidance` and `coreSettings` through `#core`, Tasks 6 and 9b do the same for `tree`, `snapshot`, and `filters`, and Task 11's new test then fails on five names defined in `settings.ts`, `snapshot.ts`, and `search.ts`; the builder either widens the test on its own judgement (the call d-hshapm was made to settle) or drops the functions and rewrites the carried tests to spell out every default, which weakens nothing but departs from line 33.
This is the same mechanism as N2, which recheck 1 scoped to `model.py` alone; the fix copied that scope rather than introducing it.
Fix: line 714 allows "the default-filling function of a `PascalCase` name of `__all__`, its first letter lower case, defined in the module that defines the type", and names the eleven (`decision`, `specEntry`, `area`, `problem`, `message`, `lengthGuidance`, `coreSettings`, `tree`, `snapshot`, `draft`, `filters`); line 430 adds `lengthGuidance` and `coreSettings` to Task 4's Produces, line 530 adds `tree` and `snapshot` to Task 6's, line 510 `draft` to Task 5b's (or says `Draft` has none exported, since no test builds one), and line 668 `filters` to Task 9b's.

### Minor

- m-a: the interface comment for `isDigit` (line 441) ends "Python's 808 characters (probe 23)", which reads as the count `isDigit` takes, while line 455 says it takes 90 more; fix: "Python's 808 characters and the 90 of line 455".
- m-b: the 90 code points of probe 23 are also where Python's regular-expression `\d` and the plan's `\p{Nd}` (line 38) differ, which reaches `feedback.py`'s `_CODE`, `_DATE`, and `_NUMBER` (`src/lodge/core/feedback.py:17-20`, Task 10); line 455 lists them for `isDigit` only; fix: Task 10's report lists the same 90 for `\d`.
- m-c: a file left in `entry` after its last reader exists keeps knip silent (probe 21, the stale-entry configuration above: exit 0, no hint), so a forgotten removal surfaces only at Task 11's Step 4 (line 719); the reading tasks' Step 4 (lines 517, 539, 578, 619, 636) could each add "and `ts/knip.json`'s `entry` no longer names the file", which costs one look.

## Preflight

Each pair of tasks that share a file or an interface: what the earlier produces against what the later consumes, at `e057056`.
Module and test order come from the import scan above, against each task's Port, Test, and Produces lines.

| Pair | Shared file or interface | Produced | Consumed | Found |
|---|---|---|---|---|
| 1 and 12 | the store's decision count | eight author decisions | the counts the run prints | Agrees, unchanged by the fix. |
| 2 and 3 | `ts/.dependency-cruiser.cjs`, `ts/package.json`, `scripts/check-ts.sh` | two rules, `#core`, the gate | the full table, the gate | Agrees. |
| 2 and 4 to 11 | `ts/knip.json`'s `entry` | Task 2's two patterns, and the note that the list grows and shrinks (line 339) | files added and taken out by the table of lines 49 to 58; Task 11 checks the two patterns are back (line 719) | Agrees; each file goes in once and out once, in the tasks the table names (m-c on a forgotten removal). |
| 2 and 4, 2 and 5a | `ignoreDependencies` | `yaml`, `@noble/hashes` | taken out in 4 and 5a | Agrees, unchanged. |
| 3 and 4 to 11 | `ts/tests/parity.json`, the rules; `plant` | statuses, the rules; `plant` with `dependencies` and `preserveSymlinks` (lines 382 and 383) | rows flipped; `core` imports `yaml` and `@noble/hashes` as `npm` | Agrees. |
| 4 and 5a | `yamlio.ts` in `entry` | `LINE_BREAKS_AND_TABS`, `quoted`, `unreadableChar` module-internal (line 454) | `fields.ts` and `fileformat.ts` read them; 5a takes `yamlio.ts` out (lines 482 and 496) | Agrees. |
| 4 and 10 | `text.ts` | `WORD_CLASS`, `PY_SPACE_CLASS` (line 447), each with a test in Task 4 (line 469) | `_NUMBER`'s `\s?` and `\b` (line 692) | Agrees (m-b on `\d`). |
| 4 and 11 | `#core`'s exports | `lengthGuidance` and `coreSettings`, which `test_settings.py:10` needs through `#core` (line 33) | `front_door_exports_nothing_else` allows only `model.ts`'s five (line 714) | **Mismatch** (N2-r). |
| 5a and 5b | `headers.ts`, `document.ts` in `entry` | the six names | `drafts.ts` reads them; 5b takes `headers.ts` out, `document.ts` stays (line 516) | Agrees. |
| 5a and 6 | `document.ts`, `fields.ts` in `entry` | `keyLine`, `loadHeader`, `readStamp` | `threads.ts` reads them; 6 takes both out (line 538) | Agrees. |
| 5b and 7b | `parseDraft`, `recordFromDraft`, `Draft` | 5b's Produces (line 510) | `test_confirmation.py` | Agrees; `draft`, the default-filling function of `Draft`, is read by no test (N2-r names it for completeness). |
| 6 and 7a to 11 | `builders.ts` in `entry`, `Tree`, `load`, `Snapshot` | `builders.ts`; `treeOf` waits | every later test file; `applying.ts` reads `treeOf` in 11, which takes `builders.ts` out (line 718) | Agrees on `entry`. |
| 6 and 11 | `#core`'s exports | `tree` and `snapshot`, needed through `#core` by `Tree(None, files)` and `Snapshot(…)` in the carried tests | `front_door_exports_nothing_else` (line 714) | **Mismatch** (N2-r). |
| 6 and 9a, 6 and 10 | `snapshot.test.ts`, `thread-files.test.ts` | one `test.todo` each | turned into tests | Agrees, unchanged. |
| 7a and 7b | `derive.ts` in `entry` | `orderKey` (line 552) | `confirmation.ts`; 7b takes `derive.ts` out (lines 567, 577) | Agrees. |
| 7a and 9a | `doubts.test.ts` | two `test.todo`s | turned into tests | Agrees, unchanged. |
| 8a and 8b | `check-state.ts` in `entry`, `checks.ts` | `newDecisions`, `problemAt`, `sortKey` (line 591); `checks.ts` but `check` and `verdict` (line 587) | `check-change.ts` reads the three; 8b takes `check-state.ts` out and adds `check` and `verdict` (lines 607, 618) | Agrees. |
| 8b and 8c | `checks.ts` in `entry` | `REMEDY_CHECK_4` unread in 8b | `check-compare.test.ts`; 8c takes `checks.ts` out (lines 625, 636) | Agrees. |
| 8c and 9a | `check-threads.test.ts` | one `test.todo` | turned into a test | Agrees, unchanged. |
| 9a and 9b | `views.ts` | `level1`, `level3`, and the rest | `render.py`, `search.py` | Agrees, unchanged. |
| 9b and 10 | `search.ts` | `search`, `related` | `feedback.py` | Agrees. |
| 9b and 11 | `#core`'s exports | `filters`, needed through `#core` by `Filters()` in `test_search.py:38` | `front_door_exports_nothing_else` (line 714) | **Mismatch** (N2-r). |
| 10 and 11 | `feedback.ts`, `index.ts` | `Feedback`, `feedback`, `areaFeedback` | Task 11's front-door test | Agrees (`Feedback` has no defaulted field). |
| 11 and 12 | `#core` | every `__all__` name | `differential.ts` | Agrees, unchanged. |

Each task against itself:

| Task | Agrees with itself | Found |
|---|---|---|
| 1 | Yes | Unchanged. |
| 2 | Yes | Line 339 says `entry` changes under the later tasks. |
| 3 | Yes | `plant` and `cruise` settle m2 (lines 382 and 383). |
| 4 | **No**, through line 33 | Its Produces (line 430) gives default-filling functions for `model.ts` only, while its own carried `test_settings.py:10` needs `lengthGuidance` and `coreSettings` through `#core` (N2-r); the `isDigit` comment and line 455 read as two counts (m-a). |
| 5a | Yes | Deferred names listed (line 488), `entry` steps match the table. |
| 5b | Yes | Step 3 names the six imports and takes `headers.ts` out. |
| 6 | Yes, given N2-r | `entry` steps match the table; its Produces (line 530) omits `tree` and `snapshot`. |
| 7a | Yes | `orderKey` waits in `entry` (line 552). |
| 7b | Yes | |
| 8a | Yes | `sortKey` named (line 591); `checks.ts` waits until 8c (line 587). |
| 8b | Yes | `checks.ts` stays in `entry` for `REMEDY_CHECK_4` (line 618). |
| 8c | Yes | Step 4 takes `checks.ts` out (line 636). |
| 9a | Yes | |
| 9b | Yes, given N2-r | Its Produces (line 668) omits `filters`. |
| 10 | Yes | `\s` and `\b` settled (line 692); m-b on `\d`. |
| 11 | **No** | Its new test (line 714) against the default-filling functions line 33 makes and the carried tests need through `#core` (N2-r). |
| 12 | Yes | |

## Read and not read

Read: `CLAUDE.md`; `plan-recheck-1.md`; `plan-fix-2.md`; `plan-fix-2-report.md`; the whole fix diff `git diff b5c8ad5 e057056` (plan, ledger, `plan-fix-1.md`, `probes.md`, `probes/fix2/`); d-tha8st, d-hshapm, d-bxcave, and d-87kzys through `lodge show`; the import lines of every core module and core test (AST scan); the dataclasses of `src/lodge/core/*.py`; `__all__` of `src/lodge/core/__init__.py`; `src/lodge/core/feedback.py:15-20`; the constructions of `Tree`, `Snapshot`, `Filters`, `CoreSettings`, and `LengthGuidance` in `tests/core`.
Not read: `lodge spec` in full; the plan outside the diff beyond the lines cited; probes 24 and 25 were not rerun.

## Counts

Findings of recheck 1: 9 (N1 to N3, m1 to m6) and 11 preflight rows; closed 8, open 1 (N2, narrowed to N2-r); the preflight rows of N1 and N3 closed, those of N2 open as N2-r.
New: Blocking 0, Important 0 introduced by the fix (N2-r is N2's remainder, recheck 1 having scoped it to `model.py`), Minor 3 (m-a, m-b, m-c).
Preflight: mismatches between 4 and 11, 6 and 11, and 9b and 11 (N2-r); Tasks 4 and 11 disagree with themselves through line 33.
Invisible characters: none in any file the fix touched; raw U+200B at `plan-recheck-1.md:101` and `:103`, raw U+2028 at `plan-review-practice.md:60`, `:62`, and `:67`.
