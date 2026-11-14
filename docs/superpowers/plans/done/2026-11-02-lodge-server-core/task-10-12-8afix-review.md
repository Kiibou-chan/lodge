# Review of Tasks 10 and 12, and recheck of the Task 8a fix round

Reviewer: `reviewer` agent (Opus), task review, three passes in order.
Task 10: `git diff 616b872~1 616b872` on `server-core`.
Task 12: lane `server-core-t12` (71182b0), merged at 9ac3208.
Task 8a fix round 1: lane `server-core-t8afix` (f344014), merged at d625cf3, under d-qe513h; findings answered: 8a-D-1, 8a-P-1, 8a-P-2, 8a-D-2, 7b-P-1, 7b-D-1 (`task-7b-8a-review.md`), and 7a-D-2 (`task-7a-review.md`, handed over in `task-7a-recheck-1.md`).
Probes ran in a detached scratch worktree at 7d5ecbc under `/var/tmp`, removed afterwards; the probe scripts lie outside the repository.
Already ruled and not raised again: d-p48gr1, d-fbhdvf, d-g1hrmn, d-4m6m35, d-0q54zn, d-f18pz7, d-442r2f, d-qe513h, d-0qmd10 (the differential's scope), and the 90 code points `\p{Nd}` takes beyond Python's `\d` (probes 23 and 27, listed in `task-10-report.md`).


## Counts

| Item | Blocking | Important | Minor |
|---|---|---|---|
| Task 10 | 0 | 0 | 2 (10-P-1, 10-D-1) |
| Task 12 | 0 | 0 | 2 (12-D-1, 12-D-2) |
| 8a fix recheck | 0 | 0 | 3 new (8afix-D-1, 8afix-D-2, 8afix-P-1); 6 closed, 8a-P-2 still open |

## Task 12

### What the differential compares, and what it cannot see

It compares five keys, each built the same way on both sides from the files under `lodge/` (`scripts/differential_dump.py:42-84`, `ts/scripts/differential.ts:28-93`): `render_spec` of the store; `check_state`'s problems; for every decision and entry, level 1, level 2, and level 3; `search` for the first word of each title with no filters; and, for each record and area file that parses, the SHA-256 of what `write_record` or `write_area` gives and whether it equals the file.
The key-by-key comparison (`differential.ts:95-113`) reports a missing key or index on either side, so it cannot pass a value that only one side has; key order in an object is not compared, which matches Python's dict semantics for these keys.
At this repository's store, its counts (350 records, 10 areas, 360 rewritten files) are those of the ledger's run, and the store has 0 problems, so the run compares:

- no problem message, no failing ID, and no failing marker in the levels or the specification (the `failing` set is empty);
- no thread at all, and this is by construction, not only because the store holds none: thread files never enter `rewrite` (the path filter at `differential_dump.py:65-76` and `differential.ts:65-73` takes `_area.md`, `decisions/*.md`, and `spec/*/*.md`), and `levels` covers decisions and entries only;
- no `feedback`, `area_feedback`, `check_change`, `apply_drafts`, `confirmation_draft`, `behind_area`, `derived_order`, `parse_draft`, or `search` with filters or another limit;
- no settings: both scripts parse `[length]` and `[import]` and discard the result (`differential_dump.py:48`, `differential.ts:38-40`), since no compared function takes them.

The earlier reviews compared most of the rest on this store and edited variants (`task-7b-8a-review.md`, `task-8b-9a-11-review.md`, `task-8c-9b-review.md`, Task 6's 1,207 built threads); `feedback` and `area_feedback` had no comparison until this review's (Task 10 below).
Run here: `uv run --frozen --quiet python scripts/differential_dump.py "$PWD"` and `bun ts/scripts/differential.ts "$PWD" <dump>` at 7d5ecbc print the ledger's two lines.

## Counts, Task 12

| Blocking | Important | Minor |
|---|---|---|
| 0 | 0 | 2 |

## Pass 1: correctness (Task 12)

No correctness finding.
The scripts follow the plan's interface (plan, Task 12) and d-0qmd10, which scopes the run to record and area files and accepts that the store holds no threads.
`differential.test.ts` was written first and seen failing (report), and its two tests use temporary made-up stores only.

## Pass 2: practice (Task 12)

No practice finding beyond 12-D-2.

## Pass 3: design (Task 12)

### 12-D-1 · Minor · the count line says threads were compared when no thread is ever compared

Handle: `ts/scripts/differential.ts:115-117` prints `${snapshot.threads.size} threads` among the counts "compared" (plan, Task 12 interface: "printing the counts of records, areas, threads, problems, queries, and rewritten files compared"); thread files are filtered out of `rewrite` at `differential.ts:65-73` and `scripts/differential_dump.py:65-76`.
Run in the scratch worktree: a made-up store of one area, one entry, one decision, and two threads (`files_of` of `tests/core/builders.py`) gives `2 records, 1 areas, 2 threads, 1 problems, 2 queries, 3 rewritten files` and `0 differences`; with `writeThread`'s `"kind: thread"` line changed to `"kind: thread-x"` (`ts/src/core/threads.ts`), it prints the same two lines and exits 0.
Failure: plan 4 or a later round runs the differential on a store that holds threads (an imported project, or this one once a thread is opened), reads `N threads, … 0 differences`, and takes `writeThread` as checked against lodge 0.2, which Review Focus 7 also says Task 12 does.
Fix: either add thread files to `rewrite` through `parse_thread` and `write_thread` on both sides (a few lines each, the same shape as the record branch), or print threads as loaded rather than compared; the first also needs d-0qmd10's scope widened by the coordinator.

### 12-D-2 · Minor · the TypeScript gate now needs uv and lodge 0.2's Python

Handle: `ts/scripts/differential.test.ts:43-55` spawns `uv run --frozen --quiet python scripts/differential_dump.py` inside `bun test`, which `scripts/check-ts.sh` runs; the Global Constraints describe the builder's gate as Biome, `tsc`, dependency-cruiser, knip, and `bun test`, "all on Bun".
Run: with `PATH` holding only `bun`, `bun test scripts/differential.test.ts` gives `Executable not found in $PATH: "uv"` and `1 pass, 1 fail`.
Failure: plan 3's compiled-binary build, a CI image with Bun alone, or the later removal of lodge 0.2's Python fails the TypeScript gate on a script that is not shipped (d-0qmd10: "a script that is not shipped").
Fix: keep the cross-language half of the test out of `bun test` (run it from `scripts/differential.sh` or `scripts/check.sh`, which already needs both), leaving `differential.test.ts` with the TypeScript-only comparison; or skip it with a named reason when `uv` is missing, which the coordinator rules on since d-xk6qtn prefers stopping to skipping.

Not raised: `differential.test.ts` writes under `tmpdir()`, which fails with a read-only `TMPDIR` (probe 13); the structure tests already do the same (`ts/tests/structure/plant.ts`, `calls.test.ts`: 10 or more fail under a read-only `TMPDIR` at 7d5ecbc), so probe 13's claim was already false before Task 12 and is the coordinator's to correct, not this task's.

## Recheck of the Task 8a fix round (f344014)

### Verdict

Closed 6 (8a-D-1, 8a-P-1, 8a-D-2, 7b-P-1, 7b-D-1, 7a-D-2), open 1 (8a-P-2, parked and still open), new 3 Minor (8afix-D-1, 8afix-D-2, 8afix-P-1).
No new Blocking or Important problem.

### Findings answered

- 8a-D-1: closed.
  `checkResult(problems, notes)` returns plain data with `ok: problems.length === 0` (`ts/src/core/check-state.ts:12-14`), and `checkState` (`:150`) and `checkChange` (`check-change.ts:47`) return through it; no getter is left (`grep -rn 'get ok' ts/src ts/tests`: none), and no `CheckResult` literal is built by hand in `ts/src` or `ts/tests` (`grep -rn 'ok:'`: only the two expected values of `check-state-order.test.ts:9-10`).
  Mutations, each alone against `tests/core`: `ok: true` in `checkResult` fails 6 tests; `checkChange` returning `{ problems, notes, ok: true }` fails `decision_edit_changing_statement_is_judged_by_the_check`; `checkState` doing so fails 4.
- 7a-D-2: closed.
  `compareOrderKeys` (`derive.ts:29-33`) is the one comparator; `derive` (`:85`), `cleared` (`:223`), `behindArea` (`confirmation.ts:34-36`), and the changed-since flag (`views.ts:204-207`) use it, and `orderKey` is private.
  Mutations: the tie-break reversed fails 3 tests (among them `orders_by_instant_across_offsets_then_by_id` and `behind_area_same_date_uses_id_tie_break`), the tie-break dropped fails 2, `behindArea` unsorted or reversed fails 2, and `views.ts` with `who` in place of the forged ID, or `>=` for `>`, fails `same_second_change_does_not_mark_changed_since`.
- 7b-P-1: closed.
  `confirmation.test.ts:125-128` asserts `toThrow(LookupError)` and the message; the report shows it failing with `IndexError` extending `Error`.
- 8a-P-1: closed.
  `oldDecision` checks `kind` and throws (`ts/tests/core/checks.ts:31-35`, the guard at `:33`); see 8afix-P-1 for the test added beside it.
- 8a-D-2: closed.
  `check-state-order.test.ts:15-50` asserts the whole problem list over two paths, three check numbers, a repeated missing `rests_on` target, a repeated missing attachment, and U+E000 against U+1D518 in paths and messages; the report's seven mutations (sort removed, path, check, or message comparison dropped, UTF-16 comparison, either set removed) each fail it, and the file is listed with `check-state.test.ts` in `parity.json`.
- 7b-D-1: closed outside this lane.
  Plan 2 (`server-store`, `docs/superpowers/plans/2026-11-02-lodge-server-store.md:259`, `:317`, `:359`) adds `minuteOf(now)`, `strftime(MINUTE_FORMAT)` in the offset's own time, with `minute_is_local_to_the_offset` and `minute_crosses_midnight`.
- 8a-P-2: open.
  The added check 8 test is still at `ts/tests/core/check-state.test.ts:259-271`; the fix round left it for Task 8c, whose brief and report do not mention it, and 8c's review does not either.
  It stays parked for the final fix wave, with 8b-P-2 (the problem comparator written twice, `check-state.ts:146-150` and `check-change.ts:41-45`), which this round touched both files of and did not take.

### 8afix-D-1 · Minor · `checkResult` in `#core` is recorded nowhere, and two decisions say otherwise

Handle: `ts/src/core/index.ts:3` exports `checkResult`, and `ts/tests/core/front-door.test.ts:39` allows it as a tenth constructor; d-qe513h's reasoning says the two exports are "read inside the package only", d-ca6wbw says `#core` exports nine default-filling functions, and d-hshapm says "nothing else"; `lodge search checkResult` finds only d-qe513h.
`checkResult` is not a default-filling function (`CheckResult` has no defaulted field; Python's `ok` is a property, `src/lodge/core/check_state.py:20-22`), so the front-door test's list now holds a name its rule does not describe.
Failure: plan 2's builder, reading d-ca6wbw and d-qe513h, drops the export as unplanned or stops BLOCKED on it, or, finding the rule loosened silently once, adds an eleventh name to the list the same way.
Fix: a coordinator decision replacing d-qe513h (or narrowing d-ca6wbw) that `#core` exports `checkResult` as `CheckResult`'s constructor, for the views tests and for plan 2's `app/state.py:69` and `app/reads.py:96`, with the ledger line naming it.

### 8afix-D-2 · Minor · "every place that builds a check result uses it" is held by no check

Handle: d-qe513h requires every constructor to go through `checkResult`; `CheckResult.ok` is still a writable-at-construction field (`check-state.ts:7-11`), so `{ problems, notes, ok: true }` and `{ ...result, problems: [p] }` both type-check; plan 2's plan names neither `checkResult` nor the rule (`git grep checkResult server-store -- docs/superpowers/plans/2026-11-02-lodge-server-store.md`: no hit).
Failure: plan 2's port of `CheckResult(problems, notes)` at `src/lodge/app/state.py:69` writes the literal, and `lodge check` reports `ok` over a failing store, the failure 8a-D-1 named, with every gate green.
Fix: plan 2's brief for `state.py` and `reads.py` names `checkResult`; or a structure rule in `ts/tests/structure/` that refuses an object literal with an `ok` key in `ts/src` outside `check-state.ts`, with a refusal and an allowed case.

### 8afix-P-1 · Minor · two practice points in the fix's own lines

Handle: `ts/tests/core/check-state-order.test.ts:12-14` (`old_decision_requires_a_decision`) and `ts/src/core/views.ts:203-207`.
The test asserts only that `baseItems()[2]` is a decision today; removing the guard it was added for (`checks.ts:33`) leaves it passing (run: survives `tests/core`), so it tests the fixture, not the helper, and every Task 8b test calling `oldDecision` already fails on a reorder.
The changed-since flag builds a `Decision` with another decision's ID (`{ ...who, id: changes[0] }`) so that `compareOrderKeys` falls through its tie-break to zero, with a comment explaining the trick; Python compares the instants alone (`src/lodge/core/views.py:223`, `order_key(...)[0]`).
Failure: a later round adds a third key to `compareOrderKeys` (the file path, say, to separate duplicate IDs), and the changed-since flag silently compares it too; the reader of `views.ts` meets a forged record where a comparison of two stamps was meant.
Fix: delete `old_decision_requires_a_decision`; write the flag as `orderInstant(changed.date) > orderInstant(who.date)` with `orderInstant` of `stamps.ts`, which `same_second_change_does_not_mark_changed_since` still pins (the ruling's "reuse it" was about sorts, which this is not).

## Task 10

## Counts, Task 10

| Blocking | Important | Minor |
|---|---|---|
| 0 | 0 | 2 |

## Pass 1: correctness (Task 10)

No correctness finding.

### Carried tests against the Python ones (Review Focus 1)

All 23 tests of `test_feedback.py` (19 in `feedback.test.ts`, 4 in `feedback-edit-back.test.ts`, both listed in `parity.json`), 3 of `test_feedback_links.py`, 10 of `test_feedback_revival.py`, 3 of `test_area_feedback.py`, and `thread_id_is_not_number_feedback` are carried by name; none of the four files is parametrised; both loops of `shared_rank_feedback` and both links of `related_silent_when_it_replaces_or_narrows` are kept.
Every `==` on a whole list is `toEqual`, Python's `next(...).startswith(...)` is `[0]?.startsWith(...)` with `toBe(true)` (which fails on an empty list, as `next` raises), `message[:30]` and `[:50]` are `slice(0, 30)` and `slice(0, 50)` on ASCII text, and `not any(...)` is `!….some(Boolean)` with `toBe(true)`.

### `feedback.ts` against `feedback.py`

The patterns follow the Text rules: `\b` as `START` and `END` from `WORD_CLASS`, `\d` as `\p{Nd}`, `\s` as `PY_SPACE_CLASS`, `re.DOTALL` as the `s` flag, every pattern with `u` (`feedback.ts:16-26`); the module-level `g` patterns are used only with `match` and `replace`, which reset `lastIndex`, so no call leaks state into the next.
The messages keep Python's order (title, then statement, reasoning, related, numbers, already replaced, edit back, revival, waiting) and text; `codePointLength` and `splitWords` count, and `byCodePoint` sorts.

### Python against TypeScript (Review Focus 2)

A Python script built 2,426 comparisons and a Bun script ran the same files through `#core`, comparing `[recordId, message]` lists as JSON:

- the repository's store at 7d5ecbc, loaded and derived once: `feedback` of every decision and entry alone under the default guidance and under the tight guidance of `test_feedback.py`, of all records in one call, and `area_feedback` with every area written (352 records, 706 comparisons);
- a made-up store (the `storage` area, two entries, three decisions with the codes `ITEM-1`, `RFC-2119`, and `Z9-10`) with an added decision and entry whose statement, reversed reasoning, and title come from 20 texts and 6 titles, with and without a numbers handle and a `replaces`, under both guidances (720 cases): digits after letters, `_`, `²`, and astral letters; Arabic-Indic, Devanagari, fullwidth, mathematical, Brahmi, and N'Ko digits; `%` after NBSP, U+2028, U+001C, U+0085, U+3000, and a tab; codes in other cases and glued to words; dates with and without times; IDs glued to `x`, `_`, and `é`; combining marks; inline and fenced code spans with newlines; words split at NBSP, U+2028, U+001C, U+0085, ZWSP, and U+FEFF; titles of 21 astral letters, of combining sequences, of 21 U+FEFF, and of `ﬃ`;
- 200 random sets of areas with shared and missing ranks and random written paths (400 comparisons, `feedback` with nothing added and `area_feedback`);
- 600 random stores of three entries and five decisions, each by the author or an agent, creating, editing, and retiring entries, replacing earlier decisions or a missing one, some on the same minute, with `feedback` of the last (600 comparisons: 48 edit-back, 119 revival, 382 already-replaced, 131 waiting, and 35 related messages).

Every comparison agrees; the first three groups alone hold 3,941 messages, among them 949 title, 583 statement, 328 reasoning, 1,086 related, 618 numbers (71 distinct), 36 named-entry, and 341 shared-rank messages.

### Targeted mutations (d-mfayy5)

40 mutations of `feedback.ts`, each alone against `ts/tests/core` and reverted.
Nineteen fail a carried test, among them: the `%` part of `NUMBER` dropped, the `s` flag of `CODE_SPAN` dropped, the self filter of "already replaced", the last-replacer and status tests of the revival line, `split(" ")` for `splitWords`, the Oxford comma, `area_feedback`'s written-path test, each of the four tests of the named-entry line, the plural of the related line, the `narrows` gate, the waiting line, the date's time and offset parts, and the numbers-handle gate.
Twenty-one survive; their Python twins are under 10-D-1.

## Pass 2: practice (Task 10)

### 10-P-1 · Minor · three test idioms say less plainly what Python says

Handle: `ts/tests/core/feedback-revival.test.ts:116-120` and `:131` (`expect(!found.map((f) => f.message.startsWith("it replaces")).some(Boolean)).toBe(true)` for `not any(...)`); `ts/tests/core/area-feedback.test.ts:6` (`snapshotOf([...[…].map(…)])`, a spread of a fresh array); `ts/tests/core/feedback.test.ts:166-170` and `:198-199` (`toBe(true)` on `startsWith`).
None weakens an assertion, but a failure prints `expected true, received false` with no message, where `expect(found.some((f) => f.message.startsWith("it replaces"))).toBe(false)` or `expect(message).toStartWith("the text holds the number 1.5 ")` prints the text.
Failure: a later round breaks the number message, and the failing test shows `false` instead of the message it got, so the fixer reruns with prints.
Fix: `toStartWith` for the four `startsWith` checks, `.some(pred)` with `toBe(false)` for the two `not any`, and drop the spread.

## Pass 3: design (Task 10)

### 10-D-1 · Minor · most of the number scan and the edit-back question are pinned by no test, here or in Python

Handle: `ts/src/core/feedback.ts`, 21 mutations surviving all of `ts/tests/core` (674 tests), each with its Python twin in `src/lodge/core/feedback.py` surviving all 1258 non-e2e Python tests (`uv run --frozen --quiet pytest -q tests -k "not e2e"`, each twin applied alone):

| TypeScript mutation | Python twin |
|---|---|
| `START` dropped from `NUMBER` (`:26`); `END` or `START` dropped from `CODE` (`:21`); `END` dropped from `ID` (`:19`); `START` dropped from `ENTRY_ID` (`:20`) | `\b` dropped from `_NUMBER`, `_CODE`, `_ID` (`:15-20`) |
| the hidden patterns applied in another order (`:150`); codes matched case-sensitively (`:151`); numbers not de-duplicated (`:152`) | `:188`, `:190`, `:176` |
| `PY_SPACE_CLASS` replaced by JavaScript's `\s` (`:26`); the title counted in UTF-16 units (`:48`) | none (a TypeScript-only rule) |
| the edit-back question asked of an agent's decision (`:92`), or about an author's edit (`:96`), or about an entry this decision itself changes (`:101`); edits left unsorted (`:100`); `CREATE` no longer a text change, or the entry test dropped (`:110-111`) | `:100`, `:105`, `:109`, `:108`, `:19`, `:121` |
| the revival line kept for an entry this decision changes (`:121`) | `:130` |
| `area_feedback` keeping unranked areas (`:165`), or either sort dropped (`:164`, `:169`) | `:198`, `:197`, `:200` |
| the specification word limit as `>=` (`:64`) | `:60` |

So the port asserts no less than Python here (Review Focus 1), and the differential above finds today's code in agreement on all of these; this guards later rounds.
Failure, for the sharpest: a round drops `isAuthor(decision)` at `:92`, and every agent decision that replaces another agent's edit is told to "edit it back", the author's question, with every gate green; or `START` leaves `NUMBER`, and `x3` in a statement asks for a numbers handle for `3`.
Fix: new tests (not carried, so each seen failing against its mutation) in a file beside `feedback.test.ts`, listed with it in `parity.json`: an agent replacing an agent's edit (no question), an author replacing an author's edit (no question), two edited entries out of order (sorted), `x3 item-1 4\u00a0% 5 5` against the code `ITEM-1`, its expected message taken from lodge 0.2, a 21-letter astral title, and an unranked area beside a ranked one.

## Files read

- `CLAUDE.md`; the plan (Global Constraints, Calls made, Review Focus, Tasks 7a to 8c, 10, 11, and 12); the ledger; `task-10-brief.md`, `task-10-report.md`, `task-12-brief.md`, `task-12-report.md`, `task-8a-fix-1.md`, `task-8a-fix-1-report.md`, `task-7b-8a-review.md`, `task-7a-recheck-1.md`, `task-7a-review.md` (D-2), `task-8b-9a-11-review.md` (format, 8b-P-2), `task-8c-9b-review.md` (searched); `probes.md` items 13 and 14.
- Decisions through `lodge show` or `lodge search`: d-qe513h, d-0qmd10, d-ca6wbw, d-s2rdn2, d-hshapm (by search), and `lodge search checkResult`.
- Python: `src/lodge/core/feedback.py`; `tests/core/test_feedback.py`, `test_feedback_links.py`, `test_feedback_revival.py`, `test_area_feedback.py`, `test_thread_files.py:198-201`; parts of `builders.py`, `settings.py`, `fields.py`, `document.py`, `check_state.py`, `views.py:223`; `scripts/differential_dump.py`, `scripts/differential.sh`.
- TypeScript at 7d5ecbc: `ts/src/core/feedback.ts`; `ts/tests/core/feedback.test.ts`, `feedback-edit-back.test.ts`, `feedback-links.test.ts`, `feedback-revival.test.ts`, `area-feedback.test.ts`, `check-state-order.test.ts`; `ts/scripts/differential.ts`, `differential.test.ts`; the diffs of f344014 (`check-change.ts`, `check-state.ts`, `confirmation.ts`, `derive.ts`, `index.ts`, `views.ts`, `checks.ts`, `confirmation.test.ts`, `views.test.ts`, `parity.json`) and of 616b872 (`thread-files.test.ts`, `parity.json`); parts of `text.ts`, `views.ts`, `threads.ts`, `front-door.test.ts:25-45`, `check-state.test.ts` (test names).
- Plan 2 on `server-store`: `docs/superpowers/plans/2026-11-02-lodge-server-store.md` by `git grep` for `MINUTE_FORMAT`, `minute`, `checkResult`, and `CheckResult`.

## Files not read

- The Codex transcripts `task-10-codex-final.txt`, `task-12-codex-final.txt`, and `task-8a-fix-1-codex-final.txt`.
- `ts/tests/core/builders.ts`, `checks.ts` beyond the diff, `ts/tests/structure/` beyond a `grep` for `tmpdir`, and the rest of `ts/src/core`.
- The rest of plan 2, plans 3 and 4, the probes folder beyond items 13 and 14, and the earlier reviews other than those named.

## Commands run

- `bun test tests/core` at 7d5ecbc in the scratch worktree: `674 pass, 0 fail`.
- `sh scripts/check-ts.sh` in the scratch worktree: Biome, `tsc`, dependency-cruiser, and knip passed, `853 pass, 0 fail`; I did not run `sh scripts/check.sh` (the Python half ran as the non-e2e suite, `1258 passed`).
- The two differential scripts on the repository (the ledger's two lines) and on the made-up store with threads (12-D-1); `bun test scripts/differential.test.ts` with `PATH` holding only `bun` (12-D-2) and with a read-only `TMPDIR` (the note under 12-D-2).
