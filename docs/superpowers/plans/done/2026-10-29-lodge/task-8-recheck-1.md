# Task 8 recheck 1: fix round e63e09f

Rechecked: e63e09f against 82de76c, for I1, M1 to M4, M6, and M7 of task-8-review.md and the ledger's M4 and M7 rulings (M5 parked).
Counts: 0 Blocking, 1 Important (new, R1), 2 Minor (new, R2 and R3); every finding answered.
Verdict: not clean; R1 must be fixed before the task is complete.

## What I ran

- Fresh `git archive` copies of e63e09f and 82de76c in `scratchpad/recheck-t8/{fix,old}`.
- `sh scripts/check.sh` on e63e09f: exit 0, 684 passed (`scratchpad/recheck-t8/check.txt`).
- e63e09f's three `tests/app` files against 82de76c's source: 9 failed, 41 passed; the failures are every new test except `test_refusal_on_a_retry_of_something_already_there_stays_a_usage_error` (see R3), which matches the report.
- My 19 first-review probes on e63e09f, diffed against the first run (`scratchpad/recheck-t8/probes-orig.txt` against `probes-fix.txt`): the only differences are p11, p12, and p13 now naming the unreadable file, `timeline(-1)` now a `LodgeError`, and p14 now `Conflict` exit 1. Every concurrency probe (p1 to p9, p16) is unchanged.
- New probes in `scratchpad/recheck-t8/fix/tests/app/test_probes_r1.py` and `test_probes_r2.py`.

## Findings answered

- I1: answered, `src/lodge/app/state.py:69-75` (`not_found`), used at `state.py:65`, `reads.py:62`, and `reads.py:85`; p11 and the four parametrised tests show the path in the message.
- M1: answered, `tests/app/test_reads.py:146`.
- M2: answered, `src/lodge/app/reads.py:86`.
- M3: answered, `src/lodge/app/reads.py:52-53`, with `test_timeline_refuses_a_negative_limit`.
- M4: answered as the ruling says, `src/lodge/app/writes.py:38-41` and `:67`, `_raced` at `:107-118`; p14 now exits 1.
- M6: answered, `src/lodge/app/ports.py:27-28`.
- M7: answered as the ruling says, `src/lodge/app/writes.py:69` and `:80-82`; both new tests fail on 82de76c.

The retry loop: `first` reaches only `_raced`, which decides whether a refusal is `Conflict` or `LodgeError`.
Minting, `apply_drafts`, `after`, `check_change`, and the publish base all still come from `state` of the same attempt (`writes.py:58-86`), so a stale first snapshot cannot decide what is published; p1 to p9 and p16 confirm it.
`first or state.snapshot` is safe because `Snapshot` defines neither `__bool__` nor `__len__`.

## New findings

### R1 (Important): a draft with a list or mapping as `name` or `id` now crashes with a traceback

`_raced` (`src/lodge/app/writes.py:107-118`) tests `name in now.areas` and `given in now.entries` on raw header values; when the header holds a list or mapping, the dictionary lookup raises `TypeError: unhashable type`.
It runs on every refusal, the first attempt included, so the refusal it should report never arrives.
Scenario (`test_probes_r1.py`, run on both copies): `lodge add` of an area draft with `name: [a, b]` or a spec draft with `id: [s-bbbbbb]` or `id: {x: 1}`.
On 82de76c each is a `LodgeError` exit 2 naming the file ("name must be a non-empty string", "id ['s-bbbbbb'] is not a specification entry ID"); on e63e09f each escapes as `TypeError`, against "no traceback reaches the user" (plan, Global Constraints) and the dispatch's "no exception other than `LodgeError` escapes".
Fix: in `_raced`, skip values that are not strings (`if isinstance(name, str) and ...`, likewise for `given`), and skip `_raced` on the first attempt (`first is not s`); add a test that these four drafts raise `LodgeError`, not `Conflict`.

### R2 (Minor): "could not read" names a file that does not exist

`not_found` lists every `Read.unrecorded` path, and `unrecorded_problems` (`src/lodge/core/views.py:55-58`) also holds problems at paths that are absent, not unreadable: an area with entries but no `_area.md` gives the check 7 problem at `lodge/spec/storage/_area.md`.
Scenario (`test_probes_r2.py`, `test_r2_unrecorded_kinds`): `lodge show d-zzzzzz` in that state says "lodge could not read lodge/spec/storage/_area.md, which may hold it", naming a file that does not exist as unreadable.
A readable area file with a check 7 problem does not show this (`test_r2b`, `unrecorded == ()`), so only the missing area file case is wrong.
Fix: list only check 1 problems in `not_found` (`p.check == 1`), or word it as "lodge has problems with <paths>"; one test with the missing area file.

### R3 (Minor): the guard test for M4 never reaches a retry

`test_refusal_on_a_retry_of_something_already_there_stays_a_usage_error` (`tests/app/test_writes_retry.py:79-84`) adds `spec_text("id: s-bbbbbb")` with no `area`, which `apply_drafts` refuses on the first attempt, so `reject_next(NOISE[0])` is never consumed and the retry path of `_raced` is untested (it passes on 82de76c too).
Scenario: a change that turned every retry refusal into `Conflict` would still pass it.
Fix: either rename it to what it tests (a first-attempt refusal stays exit 2), or assert `store.attempts == 1` and build a refusal that appears only on the retry over something present in both snapshots; renaming is enough, since a retry-only refusal over unchanged records is hard to construct and the ruling's cost is one exit code.

## Files read

Read: the fix diff for `src/lodge/app/{ports,reads,state,writes}.py` and `tests/app/{test_reads,test_writes,test_writes_retry}.py`, the report's "Fix round 1", the ledger's last lines, the rechecker role, and `core/views.py:55-58`.
Not read: anything outside the fix diff beyond that.
