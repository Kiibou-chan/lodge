# Review of Tasks 8b, 9a, and 11

Reviewer: `reviewer` agent (Opus), task review, three passes in order.
Task 8b: `git diff b93808b c3a811e -- ts/` on `server-core`.
Task 9a: `git diff b93808b 9e40182 -- ts/` on lane `server-core-t9a`.
Task 11: `git diff 0d1c6c5 854bebe -- ts/` on lane `server-core-t11`, run early under d-442r2f.
Merges: 4e20c28 and 73ab440 on `server-core`.
Probes ran in a detached scratch worktree at 73ab440 under `.claude/worktrees/`, removed afterwards; the probe scripts lie outside the repository.
Already ruled and not raised again: d-p48gr1, d-fbhdvf, d-g1hrmn, d-4m6m35, d-0q54zn, d-f18pz7, d-442r2f (Task 11's five missing `checkChange` assertions), and d-qe513h (the `ok` getter on `checkChange`'s literal, `check-change.ts:40-46`, and the hand-built `{ problems, notes, ok }` in `views.test.ts:136-145` and `:157`, both under 8a-D-1's fix).

## Counts

| Task | Blocking | Important | Minor |
|---|---|---|---|
| 8b | 0 | 0 | 3 |
| 9a | 0 | 0 | 2 |
| 11 | 0 | 0 | 5 |

## Pass 1: correctness

No correctness finding in any of the three tasks.
The evidence follows, so that the recheck can rerun it.

### Carried tests against the Python ones (Review Focus 1)

8b: every test of `test_check_change.py` (20 functions, 22 cases), `test_check_current.py` (4), `test_check_retired.py` (2), and `test_check_immutable.py` (12 functions, 29 cases) is carried by name with every case: the 14 header keys of `HEADER_EDITS` (`check-immutable.test.ts:25-43`), the four reasoning pairs as `test.each([[a, b], …])` with `%p %p` (`:81-86`), and the one-parameter verb lists through `.map((c) => [c] as const)` (`check-change.test.ts:66`, `check-immutable.test.ts:128`).
Every `==` on a whole value is `toEqual`; each Python `x in list` is `toContainEqual` on a list and `toContain` on a string (`check-change.test.ts:42`, `:193`, `:221`; `check-immutable.test.ts:51`, `:60`, `:157`), as Python's own test is weak there.
`checks.ts` gains `check` and `verdict` as `checks.py` has them (`checks.ts:50-55`).

9a: the 16 tests of `test_views.py`, 7 of `test_views_links.py`, and 7 of `test_views_trust.py` are carried by name, assertion for assertion, including both exact-text tests (`views.test.ts:250-289`).
The three `test.todo`s are now the Python tests (`snapshot.test.ts`, `doubts.test.ts`), and `thread_problems_are_visible_in_reads` carries both cases `false` and `true` through `.map((c) => [c])` (`check-threads.test.ts:5`).
Python's `is None` became `toEqual(null)` (`views.test.ts:107`, `views-trust.test.ts:28-29`), which Bun fails on `undefined`.

11: the 14 tests of `test_apply.py` (split over `apply.test.ts` and `apply-edits.test.ts`, both listed in `parity.json`) and the 24 of `test_apply_refusals.py` are carried by name; `pytest.raises(ValueError, match=…)` is `toThrow(ValueError)` and `toThrow(/2 new decision drafts but 1 IDs/u)` (`apply-refusals.test.ts:19-24`); the six cases of `id_of_the_wrong_shape_says_so` and both values of `area_name_not_a_string_is_problem` are all there.
Apart from the five `checkChange` assertions ruled under d-442r2f, no assertion is weaker than Python's.
Three tests are added beyond Python (`apply-refusals.test.ts:273-286`, `apply-edits.test.ts:185-193`); the last covers the `(the file is missing)` branch (`apply.ts:175`), which no Python test reaches, and its knip motive is gone since the merge (`snapshotOf` has readers in the views tests), but it keeps its value as coverage.

Run: `bun test tests/core` at 73ab440, `548 pass, 1 todo, 0 fail` (the todo is Task 10's `thread_id_is_not_number_feedback`).

### Targeted mutations (d-mfayy5, `task-5b-review.md` C-1)

50 mutations (25 of 8b's code, 11 of 9a's, 14 of 11's), each applied alone in the scratch worktree, run against all of `ts/tests/core`, and reverted.
Thirty-two fail a carried test, among them:

| Task | Mutation | Fails |
|---|---|---|
| 8b | `check-change.ts:84` `<=` to `<` | the three `check_1_new_decision_dated_no_later_than_its_target` cases, the shared-entry test, and `new_decision_must_be_after_an_unpublished_one…` |
| 8b | `:67` `>` to `>=` | `check_1_a_decision_dated_exactly_now_passes` |
| 8b | `:66` the `current` skip dropped; `:64` `current` left out of `earlier` | three and one `check-current.test.ts` tests |
| 8b | `:129` retired only before the change | `check_6_replacing_the_retirement_lets_the_decision_edit_the_entry_again` |
| 8b | `:92` the live filter dropped; `:69` the import exemption dropped | `check_1_import_changes_entry_only_imports_changed`; three import tests |
| 8b | `check-immutable.ts:36` `attachments` dropped; `:51` always "agent" | the `attachments` case; both author-reasoning tests |
| 9a | `views.ts:178` `retired by` dropped; `:175` replaced retirements kept | three tests; `retired_by_names_a_standing_retirement` |
| 9a | `:203` `>` to `>=`; `:147` "no decision" dropped; `:148` the day kept whole | `same_second_change_does_not_mark_changed_since`; two each |
| 9a | `:42` thread paths counted as held | both cases of `thread_problems_are_visible_in_reads` |
| 11 | `apply.ts:40` IDs unsorted; `:96` retirements not collected; `:159` duplicates kept | `new_ids_ascend_in_draft_order`; two tests; `two_drafts_for_one_record_refused` |
| 11 | `apply-areas.ts:32` restoration ignored; `:41` retired kept in the order | `replacing_retirement_restores_order`; `retire_removes_from_order` |
| 11 | `value-repr.ts:10` the one-tuple comma dropped; `:12` the `Map` branch dropped | `nested_change_read_back_repr`; two tests of `drafts.test.ts` and `apply-refusals.test.ts` |

Eighteen survive.
Ten are in 8b's code and caught by Python tests that later tasks carry; eight by the files Task 8c carries, so they are handed to 8c's review rather than raised here: `check-entries.ts:44` the "edit or link" label, `:39` the import exemption, `:84` the create-of-existing refusal, `:97` the import-source check, `:15` `Object.hasOwn`, `:20` the rests-on-only comparison, `check-immutable.ts:72` the closing-message rule, `:65` the appended-only rule (Python's twins: `test_check_links.py`, `test_check_compare.py`, `test_check_threads.py`, by `grep` of each message); the other two are `check-change.ts:55` threads left out of check 2 (Python's twin fails `tests/app/test_thread_ops.py::test_reply_appends`, plan 2), and `check-change.ts:112` the `previous` test (Python's twin fails `test_check_links.py::test_kept_rest_on_retired_entry_passes_check_6`).
Seven of the remaining eight have Python twins that survive all 1258 non-e2e Python tests (`python -m pytest -q tests -k "not e2e"` with each twin applied): see 8b-D-1, 9a-D-1, and 11-D-3.
The ValueError guard of Task 11 survives too (11-D-1); it has no Python twin.

### Python against TypeScript on this repository's records and edited variants (Review Focus 7)

A Python script read the 361 files under `lodge/` at 73ab440 into `Tree`s and built, per seed, 915 `check_change` cases, 307 states for the levels, and 513 `apply_drafts` cases; a Bun script ran the same inputs through `#core` and compared the answers as JSON, problem order included.
`check_change` cases: 25 decisions each edited in statement, reasoning, title, date, code, work item, and narrows, and removed; 20 entries edited without and with a listing decision (also with `now` one second before that decision's date), linked, made to rest on a retired entry, and removed; new decisions that replace, narrow, or confirm 25 decisions, dated at the target's date, before `now`, and after it; narrows and confirms of the 6 replaced decisions; edit, retire, link, and create of a retired entry, with the retirement published and with it only in `current`; each area's title, intro, order, and rank changed, and the area removed; 250 random line deletions, duplications, swaps, and character changes, every fifth also as the published state.
Levels: for every record of the store, a store with a retirement, and every third `check_change` state, `formatLevel1`, `headParts`, `level2`, the formatted `level2Views`, `formatLevel3`, `failingIds`, and `unrecordedProblems`.
`apply_drafts`: `lodge draft`'s text (`src/lodge/app/reads.py:110-122`) of 20 entries and 25 decisions, edited in the body, unchanged, with a stale or missing base, a moved or list-valued area, an added `imported_from`, an upper-case ID, as new records with and without a date and with `--import`, two new decisions in one add; each area's draft edited, stale, and given twice; a retirement and a replacement that restores the order; an ID count that does not match; and 150 random line edits of drafts with `--import` at random.
Seeds 1, 2, and 3 (2,745 checks, 921 states, 1,539 applies): every answer agrees, the written files byte for byte (221 and 226 applies wrote files in seeds 1 and 2), except 44 answers where a fuzzed header does not parse and PyYAML's message and, for an unclosed quote, its line differ from the TypeScript parser's (d-p48gr1; Task 4's layer, not these tasks).
A further 80 cases ran `applyDrafts` with an `id`, a new or moved `area`, and a `base` of each of U+0085, U+1D518, U+D800, U+2028, U+FEFF, U+001C, U+007F, a tab, a backslash, quotes, `é`, a list, a map, an empty list, and an empty map: all 80 messages agree with Python's (Review Focus 2).

### Purity (Review Focus 5)

`views.ts`, `apply.ts`, `apply-areas.ts`, `value-repr.ts`, and the three `check-*.ts` modules use no `Date`, `process`, randomness, console, timer, or crypto (`grep -nE`), and `checkChange` and `applyDrafts` take `now` and `date` as stamps.
A Python decision cannot hold a bare day after it is read (`src/lodge/core/fields.py:128-130` widens it to `T00:00:00+00:00`), so `instant` in `check-change.ts:67` and `:84` never meets one from a store; built directly, Python raises `TypeError` there and TypeScript `ValueError`, which no code path reaches.

### The merges at 4e20c28 and 73ab440

`index.ts` at 73ab440 exports `checkChange` (8b), `Applied`, `applyDrafts`, and `StaleBase` (11), and the eleven names of `views.ts` (9a), as each lane added them.
`knip.json`'s `entry` is `tests/**/*.test.ts`, `scripts/*.ts`, and `tests/core/checks.ts`: 8b took out `src/core/check-state.ts`, 11 took out `tests/core/builders.ts`, 7b had taken out `src/core/derive.ts`, and `checks.ts` waits for 8c, as d-tha8st's table says.
`parity.json` gains the 13 flips of the three lanes (5, 3, and 5), with `apply-edits.test.ts` beside `apply.test.ts`; `test_check_threads.py` stays `planned` for 8c.

### `value-repr.ts` against Task 5b's P-1

One `valueRepr` (`value-repr.ts:3-26`) now serves `drafts.ts`, `fileformat.ts` (with `"tuple"`), and `apply.ts`, and both private copies are gone (`git diff 0d1c6c5 854bebe -- ts/src/core/drafts.ts ts/src/core/fileformat.ts`); the mutations above show each mode reached by a test.
`display` (`apply.ts:208-210`) gives Python's `str` where the message has `{x}` rather than `{x!r}` (`src/lodge/core/apply.py:131`, `:206`), which the 80 edge cases confirm.

## Pass 2: practice

### 8b-P-1 · Minor · three private structural `equal`s and three ways of de-duplicating changes

Handle: `ts/src/core/check-entries.ts:8-18`, `ts/src/core/check-immutable.ts:10-20`, and `ts/src/core/fileformat.ts:90-100` (which lacks the `Object.hasOwn` test the other two have); change de-duplication at `check-change.ts:123-127`, `check-entries.ts:55-59` (both `${entry}:${action}` strings), and `views.ts:86-92` (a map of sets), where Python writes `dict.fromkeys(d.changes)` each time.
Each `equal` treats any two `Map`s or `Set`s as equal (`equal(new Map([["a", 1]]), new Map())` and `equal(new Set(["x"]), new Set())` both give `true`, run with Bun), since `Object.keys` of either is empty; no record field holds one today.
Failure: a later round gives a record a `ReadonlyMap` or `ReadonlySet` field, as the Types rule maps `Mapping` and `frozenset`, fixes one copy, and check 4 or check 5 stops seeing a change to that field, as Task 5b's P-1 found two `valueRepr`s drifting apart.
Fix: one `equal` exported from a module of `core` that all three import, with a `Map` and `Set` branch or a throw on them, and one `uniqueChanges(changes)` beside `Change` in `model.ts`, used by the three loops.

### 8b-P-2 · Minor · the problem comparator is written twice

Handle: `ts/src/core/check-state.ts:142-146` and `ts/src/core/check-change.ts:35-39`, the same three-way comparison over `sortKey`.
Failure: a round changes the tie-break in one (as d-qe513h found for order keys), and `lodge check` and `lodge add` list the same problems in different orders.
Fix: `check-state.ts` exports `compareProblems` beside `sortKey`, used by both sorts; it can ride on 8a's fix round under d-qe513h, which already touches `check-state.ts`.

### 9a-P-1 · Minor · `split("\n")` where Python says `splitlines()`

Handle: `ts/tests/core/views-trust.test.ts:46` and `:97`, for `splitlines()[0]` in `tests/core/test_views_trust.py:36` and `:77`; the Text rule sends `splitlines` through `text.ts`.
The headers tested hold no other line break, so both agree today.
Failure: a later fixture puts U+2028 or a CR in a title, and the test reads another first line than Python.
Fix: `splitlines(…)[0]` from `#core`.

### 11-P-1 · Minor · `apply-areas.ts` holds the whole add's state and the refusal helper

Handle: `ts/src/core/apply-areas.ts:8-23` (`Add`, `refuse`), split from `apply.ts`; the brief splits only past 300 lines, and the two files are 210 and 70 lines, about 270 together after the shared imports.
`refuse` is used for decisions, entries, and areas alike (`apply.ts`, 22 calls), and `Add.draftedAreas` is typed `ReadonlySet<unknown>` (`apply-areas.ts:14`) because the name filter at `apply.ts:30-34` loses its narrowing.
Failure: a reader looking for the add's state or its refusals opens `apply.ts` and finds them imported from a module named for areas.
Fix: fold `apply-areas.ts` back into `apply.ts`, or name it for what it holds (the add's state), and narrow `draftedAreas` to `ReadonlySet<string>` with a type predicate in the filter.

### 11-P-2 · Minor · three default sorts where the Text rule asks for code points

Handle: `ts/src/core/apply.ts:40`, `ts/src/core/apply-areas.ts:38` and `:69`, `.sort()` on IDs and area names; every other module of `core` sorts with `byCodePoint`.
Today the values are ASCII (`src/lodge/core/ids.py:6-8`, `src/lodge/core/fields.py:12`), so the order is Python's.
Failure: the area-name or ID alphabet widens, or a caller passes other IDs, and the area files of one add come out in UTF-16 order.
Fix: `.sort(byCodePoint)` at the three places.

## Pass 3: design

### 8b-D-1 · Minor · three behaviours of `checkChange` are pinned by no test, here or in Python

Handle: `ts/src/core/check-change.ts:121` (check 6 reads the published status, not the standing one), `:35-39` (the sort), and `:123-127` (the de-duplication of changes); Python's `check_change.py:122`, `:52`, and `:124`.
Each mutation survives `ts/tests/core`, and its Python twin survives all 1258 non-e2e Python tests.
Failure, for the first: one add holds a decision replacing X and another narrowing X; Python passes it, and a round that reads `standing` refuses it with "narrows X, which is replaced", every gate green.
The differential above agrees on all three today, so this guards later rounds.
Fix: one new test per behaviour (not carried, so seen failing against the mutation), in a second file beside `check-change.test.ts`, listed with it in `parity.json`.

### 9a-D-1 · Minor · the author test of the level 1 quote and the change de-duplication of level 3 are pinned by no test

Handle: `ts/src/core/views.ts:62` (`who && isAuthor(who)`), `:86-92`; Python's `views.py:73` and `:114`, whose twins survive the Python suite.
Failure, for the first: a round drops `isAuthor`, and an agent decision that carries a quote shows it at level 1 and on its entries as if the author had said it, the confusion the trust tests exist to prevent.
Fix: a new test in `views-trust.test.ts`'s neighbour with an agent decision carrying a quote, asserting `quote` is `null` on it and its entry; and one with a decision listing the same change twice, asserting one link.

### 11-D-1 · Minor · the brief's `ValueError` guard is enforced by no test

Handle: `ts/src/core/apply.ts:163-164` and `ts/src/core/apply-areas.ts:53-54`, written as the brief asks (`except ValueError` becomes a `catch` that rethrows anything else); replacing the guard at `apply.ts:164` with a bare `return refuse(…)` survives `ts/tests/core`, and `tests/structure` has no rule over `catch`.
Failure: a round loosens the guard, and a bug in `writeRecord` (a `TypeError`) reaches the agent as an add refusal naming its draft, so the coordinator never sees the crash and the agent edits a draft that is not at fault.
Fix: a structure rule in `ts/tests/structure/calls.ts`, with a refusal and an allowed case, that the first statement of every `catch` clause in `ts/src` rethrows unless the error is an instance of a named class; it covers every guard the Global Constraints require, not this one.

### 11-D-2 · Minor · plan 2 needs `isinstance(p, StaleBase)`, and the only guard is a test helper

Handle: `src/lodge/app/writes.py:174` (`any(isinstance(p, StaleBase) for p in problems)` decides a conflict); in TypeScript `StaleBase` is an interface (`ts/src/core/apply.ts:10-12`) and the guard `isStale` lives in `ts/tests/core/applying.ts:83-85`.
Failure: plan 2's port of `writes.py` writes its own test (`p.stale`, `"stale" in p`, or a message match), and a later change to the marker updates one of the two.
Fix: a coordinator ruling, as d-qe513h did for `checkResult`, that `apply.ts` exports `isStaleBase` beside `StaleBase` and both the tests and plan 2 use it; or plan 2's brief names the test.

### 11-D-3 · Minor · two apply behaviours are pinned by no test, here or in Python

Handle: `ts/src/core/apply.ts:205` (`sameOrigin` compares the heading too) and `ts/src/core/apply-areas.ts:68` (an entry is restored when it is `current`); Python's `apply.py:111`, `:157`, and `:244`, whose twins survive the Python suite.
Failure, for the first: a round compares the file only, and a draft that changes only the heading of `imported_from` passes without `--import`, rewriting the record's provenance with no refusal.
Fix: a second case in a new test beside `edit_changing_imported_from_has_its_own_message`, with the same file and another heading, seen failing against the mutation.

## Files read

- `CLAUDE.md`; `docs/superpowers/plans/2026-11-02-lodge-server-core.md` (Review Focus); `task-8b-brief.md`, `task-9a-brief.md` (task section), `task-11-brief.md` (coordinator notes and task section), their three reports; `task-8c-brief.md` (searched); `task-7b-8a-review.md` (format, 8a-D-1, 8a-D-2); `task-5b-review.md` (C-1, P-1 by `grep`); the ledger by `grep`.
- Decisions through `lodge show`: d-442r2f, d-p48gr1, d-fbhdvf, d-g1hrmn, d-4m6m35, d-0q54zn, d-f18pz7, d-qe513h.
- Python: `src/lodge/core/check_change.py`, `check_entries.py`, `check_immutable.py`, `views.py`, `apply.py`; parts of `snapshot.py`, `model.py`, `fields.py`, `drafts.py`, `yamlio.py`, `ids.py`, `settings.py`, `src/lodge/app/reads.py:105-122`, `src/lodge/app/threads.py:70-100`; `tests/core/checks.py`, `applying.py`, `test_check_change.py`, `test_check_current.py`, `test_check_retired.py`, `test_check_immutable.py`, `test_views.py`, `test_views_links.py`, `test_views_trust.py`, `test_apply.py`, `test_apply_refusals.py`; parts of `test_snapshot.py`, `test_doubts.py`, `test_check_threads.py`.
- TypeScript at 73ab440: `ts/src/core/check-change.ts`, `check-entries.ts`, `check-immutable.ts`, `views.ts`, `apply.ts`, `apply-areas.ts`, `value-repr.ts`, `stamps.ts`; parts of `check-state.ts`, `snapshot.ts`, `model.ts`, `fileformat.ts`, `drafts.ts`, `yamlio.ts`, `text.ts`; `ts/tests/core/checks.ts`, `applying.ts`, `check-change.test.ts`, `check-current.test.ts`, `check-retired.test.ts`, `check-immutable.test.ts`, `views.test.ts`, `views-links.test.ts`, `views-trust.test.ts`, `check-threads.test.ts`, `apply.test.ts` (assertions), `apply-edits.test.ts`, `apply-refusals.test.ts`; the diffs of `snapshot.test.ts`, `doubts.test.ts`, `index.ts`, `knip.json`, and `parity.json`.

## Files not read

- The Codex transcripts `task-8b-codex-final.txt`, `task-9a-codex-final.txt`, and `task-11-codex-final.txt`.
- `ts/tests/core/builders.ts`, `samples.ts`, `derive.ts`, `derive-review.ts`, and `ts/tests/structure/` beyond a listing and a `grep`.
- The rest of the plan, the probes folder, and the earlier reviews other than those named.
- I did not run `sh scripts/check.sh` or `sh scripts/check-ts.sh`; the dispatch reports the gate green at 73ab440, and I ran `bun test tests/core` and the non-e2e Python suite there.
