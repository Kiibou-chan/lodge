# Review of Tasks 8c and 9b

Reviewer: `reviewer` (Opus), at 51e2121 (`server-core`), in a detached scratch worktree.
Task 8c: `git diff b774146 5cace5c -- ts/`; Task 9b: `git diff a54f486 c54d421 -- ts/`, merged at 51e2121.
Baseline: `bun test` in the scratch worktree at 51e2121, `805 pass`, `1 todo`, `0 fail`, `Ran 806 tests across 49 files`.

## The merge at 51e2121

`git merge-tree --write-tree 5cace5c c54d421` gives tree `b6794b7`, the tree of 51e2121, so the merge is the clean automatic merge with no hand resolution.
The two lanes touch disjoint lines of `ts/tests/parity.json` and only 9b touches `ts/src/core/index.ts`.

## Task 8c, correctness

Each of the 17 compare, 13 link, and 15 thread tests was read beside its Python original (`tests/core/test_check_compare.py`, `test_check_links.py`, `test_check_threads.py`).
Every name is present, every parametrised case is present (`title`, `statement`, `code`; `[false, EDIT]`, `[true, CREATE]`; `statement`, `title`; both stale-path and both wrong-name cases), and the one-parameter lists use `.map((c) => [c])` as probe 15 asks.
Whole-value `==` became `toEqual`, `in found` became `toContainEqual`, and `any(...)` became `.some(...)` with `toBe(true)`, none weaker than Python.

The five restored `checkChange` assertions (`ts/tests/core/apply.test.ts:59`, `:160`, `:190`; `ts/tests/core/apply-edits.test.ts:58`, `:93`) match `tests/core/test_apply.py:61-62`, `:144-145`, `:157-158`, `:224-226`, and `:246-247`: the tree is the union of the original and written files with the written ones winning, as `{**tree.files, **result.files}` does, and the reasoning edit asserts exactly `[5]`.

The report's mutations were rerun for the five apply assertions in the scratch worktree and each fails as claimed: `>` to `>=` at `ts/src/core/check-change.ts:67` fails the three accepting tests, and dropping `["reasoning", "reasoning"]` or `["statement", "statement"]` at `ts/src/core/check-immutable.ts:26-27` fails its one test.
Seven further mutations of my own were run against the three check test files; six fail at least one test:

| Mutation | Result |
|---|---|
| `check-entries.ts`, the link exemption accepts only `EDIT`, not `CREATE` | `link_with_another_decision_accounting_for_text_passes true "create"` fails |
| `check-entries.ts`, no `create` wanted for a new entry | 3 fail |
| `check-entries.ts`, verb `edited` becomes `changed` | 9 fail |
| `check-entries.ts`, imported exemption without `before === undefined` | 3 fail |
| `check-entries.ts`, unlisted-source check on every entry, not only new ones | 1 fails |
| `check-cycles.ts`, the other members joined in reverse | 1 fails |
| `check-entries.ts:58`, the duplicate-change skip removed | survives the whole core suite (628 pass) |

The surviving mutation removes the TypeScript form of Python's `dict.fromkeys(d.changes)` (`src/lodge/core/check_entries.py:42`); no Python test covers it either (by reading `tests/core/test_check_*.py`, not run), so it is not a weakening by this task and is recorded here only as information for Task 12's differential run.

No Blocking or Important finding for Task 8c in this pass.

## Task 9b, correctness

### Rendering and search against lodge 0.2 on this repository's records

A Python dump (`load` of every file under `lodge/` into `Tree`, `derive`, `check_state`, `failing_ids`, then `render_spec`, `spec_view`, `search_counted`, `related`, and `resolve`) was compared with the same dump from the TypeScript core, at 51e2121, on the 225 decisions and 125 entries (350 records), in two states:

- the records as they are;
- the records with edge text put in: thirteen statements holding U+2028, a lone CR, CRLF before `#` and `===`, U+001C, U+0085, U+000B, U+000C, U+FEFF, U+2029, an astral character, a lone surrogate U+D800, three and four spaces before `#`, a tab after `---`, and a trailing newline; nine decision and nine entry titles holding `Ⅻ`, `x_y`, `ﬁ`, `ß`, `İ`, an emoji, a combining accent, `ΣΑΣ`, and `½ ² ٣`; and an area intro holding U+2028, CRLF, and `===`.

Each state compares 2,992 keys: `render_spec` of the whole store, of each of the ten areas, and of an unknown area; `spec_view`'s placements; `search_counted` for 69 queries (the edge words above in both cases, function words, empty and blank queries, five IDs of each kind, fifteen codes) under 19 filters (each kind, status, scope, `decided_by`, and area) at limits 3 and 20; `related` for every decision; and `resolve` of every query, bare and upper-cased with spaces.
All 5,984 values are equal, and both renders are equal byte for byte as UTF-8 with lone surrogates kept (42,974 and 38,881 code points).
1,570 of the 2,622 edge-state searches return at least one ID, so the edge words are found, not only missed alike.
The scripts (`py_probe.py`, `edges.json`, and `probe9b.ts`, the last run from `ts/` so that `#core` resolves) lived in the reviewer's scratch space and the scratch worktree, both gone after this review; the two dumps were compared key by key with `json` in Python.

The repository holds no undated record and no bare day (0 of 350 by `level1(...).date`), so the run does not reach `NEVER` (`ts/src/core/search.ts:10`).
A separate run with two undated entries and two dated decisions gives `['d-dddddd', 'd-bbbbbb', 's-cccccc', 's-aaaaaa']` for both the empty query and `cache` in both languages.

`render-text.test.ts`'s expected text equals what Python's `render_spec` gives for the same snapshot (run: `True`).

### `words` over every code point

`words("a" + c + "b z" + c)` was computed for every code point outside the surrogates in both languages: they differ at 9,039 code points, every one of category `Cn` in Python 3.13.5's database (Unicode 15.1.0) and a letter or number to Bun 1.3.14 (the first U+088F, U+0C5C, U+0CDC).
`/[^\W_]/` matches 138,557 code points in Python and `/[\p{L}\p{N}]/u` 147,596 in Bun, the difference being those 9,039.
So lowercasing and the class agree at every code point Unicode 15.1 assigns; the difference is the known Unicode-version skew of probes 14, 18, and 23 (see 9b-P-1).

### Carried tests against the Python ones (Review Focus 1)

All 13 render tests and 17 search tests were read beside `tests/core/test_render.py` and `tests/core/test_search.py`.
Neither file has a parametrised test; whole values compare with `toEqual`, `in text` with `toContain`, and `pytest.raises(AmbiguousRef, match=…)` with `toThrow(AmbiguousRef)` and `toThrow(/d-aaaaaa, s-bbbbbb/u)`.
One test asserts less than its original (9b-C-1).

### Mutations

Mutations of the new modules, run against `render.test.ts` with `render-text.test.ts`, and against `search.test.ts`:

| Mutation | Result |
|---|---|
| `HEADING_LINE` back to `^…$` with the `m` flag | `heading_line_breaks_at_newline_only` fails |
| `=+[ \t]*` without its end anchor | 1 fails |
| `removesuffix` as `/\n+$/` | 6 fail |
| `rests_on` targets not deduplicated | 1 fails |
| `HEADING_LINE` indent `{0,3}` as `{0,4}` | survives |
| `[ \t]` as `[ ]` after `===` or after `---` | survives, both |
| tie by ID reversed | 1 fails |
| `NEVER` as the latest instant | survives |
| score `> 0` as `>= 0` | 5 fail |
| common-word threshold `n * 3 > len` as `>=` | survives |
| `COMMON_FROM` 6 or 4 | 1 fails each |
| `RELATED_SCORE` 1 or 3 | survives, both |
| `RELATED_WORDS` 1 | 1 fails |
| `isDigit` filter dropped | 1 fails |
| `strip` dropped in `resolve` | survives |
| ambiguous IDs not sorted | survives |
| `TITLE_WEIGHT` 1 | 1 fails |
| `decided_by` filter ignored | 1 fails |
| `words` class with `_` | survives |
| `toLowerCase` dropped in `words` | 9 fail |
| exact hits not excluded from the ranked list | survives |

The Python tests hold the same cases (by reading, not by running each mutation in Python), so no surviving mutation is a weakening by this task; the ones the brief names or Review Focus 2 lists are 9b-C-2.

### 9b-C-1 · Minor · `render_spec_follows_rank_then_derived_order` passes when a heading is missing

Handle: `ts/tests/core/render.test.ts:134-135`; Python `tests/core/test_render.py:129`.
Python's `text.index` raises `ValueError` when the text is absent; `indexOf` gives -1, and `-1 < indexOf("## First")` holds.
Run: rendering the area heading as `#${held.title}` (`ts/src/core/render.ts:41`) leaves this test passing in TypeScript (`1 pass`), while the same change at `src/lodge/core/render.py:52` fails the Python test with `ValueError`.
Other render tests compare the whole text, so the suite still catches that mutation; only this test is weaker than its original (Review Focus 1).
Fix: a local `at(text, part)` that throws when `indexOf` gives -1, or `expect(text.indexOf("# Storage")).toBeGreaterThanOrEqual(0)` before the two comparisons.

### 9b-C-2 · Minor · four edges the brief names or Review Focus 2 lists are pinned by no test

Handle: `ts/src/core/search.ts:10` (`NEVER`, brief Interfaces "search's never date is the earliest instant"); `ts/src/core/words.ts:85` (the brief's `[^\W_]+` becomes `[\p{L}\p{N}]+`, so `_` splits); `ts/src/core/render.ts:6` (the three-space limit and the tab in `[ \t]`).
Each survives its mutation in the table above (the Python tests hold the same cases, by reading), and Task 12's differential run reads only this repository's records, which hold no undated record (0 of 350) and no line with four spaces before `#` or a tab after a run of `=` or `-` (`grep -rlP '^ {4,}#|^[=-]+[ ]*\t' lodge`: 0 files); its queries are the first word of each title, so whether one meets a word holding `_` (statements hold `decided_by` and `work_item`) is not established.
Failure scenario: a later fix round writes `NEVER` as `Number.MAX_SAFE_INTEGER` or the word class as `[\p{L}\p{N}_]` (the Global Constraints' `WORD_CLASS` of `text.ts` holds `_`, an easy reach); every test passes, and an undated imported entry then heads every search, or `x_y` stops finding `x`.
The behaviour is right today: the differential above and the undated run agree with Python.
Fix: add to `render-text.test.ts` (the task's new test file) a statement with `    # four spaces` and `---\t`, expected as Python renders it, and a coordinator ruling on whether a new `search-text.test.ts` holds an undated entry beside dated decisions and a title with `x_y`, since the plan names no new search test.

No Blocking or Important finding for Task 9b in this pass.

## Practice

### 8c-P-1 · Minor · the restored `checkChange` call is written out five times

Handle: `ts/tests/core/apply.test.ts:59-66`, `:160-167`, `:190-197`; `ts/tests/core/apply-edits.test.ts:58-65`, `:93-100`.
Each is the same eight lines, `checkChange(s, load(makeTree({ rev: null, files: new Map([...tree.files, ...result.files]) })), coreSettings(), NOW)`, differing only in `.ok` or `.problems`; Python writes the merged tree inline too, but in two short lines (`tests/core/test_apply.py:61-62`).
Failure scenario: a later change to how the merged tree is built (plan 2 replaces `Tree` loading with the store) is made in four places and missed in the fifth, and that test then checks a different tree from the others.
Fix: a local `checkedAfter(s, tree, result)` in each of the two test files, not an export of `applying.ts`, whose exports follow `applying.py`'s (d-tha8st).

### 9b-P-1 · Minor · the report does not list `words`' known difference from Python

Handle: `docs/superpowers/plans/2026-11-02-lodge-server-core/task-9b-report.md` ("Every carried Python test holds in TypeScript"); `ts/src/core/words.ts:85`; the plan lists the same kind of difference for `isDigit` and `pyRepr` as known differences each report names (`docs/superpowers/plans/2026-11-02-lodge-server-core.md:456`, `:458`).
Run (see "`words` over every code point"): 9,039 code points, all unassigned in Unicode 15.1, are words to the TypeScript and not to lodge 0.2; `related` also inherits `isDigit`'s 90.
Failure scenario: Task 12 or plan 4's importer meets a title in a script Unicode 16 added, search results differ, and the difference reads as a bug in `search.ts` rather than the accepted Unicode skew.
Fix: one line in the report (or the ledger line for 9b) naming the 9,039 code points, the first U+088F, and that they are the probe 14 skew.

Other practice points checked without a finding: the function words of `ts/src/core/words.ts` equal Python's list (79, `diff` empty); the three modules carry no comments and no dead code; `knip` reports no unused export; each new file is under 300 lines (81, 133, 87, 212, 264, 15).
The 8c report's mutation for `check_4_new_entry_without_a_decision` and `check_4_new_entry_listed_with_the_wrong_action` is keyed on the fixture's ID (`entry.id !== "s-bbbbbb"`), which targets the test rather than the behaviour; the behavioural form (`if (false) wanted.push`) also fails both, so the evidence holds.

## Design

No finding.
The apply tests now import `checkChange`, `load`, and `tree` from `#core`, as `tests/core/test_apply.py` imports `check_change`; no import rule or front door changes.
`search.ts` and `render.ts` import only `core` modules; `NEVER` is a module constant computed from a literal with `orderInstant`, no clock (Review Focus 5).
`search`'s ordering of a bare day through `orderInstant`, where Python's `_when` gives a naive `datetime` that cannot be compared with the aware ones, falls under ruling d-g1hrmn and is not raised again.
`words` is not exported through `#core`, as `words` is not in `lodge.core.__all__` (`src/lodge/core/__init__.py`), and `filters` is the default-filling function d-ca6wbw asks for.

## Files read

Read: `CLAUDE.md`; the plan's `## Review Focus` (`docs/superpowers/plans/2026-11-02-lodge-server-core.md:94-102`), Task 12 (`:724-749`), and the known-difference lines (`:442-458`); `task-8c-brief.md`, `task-8c-report.md`, `task-9b-brief.md` (coordinator notes and Task 9b), `task-9b-report.md`, `task-11-report.md:130-160`; `probes.md` items 14, 16, 18, 23, and 27 (by `grep`); `task-7a-review.md` and `task-5a-review.md` (severity of weaker tests, by `grep`); rulings d-p48gr1, d-fbhdvf, d-g1hrmn, d-4m6m35, d-0q54zn, d-f18pz7, d-442r2f, d-qe513h through `lodge show`.
Code at 51e2121: the whole diffs `b774146..5cace5c -- ts/` and `a54f486..c54d421 -- ts/`; `ts/src/core/check-entries.ts`, `render.ts`, `search.ts`, `words.ts`; `ts/src/core/index.ts`, `errors.ts` (class lines), `stamps.ts:49-51`, `snapshot.ts:1-28`, `views.ts:13-26`; Python `src/lodge/core/render.py`, `search.py`, `words.py`, `check_entries.py:35-80`, `snapshot.py:30-50`, `views.py:49-58`, `app/state.py:40-80`, `__init__.py` (by `grep`); `tests/core/test_check_compare.py`, `test_check_links.py`, `test_check_threads.py`, `test_render.py`, `test_search.py`, `test_apply.py:38-250`.
Not read: `ts/tests/core/checks.ts`, `builders.ts`, and `applying.ts` beyond their use in the tests; `check-change.ts`, `check-immutable.ts`, `check-state.ts`, and `check-cycles.ts` beyond the mutated lines; `order.ts` and `derive.ts`; `ts/tests/parity.test.ts`; the Codex final messages; the ledger.

## Counts

Task 8c: 0 Blocking, 0 Important, 1 Minor (8c-P-1).
Task 9b: 0 Blocking, 0 Important, 3 Minor (9b-C-1, 9b-C-2, 9b-P-1).
The merge at 51e2121: no finding.

Status: complete.
