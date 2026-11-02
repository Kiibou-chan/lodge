# Preflight scan of plan 2 (server-store at 5af878e)

Scope: the plan as it stood at 5af878e against plan 1's code at `/var/tmp/lodge-server-core/ts` (core branch HEAD 7d5ecbc; the cited `derive.ts:153` is unchanged).
Python sources and tests were read in the `server-store` worktree.
Rows marked **RECHECK-R3** touch Tasks 11, 12a, or 12b and are to be rechecked after fix round 3 (the author's STORE-1 answer, d-2v8vtk).
Nothing was run beyond greps, one `sha256` check (probe 7's `518254327818` reproduces), and line counts; no builds.

## 1. Pairs of tasks sharing a file or an interface

| # | Earlier -> later | Produces / Consumes | Finding |
|---|---|---|---|
| P1 | 1 -> 7a | `kysely` 0.29.7 in `ts/package.json`; `ts/knip.json` `ignoreDependencies` gains it (T1), loses it (7a) | match: `ignoreDependencies` is `[]` today in plan 1's `knip.json` |
| P2 | 2 -> 3 | `Store`, `Clock`, `IdSource`, `Now`, `stampOf`, `Added`/`AddOutcome`, `LodgeError`/`Conflict`, `MemoryStore`, `FixedClock`, `CountingIds`, `START`; `#app` index | match, with one placement slip: `add_fills_id_and_date_from_ports` (T3) uses `START.replace(microsecond=999_999)` (`tests/app/test_writes.py:32`), but the translation "START plus 999 ms" is written in T4 (plan line 309) |
| P3 | 2 -> 4 | `Read`/`read`, `Shown`, `Listed`/`listed`, `ThreadList`, `ThreadShown`, `ThreadsWaiting`, `Written`/`written`, `minuteOf`, `NotFound`, `coreSettings` of `#app` | match; `ThreadsWaiting` fields `forAgent`/`forAuthor` agree with `results.py` |
| P4 | 3 -> 4 | `state.ts` `readChecked`, `resolveRef`, `notFound`, `Wiring`, `State`; `writes.ts` `mintUnused`; `support.ts` `ENTRY`; `Lodge` | match with an ambiguity: plan 279 puts `Wiring` in `state.ts` (as `state.py:24` has it), plan 285 says "`lodge.ts` holds `Wiring`". If it were declared in `lodge.ts`, `state.ts`/`writes.ts` would import it back and `no-circular` (`.dependency-cruiser.cjs:40`, `tsPreCompilationDeps: true`) would fail. Fix: say `lodge.ts` holds a `Wiring` value, declared in `state.ts` |
| P5 | 3 -> 4 | the 13 T3 tests and the 6 T4 tests of `test_writes.py` | match: 13 + 6 = 19 `def test_` (grep); the 13 call only `add`/`mint`; the 6 call `draft` (T4); `writes-attach` (6) calls neither `draft` nor later methods |
| P6 | 3 -> 4 | knip `entry` table: `fakes.ts` first read (3), out of `entry` (4) | mismatch (Minor): all four `fakes.ts` names (`MemoryStore`, `FixedClock`, `CountingIds`, `START`) are read by T3's tests (`test_writes.py:6`), so by d-tha8st `fakes.ts` should leave `entry` in T3, not T4. Harmless (an extra `entry` line), but the table contradicts its own rule |
| P7 | 4 -> 5 | no new name; `thread-ops` split at line 156 | match: `test_thread_ops.py` first file lines 28-149 (17 defs), second 156-245 (12 defs), 29 in all; every call is `add/ask/reply/close/thread(s)/threadsWaiting/search/show/timeline`, all T3/T4 |
| P8 | 5 -> 6 | `lodge.ts`, `index.ts`, `parity.json` rows | match |
| P9 | 3, 4 -> 6 | `state.ts` `readState`, `notFound`; `confirmationDraft(confirms, scope, words, when, area)` of `#core`; `minuteOf` | match: `confirmation.ts:38` takes exactly five parameters in that order |
| P10 | 2 -> 7a | `LodgeError` for `schema.ts`'s refusal; `#app` front door | match (`store` may import `#app`, `table.ts` `["store", ["app","core"]]`) |
| P11 | 7a -> 7b | `LodgeDatabase`, `Tables`, `openDatabase`, `rebuild`, `appendEvents`, `json`, `encodeUtf8`/`decodeUtf8`; `MIGRATIONS` and `NewEvent` unexported | match; `events.ts` in `knip` `entry` 7a, out 7b (both read in 7b) |
| P12 | 3 -> 7b | `Lodge.add`, `AREA`, `wired` of `support.ts`; `decisionText`/`specText`/`filesOf` of plan 1 | match: `decisionText` (`tests/core/applying.ts:32`) writes `decided_by: coordinator`, as the T7b test says; a `reviewer` decision needs the `decision({ decidedBy })` builder instead (`builders.ts:35`), which exists |
| P13 | 2 -> 7b | `stampOf`, `actorText`, `Actor`, `Role`, `Projects`, `Clock`, `Store`, `PublishOutcome`, `gate`, `committed`, `CommitOutcome`, `NotFound`, `Conflict` | match |
| P14 | 7b -> 8 | `SqliteStore`, `SqliteProjects`, `openDatabase`; `Interleaved`/`Interleaving` over any `Store` | match |
| P15 | 8 -> 9 | `Interleaved(inner, during, drafts)`, `Interleaving` (`attempts`, `publishes`, `rejectNext`, `movesAfterRead`, `files()`); `interleaving.ts` into `entry` (8), out (9) | match. Minor: `rejectNext({})` (used by `test_thread_ops.py:159`, a MemoryStore test in T5, not T9) would land an empty `publish`, which appends no event and moves no `rev`, so it rejects nothing; no T9 test passes an empty change |
| P16 | 6 -> 9 | `Lodge.confirm`, `check`, `problems`, `show`, `search`, `timeline`, `draft` | match: 9 waits for 6 and 8 |
| P17 | 6 -> 9 | `writes-retry` (8 titles), `reads-published` (6) | match: grep gives 8 and 6 `def test_` |
| P18 | 8 -> 9 | cites `tests/app/test_writes_retry.py:43-48` for "asserts an attachment path" (plan 456) | mismatch (Minor): the assertion is at line 67 (`test_ref_moving_between_reads_retries`); lines 43-48 are `test_add_retry_concurrent_edit_of_same_entry_conflicts` |
| P19 | 9 -> 11 | every `Lodge` of `ts/tests/store/*.test.ts` gets `person("author")`; `wired` gets the actor | match in text; `reads-published` and `writes-retry` (in `tests/app/`) use `wired`, so they are covered. **RECHECK-R3** |
| P20 | 3, 4 -> 11 | `Wiring` carries the actor for `threads.ts` and `confirm.ts` | mismatch (Important-ish): T11's Files omit `ts/src/app/state.ts`, where `Wiring` lives (`state.py:24`; plan 279). Either name it or say where the actor travels. **RECHECK-R3** |
| P21 | 10 -> 11 | `Tree.people`, `Snapshot.people`, `isAuthor(d, people)`, `parseThread`/`writeThread(…, people)`, `confirmationDraft(…, person)` | match (all trailing and defaulted); `confirmationDraft` today has five parameters. **RECHECK-R3** |
| P22 | 10 -> 3, 4 (lane A) | trailing defaulted `people` so one-argument `writeThread(thread)` and `tree({…})` compile | match for `src/`; but see T10 row: `ts/scripts/differential.ts:41` is a `Tree` literal |
| P23 | 10 -> 7b | `readTree` builds `tree({ rev, files, attachments })` | match (defaults fill `people`) |
| P24 | 11 -> 12a | `MemoryStore` `people` option, `support.ts` `wired(…, actor)`, `fakes.ts` | match. **RECHECK-R3** |
| P25 | 12a -> 12b | `HeldDraft`, `Held`, `Store.hold/held/decline`, `publish(…, approves)`, `MemoryStore` holds | match; open point: `held()` returns `at`, but `MIGRATIONS[1]`'s `held` table has no `at` column (plan 578), so `held()` must join `events` on `seq`; not stated. **RECHECK-R3** |
| P26 | 12b -> 2 | `added()` default-fills `awaits`/`held` with `null`; `AddOutcome.HELD` | match (T2's test covers only the T2 defaults; 12b must extend it, not listed in 12b's Files). Minor. **RECHECK-R3** |
| P27 | 10 -> 13 | `people.ts`, `derive.ts`, `views.ts`, `feedback.ts` | match; sizes today `derive.ts` 238, `views.ts` 220, `feedback.ts` 177 lines against the 300 limit, so per-person logic in `derive.ts` may need a split (Minor risk) |
| P28 | 13 -> 11 | feedback first words `this decision will wait for` | match: `feedback.ts:89` today reads "this decision will wait for the author: …" and T10/T13 keep the prefix. **RECHECK-R3** |
| P29 | 2 / 7a (parallel lanes) | both edit `ts/package.json` `imports` and `ts/knip.json` `entry` (a single-line array today) | risk (Minor): textual merge conflict between lanes A and B on first merge; the integrator resolves it |
| P30 | 7a -> plan 1 structure tests | `STORE_NPM` beside `CORE_NPM` in `tests/structure/table.ts`; `store-imports` rule; `table.test.ts` | match: `CORE_NPM` form and `.dependency-cruiser.cjs` `require` of `table.ts` exist; `sqlite-confinement` already allows `^src/store/` (line 73) |
| P31 | 8, 9 -> 14 | `parity.json` rows (`changed`, plan 2) and `knip` `entry` closing state | match for `entry` (every plan-2 addition leaves: fakes 4, support 4, state 4, writes 4, events 7b, interleaving 9). Minor: T8 and T9 list `parity.json` under Modify while saying the rows "stay `changed`", so nothing is edited; and T14's `grep -c '"planned"'` cannot show which plans the rows belong to |
| P32 | 9 -> parity test | `parity.test.ts` extended so a `changed` row with `plan` 2 is held to the `ported` rules | match: today `ported_files_exist` already takes `changed` plan 1 only (`parity.test.ts:41`); `rowMissing` reads the Python names, which the three plan-2 `changed` rows keep |
| P33 | 6 -> 14 | front-door allow-list: default-filling functions, `Now`, `Actor`, `person`, `agent`, `actorText`, `Role`, `Projects`, `stampOf`, `minuteOf`, `Forbidden`, `HeldDraft`, `Held` | match with the Interfaces block (same 18 additions); `Forbidden` (T11) and `HeldDraft`/`Held` (12a) are allowed before they exist. **RECHECK-R3** |

## 2. Each task against itself

| Task | Own text agrees? | Finding |
|---|---|---|
| 1 | yes | Files, steps, and the verifying `grep -c '"[~^]' ts/package.json` agree (no `^` or `~` in plan 1's file today) |
| 2 | yes | Files create all three test files named in Step 1; the five `ports.py` methods plus `attachmentTexts` equal the six `Store` methods; `START` needs `instant` and `isStamp`, both exported by `#core` (`stamps.ts:24`, `:14`). Lane A, waits for 1, tests import `#app`, `#core`, `tests/core/builders.ts` only |
| 3 | mostly | 13 tests + `writes-attach` (6) need only `add`, `mint`, fakes, `support.ts`; matches the wait on 2. Slips: the `START.replace` translation sits in T4 (P2); `wired` is typed by `Store`, as T9 needs |
| 4 | mostly | 11 + 13 = 24 `test_reads.py` tests split at line 142/143 as stated; 6 + 6 mutation-checked write tests; `reads.py:128` sorts `(date, id)` with `reverse=True`, so the ID tie-break is descending too, which "as plan 1's `newestLast`" (ascending) does not say; `writes-dates` needs `NEWEST` as a `Now` with `offsetMinutes` 60 (`at()` is `+01:00`, `builders.ts:33`), unstated; plan 306 attributes a `fromisoformat` ordering to `threads.py`, which has none (only `reads.py:128` and `writes.py:149`) |
| 5 | yes | 29 tests split correctly; `thread-fix-paths` 1 test + 2 `test.todo`; row `plan` 3 allowed by `planned_rows_name_a_plan` |
| 6 | yes | `confirm` and `behindArea` complete the 19 `Lodge` methods (3 + 14 + 2); front-door path "`../src/lodge/app/__init__.py`" is written root-relative while plan 1's test resolves it from `root = ../../..` (harmless) |
| 7a | yes | Files cover every item in Step 1 (`bytes`, `database`, `imports`, `table` tests); probe 7's seven and probe 11's three byte strings match `probes.md`; `518254327818` reproduces by `sha256(b"a\x80\n")`. `tests/core/bytes.test.ts` is in plan 1's folder, allowed since `text.ts` names pass its front-door test |
| 7b | yes, one risk | 8 `check_writes` cases in `path_outside_lodge_is_refused`, thirteen tests in `sqlite-store.test.ts`: likely to exceed 300 lines (`sizeViolations`, `calls.ts`), splitting not planned. `publish` calls only Kysely `execute`; no name in `calls.ts`'s `writes` set |
| 8 | yes | three titles equal `test_concurrent.py` (87, 99, 109); `Interleaved` takes `drafts` where Python holds `A_DRAFTS` (line 35); `parity.json` listed under Modify but unchanged |
| 9 | yes | six + eight + four tests; waits 6 and 8 cover every import; Step 2's mutations named |
| 10 | no (one gap) | `ts/scripts/differential.ts:41` builds `load({ rev: null, files, attachments: new Set() })`, a `Tree` literal; once `Tree.people` is required, `tsc` (which includes `scripts`, `tsconfig.json`) fails in T10's Step 4. Not in the Files list or the Step 3 grep (`ts/src/core` only). Fix: list `ts/scripts/differential.ts` (pass `people`, or use `tree({…})`). All other `isAuthor`/`parseThread`/`writeThread`/`tree({` callers are in the listed files (grep) |
| 11 | no (one gap) | Files omit `state.ts` (P20). **RECHECK-R3** |
| 12a | yes | Files cover the nine changes; `held` table lacks `at` that `held()` returns (P25). **RECHECK-R3** |
| 12b | yes | import order `held.ts -> writes.ts -> awaits.ts` has no cycle given `Wiring` in `state.ts`; twelve titles listed equal twelve in Step 1. **RECHECK-R3** |
| 13 | yes | Files and Step 1 (eight tests) agree; lane C only |
| 14 | yes, weak check | the `"planned"` count check (P31) |

## 3. Names consumed from plan 1 (`/var/tmp/lodge-server-core/ts/src/core`)

| # | Name | Exists? (file:line, signature) |
|---|---|---|
| N1 | `Tree`, `tree()` | `snapshot.ts:12`, `:17`: `tree(value: Omit<Tree,"attachments"> & Partial<Pick<Tree,"attachments">>)`; `rev: string | null` |
| N2 | `load` | `snapshot.ts:44`: `(tree: Tree): Snapshot`; unions `tree.attachments` with files under `lodge/attachments/` |
| N3 | `Snapshot` | `snapshot.ts:20` (no `people` yet; T10 adds) |
| N4 | `instant`, `isStamp`, `orderInstant` | `stamps.ts:24`, `:14`, `:~40`: `(stamp: string): number` in ms |
| N5 | `parseCoreSettings`, `SettingsError`, `coreSettings`, `CoreSettings` | `settings.ts:35`, `:2`, `:24`, `:20` |
| N6 | `ValueError` | `errors.ts:1` |
| N7 | `pyRepr`, `byCodePoint` | `text.ts:76`, `:93` |
| N8 | `contentHash` | `fileformat.ts:78`, uses `new TextEncoder()` (T7a swaps in `encodeUtf8`) |
| N9 | `newestLast`, `appended`, `cleanText`, `threadPath` | `threads.ts:156`, `:146`, `:143`, `:22` |
| N10 | `parseThread`, `writeThread` | `threads.ts:25` `(path, text)`, `:107` `(thread)`; T10 adds trailing `people` |
| N11 | `isAuthor` | `derive.ts:153` `(d: Decision): boolean` |
| N12 | `derive`, `Derived` | `derive.ts:84`, `:13` (`awaitingAuthor` at `:19`) |
| N13 | `checkChange` | `check-change.ts:18` `(published, after, settings, now: string, current: Snapshot | null = null)`; `now` is a stamp, as T3 says |
| N14 | `checkState`, `CheckResult`, `checkResult` | `check-state.ts:133`, `:7` |
| N15 | `applyDrafts` | `apply.ts:17` `(current, tree, drafts, newDecisionIds, date, importing)` |
| N16 | `parseDraft`, `Draft` | `drafts.ts:28` `(source, text)`, `:21` |
| N17 | `feedback`, `areaFeedback`, `Feedback` | `feedback.ts:32`, `:158`, `:28` (`{ recordId, message }`) |
| N18 | `mintId` | `ids.ts:8` `(prefix: "d"|"s"|"q", entropy: Uint8Array)`; matches `IdSource.entropy(): Uint8Array` |
| N19 | `attachmentPath`, `ATTACHMENTS` | `snapshot.ts:30`, `:28` |
| N20 | `confirmationDraft` | `confirmation.ts:38` `(confirms, scope, words, when, area)` |
| N21 | `behindArea`, `confirmableIds`, `MINUTE_FORMAT`, `VIEWER` | `confirmation.ts:24` `(s, d, area)`, `:14`, `:12`, `:11` |
| N22 | `level1`, `level2`, `level2Views`, `level3`, `failingIds`, `unrecordedProblems`, `Level1`, `Level3` | `views.ts:45`, `:65`, `:69`, `:79`, `:35`, `:41`, `:13`, `:27` |
| N23 | `resolve`, `AmbiguousRef`, `searchCounted`, `Filters` | `search.ts:31`, `:28`, `:46` `(s, d, query, f, limit)`, `:18` |
| N24 | `renderSpec`, `specView`, `SpecArea` | `render.ts:32`, `:22`, `:15` (`area: string | null = null`) |
| N25 | `restsOnTree`, `Branch` | `order.ts:80`, `:74` |
| N26 | `Action`, `Scope`, `Raises`, `Thread`, `Message`, `ThreadState`, `Decision`, `SpecEntry`, `Area`, `Record`, `Problem` | `model.ts:5`, `:3`, `:127`, `:143`, `:131`, `:129`, `:24`, `:77`, `:98`, `:152`, `:113` |
| N27 | builders: `filesOf`, `at`, `decision`, `entry`, `area`, `thread`, `message`, `treeOf`, `snapshotOf` | `tests/core/builders.ts:80`, `:32`, `:35`, `:52`, `:61`, `:67`, `:64`, `:116`, `:91` (`snapshotOf` builds a `Snapshot` literal, as T10 says) |
| N28 | `decisionText`, `specText`, `areaText` | `tests/core/applying.ts:32`, `:45`, `:49` |
| N29 | `CORE_NPM`, `PACKAGES` | `tests/structure/table.ts:11`, `:1` |
| N30 | `.dependency-cruiser.cjs` rules `no-circular`, `sqlite-confinement`, `file-confinement`, `app-imports` | lines `40`, `73`, `79`, plus `app-imports` (app may import no `core`-type or npm module) |
| N31 | `calls.ts` rules T2/T3 rely on | `app` may write `new Date(x)` with one argument and UTC getters only (`calls.ts`: `Date` rule, `local` set); a call named `write` is file writing, which is why `writeMessage` (plan 307) |
| N32 | `scripts/differential.sh`, `scripts/differential.ts` | exist; `differential.ts:41` is a `Tree` literal (T10 mismatch) |
| N33 | `ts/knip.json` closing `entry` | `["tests/**/*.test.ts", "scripts/*.ts"]` on `server-core` (two patterns), as T14 expects |

Not found at the cited line: none of the N-rows; `restsOnTree`, `newestLast` ordering and `compareOrderKeys` (not exported from `#core`) were not needed by name.

## Counts

33 pair rows (P1-P33), 16 task rows, 33 name rows: 82 rows.

## Mismatches

1. **T10, plan 504-505 / 537**: Files and Step 3 omit `ts/scripts/differential.ts:41`, a `Tree` literal `{ rev: null, files, attachments: new Set() }`; making `Tree.people` required breaks `tsc` (which includes `scripts`) at Step 4. Fix: list the file and pass `people`, or build it with `tree({…})`.
2. **T11, plan 544 (P20)**: Files omit `ts/src/app/state.ts`, where `Wiring` lives (`src/lodge/app/state.py:24`; plan 279), though the actor must reach `threads.ts` and `confirm.ts`. **RECHECK-R3**.
3. **T3, plan 285 vs 279 (P4)**: "`lodge.ts` holds `Wiring`" contradicts `Wiring` in `state.ts`; the first reading creates a cycle that `no-circular` refuses.
4. **Knip table, plan 43 (P6)**: `fakes.ts` names are all read in Task 3 but leave `entry` in Task 4; d-tha8st says the task that gives the reader. Minor.
5. **T8, plan 456 (P18)**: `tests/app/test_writes_retry.py:43-48` should be `:67`. Minor.
6. **T3/T4, plan 309 (P2)**: the `START.replace(microsecond=999_999)` rule belongs to T3's `add_fills_id_and_date_from_ports`, not T4. Minor.
7. **T4, plan 306**: `threads.py` has no `fromisoformat` ordering; only `reads.py:128` (descending on both date and ID, which "as `newestLast`", ascending, does not say); and `writes-dates`' `NEWEST` needs `offsetMinutes` 60. Minor.
8. **T12a, plan 578-580 (P25)**: `held()` returns `at`, but `held` has no `at` column; say it joins `events`. Minor. **RECHECK-R3**.
9. **T7b / T12b tests (Minor risk)**: `sqlite-store.test.ts` (13 tests) and `app/held.test.ts` (12) may exceed the 300-line limit; `derive.ts` (238) may after T13. No split planned.
10. **P29 (Minor)**: lanes A and B both edit the one-line `entry` array of `ts/knip.json` and `ts/package.json` `imports`; expect a merge conflict.
11. **T8/T9/T14 (P31, Minor)**: `parity.json` listed under Modify with nothing to change; `grep -c '"planned"'` cannot show which plans the rows belong to.
12. **T12b (P26, Minor)**: T2's `default_filling_functions_fill_python_defaults` covers `added()` as of T2; 12b changes `added()` but lists no edit to `ports.test.ts`. **RECHECK-R3**.
