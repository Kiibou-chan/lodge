# Task 7a review: doubts and derived statuses

Reviewer: `reviewer` (Opus), from the dispatch of the coordinator.
Commit under review: 1660e45 against its parent d811f22 (`git diff d811f22 1660e45 -- ts/`).
Probes ran in a detached scratch worktree at 1660e45 (`.claude/worktrees/review-task7a` of the main checkout, `ts/node_modules` linked to this worktree's), since removed.
Already ruled and not raised: d-p48gr1, d-fbhdvf, d-g1hrmn, d-4m6m35, d-0q54zn, d-f18pz7.

## Verdict

0 Blocking, 2 Important, 5 Minor.
The port is right: `derive` and `doubtMarks` agree with lodge 0.2 on this repository's records and on 6000 random made-up stores, list order included, under three time zones.
The two Important findings are both about tests that do not hold what the brief and the plan ask: nothing pins ordering by instant and then by ID (C-1), and the link test's deliberate out-of-order snapshot is sorted away by the loader before `derive` sees it (C-2).
Both fixes are test-only and were run in the scratch worktree.

## Pass 1: correctness

### What was run

- `cd ts && bun test tests/core` at 1660e45: 350 pass, 4 todo, 0 fail, 354 tests across 23 files.
- Parity of `derive` on this repository's records: a Python dump (`lodge.gitstore.checkout.disk_tree`, `load`, `derive`, every field of `Derived`, list order kept) against a TypeScript dump (the same files read into `tree`, `load`, `derive`) of the 222 decisions and 126 entries at 1660e45.
  Result: equal in every field.
  This repository's records exercise little of the review flag: `awaiting_author`, `confirmed_by`, `touched_by_flagged`, `revived`, and `doubts` are all empty, so this comparison alone says nothing about the flag.
- A differential fuzz to cover what the repository does not: 6000 random made-up stores (two seeds, 7 and 11), each of one to five entries, one to nine decisions, and up to three threads, written by lodge 0.2's `files_of` and read by each language's own `load`.
  Decisions draw `decided_by` from author, coordinator, and builder, a quarter of them imported, with random `changes` of every action (dangling entries included), `replaces`, `narrows`, and `confirms` (dangling IDs included), and dates from nine stamps with offsets from -23:59 to +01:00, several of which name the same instant (`2026-10-28T10:00:00+01:00` and `2026-10-28T09:00:00+00:00`), so equal instants are tie-broken by ID; entries carry random `rests_on` (cycles and dangling targets included) and `imported_from`; threads are doubts or questions, open or closed, about a random record.
  Of the 6000, 3846 had a review flag, 2271 a revival, and 3191 a doubt mark.
  Result: every field of `Derived` equal in all 6000, list order included.
  A bare day cannot reach `derive` through files, since `readDate` turns it into `T00:00:00+00:00` and lodge 0.2's `write_record` refuses to write one (`fileformat.py:53`, "date reads back as '2026-10-27T00:00:00+00:00'"), so the bare-day branch of `orderInstant` is reached only by a snapshot built in memory.
- The same fuzz stores under `TZ=Pacific/Kiritimati` and `TZ=America/St_Johns`: 0 differences; `derive.ts`, `derive-review.ts`, and `doubts.ts` name no `Date`, `process`, `console`, or `Math.random` (Review Focus 4 and 5).
- Twenty targeted mutations of `derive.ts`, `derive-review.ts`, and `doubts.ts`, each applied alone, run against all of `tests/core`, and reverted; the ten that survive the tests were then run against the fuzz stores.

| Mutation | `tests/core` failing | Fuzz stores differing (of 3000) |
|---|---|---|
| `derive.ts:31` tie-break dropped, `return at - bt` | 0 | 0 |
| `derive.ts:31` tie-break reversed, `byCodePoint(bi, ai)` | 1, `changed_by_newest_first` | not run |
| `derive.ts:31` the date compared as text, not through `orderInstant` | 0 | 1640 |
| `derive-review.ts:47` clearing ignores the order | 1, `confirm_dated_before_does_not_clear` | not run |
| `derive-review.ts:9` an imported confirmation counts as hers | 1, `imported_confirmation_does_not_make_a_decision_hers` | not run |
| `doubts.ts:30` the last-change clause dropped | 1, `doubt_on_decision_marks_entries_it_created_and_last_changed` | not run |
| `derive.ts:69` the reviver-is-a-retirement skip dropped | 0 | 123 |
| `derive.ts:76` the revival dedupe dropped | 0 | 32 |
| `derive.ts:120` targets of a flagged decision not sorted | 0 | 0 (key order only) |
| `derive.ts:129` `supports` built in map order | 0, see C-2 | 0 (one area per store) |
| `derive.ts:144` a decision whose revived entries are all unknown kept, with an empty list | 0 | 443 |
| `derive-review.ts:64` the `undone` filter dropped | 1, `agent_edit_after_she_replaced_an_agent_edit_flagged` | not run |
| `derive.ts:130` `rests_on` not deduplicated | 0 | 0 (no duplicates generated) |
| `derive-review.ts:27` replaced edits not skipped behind a flag | 0 | 692 |
| `derive.ts:70` other retirements not limited to earlier ones | 0 | 248 |
| `doubts.ts:35` questions propagate | 1, `question_open_mark_and_no_propagation` | not run |
| `derive.ts:101` agents' confirmations listed | 1, `confirm_by_an_agent_does_not_clear` | not run |
| `derive-review.ts:15` the imported clause of `countsFor` dropped | 3, the imported tests | not run |
| `derive.ts:94` a link counts as a change | 2, the link tests | not run |
| `doubts.ts:48` propagation stops after one step | 2, the propagation tests | not run |

  The analogous mutations of `src/lodge/core/derive.py` (text comparison of the date, the reviver skip dropped, unknown revived entries kept, replaced edits not skipped, other retirements not limited) leave all of lodge 0.2's `tests/core` passing (594), so those survivors are gaps lodge 0.2's tests already have, carried faithfully, not losses in the port; the dedupe survivor is killed in Python by `test_feedback_revival.py::test_one_revival_line_names_every_replaced_retirement`, which a later task carries.
- `test.todo`: this task adds two, `confirmed_decision_shows_confirmation_and_keeps_decided_by` and `flag_order` (`ts/tests/core/doubts.test.ts:77-78`), as the brief requires.
  `tests/core/test_doubts.py` stays `planned` with tasks 7a and 9a (`ts/tests/parity.json:184-189`), so `ported_files_hold_no_todo` does not apply to it and is not broken; the four rows this task flips to `ported` hold no `test.todo`.
  Since a planned row's names are not checked, `rowMissing(…, "tests/core/test_doubts.py", …)` was run by hand: `[]`, every one of the nine Python names is present.
- Review Focus 1, by reading every carried test beside its Python original: each assertion compares what the Python compares, whole maps and sets with `toEqual` (Bun's `toEqual` on a `Map` ignores key order and refuses an extra key, checked), membership with `has` or `includes` where the Python uses `in`; the one test weaker than its original is C-2, through its helper rather than its assertion.

### C-1 · Important · no test holds `derive` to ordering by instant, then by ID

Handle: `ts/src/core/derive.ts:25-32`; the brief's Interfaces ("`derive`'s ordering key is `(instant(date), id)`"); plan `## Review Focus` item 4 ("two decisions in the same second ordered by ID"); ruling d-g1hrmn.
The code is right: the fuzz above agrees with Python on 6000 stores with mixed offsets and equal instants.
But comparing the date as text instead of through `orderInstant` leaves all 354 tests of `tests/core` passing while changing 1640 of 3000 fuzz stores, and dropping the ID tie-break leaves both the tests and the fuzz unchanged.
The tie-break is invisible today because `load` walks paths in sorted order (`ts/src/core/snapshot.ts:52`) and a decision's path starts with its ID, so loaded decisions arrive in ID order and the stable sort keeps it.
Failure scenario: plan 2's store rebuilds the snapshot from events in event order, or a refactor in Task 7b (whose `confirmation.ts` sorts by `orderKey`, `src/lodge/core/confirmation.py:31`) compares `date` strings; two decisions dated `2026-10-28T10:00:00+01:00` and `2026-10-28T09:30:00+00:00` then order the wrong way round, a review flag lands on the wrong decision, and no test fails.
Fix: add one test to `ts/tests/core/derive.test.ts` that builds the snapshot in memory with `snapshotOf` of `builders.ts`, in reverse ID order, so neither the loader nor the stable sort supplies the order:

```ts
test("orders_by_instant_across_offsets_then_by_id", () => {
  const changes = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const at = (id: string, date: string) => decision({ id, date, changes });
  const got = derive(snapshotOf([
    entry({ id: "s-aaaaaa" }),
    at("d-dddddd", "2026-10-28T08:45:00-01:00"),
    at("d-cccccc", "2026-10-28T09:30:00+00:00"),
    at("d-bbbbbb", "2026-10-28T10:00:00+01:00"),
    at("d-aaaaaa", "2026-10-28T09:00:00+00:00"),
  ]));
  expect(got.changedBy.get("s-aaaaaa")).toEqual(["d-dddddd", "d-cccccc", "d-bbbbbb", "d-aaaaaa"]);
});
```

Run in the scratch worktree: it passes at 1660e45, fails with the tie-break dropped, and fails with the date compared as text.
It carries no Python name; `rowMissing` checks only that Python names are present (`ts/tests/parity-names.ts`), so an added title does not break parity, but it is a test lodge 0.2 does not have, so the coordinator may prefer to rule it in.

### C-2 · Important · the doubt and link tests load from files where lodge 0.2 builds the snapshot in memory, and one of them loses what it tests

Handle: `ts/tests/core/derive-links.test.ts:4` and `ts/tests/core/doubts.test.ts:12` import `snapshotOf` from `./derivation.ts`; `tests/core/test_derive_links.py:1` and `tests/core/test_doubts.py:5` import `snapshot_of` from `builders`; `ts/tests/core/derivation.ts:7` widens Python's `*records: Record | Area` (`tests/core/derivation.py:10`) to `(Record | Area | Thread)[]` to make room.
`builders.snapshot_of` keeps the items in the order given, "without reading files" (`tests/core/builders.py:91`); `derivation.snapshot_of` writes them and loads them, and `load` walks the paths sorted (`ts/src/core/snapshot.ts:52`).
`supports_is_the_reverse_of_rests_on` passes the entries as `c, b, a` on purpose (`tests/core/test_derive_links.py:27`), so that `derive` must sort them itself (`derive.py:82`, `sorted(s.entries.items())`); through `load` they arrive as `a, b, c` already, and the test no longer checks the sort.
Run: dropping the sort in `src/lodge/core/derive.py:82` fails `test_supports_is_the_reverse_of_rests_on` in Python; dropping it in `ts/src/core/derive.ts:129` leaves `derive-links.test.ts` passing at 1660e45, and fails `supports_is_the_reverse_of_rests_on` once the file takes `snapshotOf` from `builders.ts`.
Failure scenario: a later change makes `supports` follow the snapshot's map order, which for entries is area folder first (`lodge/spec/<area>/<id>-…`), so `supports` lists an entry of area `model` before one of area `storage` with a smaller ID, and the carried test still passes; secondarily, a loader change that reports a problem for a thread file fails the doubt tests on the loader, not on `derive`.
Fix: in both files import `snapshotOf` from `./builders.ts` and call it with an array, `derive(snapshotOf(items))` and `snapshotOf([area(), c, b, a])`, since the TypeScript `snapshotOf` takes `readonly Item[]` (`ts/tests/core/builders.ts:91-93`); restore `derivation.ts`'s parameter to `(Record | Area)[]`.
Run in the scratch worktree with that change: `doubts.test.ts` 7 pass, 2 todo, 0 fail; `derive-links.test.ts` 3 pass, 0 fail, and 1 fail with the sort at `derive.ts:129` dropped.

### C-3 · Minor · the report's evidence table shows only that each test calls `derive`

Handle: `task-7a-report.md`, "Failure evidence" M1 and the table under it; Task 5b's review C-1; d-mfayy5.
M1 throws at the top of `derive` and makes `isAuthor` return `false`, which fails any test that calls `derive`, including one whose assertions were deleted, so the table is no evidence that a test detects what its name says.
For this task that is not a breach of test-first: `derive` is new code, the missing-export run R2 counts as failing (Global Constraints), and the report says plainly that `derive.test.ts` had no clean pre-implementation red because its first run was a syntax error (`Expected ";" but found "new"`).
The targeted mutations above stand in for the table: ten of twenty are caught by a named test, and the ten survivors are either neutral here (three: key order, map order, which C-2 makes visible, and duplicates the fuzz does not generate), gaps lodge 0.2's own tests share (four), killed by a later task's carried test (one, the revival dedupe), or C-1 (two).
Fix: none in the code; the next brief that names mutation evidence should ask for a mutation inside the function's logic, as Task 5b's review did.

## Pass 2: practice

### P-1 · Minor · the contract of `Derived` and the helpers' docstrings were dropped

Handle: `ts/src/core/derive.ts:12-24` against `src/lodge/core/derive.py:18-24`; `ts/src/core/derive-review.ts:33-71` against the docstrings of `_cleared`, `_counts_for`, and `_follows_author_change` (`derive.py:201`, `222-225`, `237-241`).
The Python docstring of `Derived` states facts every later reader of the type depends on: each list of decisions is newest first with ties by ID, the maps hold known records only, and a reviving decision counts as changing the entry.
`ts/src/core/derive.ts` and `ts/src/core/derive-review.ts` carry no comment at all, while earlier ported modules keep such facts (`ts/src/core/fields.ts`, "A bare day is accepted only for an imported record.").
Failure scenario: Task 9a's `levels.ts` or plan 2's store consumes `changedBy` expecting oldest first or expects a dangling target as a key, and nothing on the type says otherwise.
Fix: carry the `Derived` docstring as a comment on the interface, and one line each on `flagged` (the skip of a change undone by her replacement) and `countsFor` (an imported decision is flagged only by non-imported ones).

### P-2 · Minor · two small leftovers

Handle: `ts/src/core/doubts.ts:28-29` reads `s.decisions.get(id)` and then `d?.changes`, though `id` comes from a filter on `s.decisions.has(id)` one line up, so the optional chain can never short-circuit and hides that invariant; `ts/tests/core/derive.test.ts:172` writes `files: files`.
Fix: `const d = s.decisions.get(id) as Decision` or iterate the decisions themselves; write `files`.

## Pass 3: design

### D-1 · Minor · an unplanned module, and two Python helpers folded into one function

Handle: `ts/src/core/derive-review.ts` (71 lines) is not in the brief's Files, which create `doubts.ts` and `derive.ts` only; `derive.ts` is 150 lines, so the two together would be about 215, not "nearing 300" (Global Constraints, "A module nearing 300 lines is split by topic").
Inside it, `flagged` (`derive-review.ts:33-71`) folds Python's `_cleared` (`derive.py:200-208`) and `_follows_author_change` (`derive.py:234-243`) into one function, and `_cleared`'s comparison `order_key(target) < order_key(later)` becomes an index comparison over `oldest` (`derive-review.ts:47`), equivalent only because order keys are unique.
The report names the split, as the constraint asks, so the coordinator may accept it.
Cost if kept: `derive.py` no longer reads beside one TypeScript module, which Task 12's differential review and every later port of a `derive` change (plan 2's people in `decided_by`, design line 77) will pay; the fuzz shows no behaviour difference.
Fix: either fold `derive-review.ts` back into `derive.ts` with `cleared` and `followsAuthorChange` as their own functions, or keep the split and record it in the ledger line.

### D-2 · Minor · Task 7b will need the comparator that `derive.ts` keeps private

Handle: `ts/src/core/derive.ts:25-32`; `src/lodge/core/confirmation.py:31` sorts by `order_key`, and `src/lodge/core/views.py:223` compares `order_key(...)[0]`.
`orderKey` returns a tuple, which JavaScript cannot compare with `<` or hand to `sort`, so Task 7b's `confirmation.ts` must write a second comparator of `orderKey`'s two parts, the same three lines as `compare`.
Failure scenario: the second copy breaks the tie the other way, or compares `at < bt` without the ID, and C-1's missing test lets it through.
Fix: in Task 7b's brief, have `confirmation.ts` reuse one comparator, either by exporting `compare` from `derive.ts` under a name of its own (an export beyond `order_key`'s, so the coordinator rules it) or by stating that the second comparator is `orderInstant` difference, then `byCodePoint` of the IDs, and pinning it with C-1's test.

### Plan assumptions checked against the code

- `derive.ts` in knip's `entry` until Task 7b (`ts/knip.json:2`): as the table in the Global Constraints says.
- `#core` exports `Derived`, `derive`, and `isAuthor` (`ts/src/core/index.ts:1`), the names `src/lodge/core/__init__.py:13` exports from `derive`.
- `isAuthor` compares `decidedBy === "author"` as lodge 0.2 does (`derive-review.ts:4-6`), with people in `decided_by` left to plan 2 (d-88p8h9).
- `orderKey` is `[orderInstant(d.date), d.id]` (`derive.ts:25-27`), per d-g1hrmn; its bare-day branch is reached only by a snapshot built in memory (see Pass 1).

## Files read

Read: `CLAUDE.md`; `docs/superpowers/plans/2026-11-02-lodge-server-core/task-7a-brief.md`, `task-7a-report.md`, and `task-5b-review.md` (C-1); the plan's `## Review Focus` and its Task 7a and 7b lines (`docs/superpowers/plans/2026-11-02-lodge-server-core.md`, by `grep`); the rulings d-g1hrmn, d-p48gr1, d-fbhdvf, d-4m6m35, d-0q54zn, d-f18pz7, and d-mfayy5 through `lodge show`; the whole diff `d811f22..1660e45 -- ts/`: `ts/src/core/derive.ts`, `derive-review.ts`, `doubts.ts`, `index.ts`, `ts/knip.json`, `ts/tests/parity.json`, `ts/tests/core/derivation.ts`, `derive.test.ts`, `derive-imported.test.ts`, `derive-links.test.ts`, `derive-confirmed-retired.test.ts`, and `doubts.test.ts`; `ts/src/core/stamps.ts`; `ts/src/core/fields.ts` (`readDate`, `readStamp`); `ts/src/core/snapshot.ts` (`tree`, the sorted walk); `ts/tests/core/builders.ts` (`snapshotOf`, `filesOf`); `ts/tests/parity.test.ts` and `ts/tests/parity-names.ts`; `src/lodge/core/derive.py`, `doubts.py`, and `fields.py` (`read_date`); `src/lodge/gitstore/checkout.py` (`disk_tree`); `tests/core/derivation.py`, `test_derive.py`, `test_derive_links.py`, `test_derive_confirmed_retired.py`, `test_doubts.py`, and `builders.py`.

Not read: `task-7a-codex-final.txt`; `ts/tests/core/order-instant.test.ts` beyond its `orderInstant` lines; the structure rules and the dependency-cruiser and Biome configurations (the gate is green, per the dispatch); `src/lodge/core/confirmation.py` and `views.py` beyond their `order_key` lines; the plan text outside the sections named above.
The whole gate `sh scripts/check.sh` was not rerun; `bun test tests/core` was.
