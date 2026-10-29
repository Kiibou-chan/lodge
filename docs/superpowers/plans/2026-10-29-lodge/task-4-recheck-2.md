# Task 4 recheck 2: fix round 2

Rechecked: `build-0.1` fix commit faa7aeb against 4fb80cc, answering recheck 1's N1 and N3 under the rewritten `Ruling: I2,` (progress ledger, line 60).
Counts: 2 of 2 answered; new findings 0 Blocking, 0 Important, 1 Minor.
Verdict: fixed; no regression to B1, B2, or I1; every remaining hole has an owner.

## What I ran

Fresh scratch copies (`git archive faa7aeb` and `git archive 4fb80cc`) under `scratchpad/rc2/{new,old}`; the build worktree was not touched.

- `sh scripts/check.sh` on faa7aeb: ruff format, ruff, mypy, vulture clean, `441 passed`, exit 0 (log `scratchpad/rc2/gate.log`).
- faa7aeb's `tests/core/test_derive.py` over 4fb80cc's source: `2 failed, 24 passed`, the two failures being `test_imported_author_creation_not_flagged_by_her_later_live_edit` and `test_imported_agent_edit_before_her_later_live_edit_not_flagged`; on faa7aeb `26 passed`.
- The test diff removes `test_backdated_import_editing_live_author_entry_flagged` (the I2 fix the ruling withdrew) and adds the two tests above, which are recheck 1's R1 and R2; no other test changed.
- All probes on faa7aeb: `probes/probe_flag.py`, `probes/probe_crash.py`, `probes/probe_retire.py`, `probes-rc1/probe_regress.py`.

## Findings

### N1: answered

`src/lodge/core/derive.py:125-130` drops the import branch, so `_follows_author_change` uses the latest earlier change by date for every decision.
Run: R1 and R2 no longer flag; the two new tests pin them.

### N3: answered

`derive.py:85` now reads "The agent decisions and the imported decisions awaiting the author".

## Remaining holes and their owners

- P3, P4 (I3): with the author as LODGE-6 (ledger line 63).
- `probe_retire.py` (I4) and P12: with the author as LODGE-7 (ledger line 63).
- P13 (M2) and R5 (N2): parked for Task 7 or 8 (ledger line 67).
- P7 and R7 (a back-dated import changing an entry she edited live): Task 5's check, by `Ruling: I2,` (ledger line 60); `derive` no longer flags them, which is the ruling.

Every other probe passes: P1, P2, P5, P6, P8 to P11, P14, P15, R1 to R4, R6, R8, and crash probes A, B, and C.

## Regressions to B1, B2, and I1

None found.
B1: crash probes A and B run clean, and both B1 tests pass.
B2: P5 is flagged, and `test_imported_author_editing_live_author_entry_flagged` passes; that test's import is dated after the live decision, so the date rule still flags it.
The back-dated variant of B2's entry case (an imported author decision dated before her live edit of the entry) is now unflagged, like P7, and falls under the same Task 5 refusal, which the ruling words for any imported decision.
I1: P6 and P15 stay flagged; R3 and R4 clear.

## New finding

### M3 (Minor): the Task 5 refusal is recorded only in the ledger

Handle: the plan's Task 5 check 1 and check 4 (`docs/superpowers/plans/2026-10-29-lodge.md:250`, `:253`) do not mention refusing an imported decision that changes an entry a published non-imported decision already changed; it lives only in `Ruling: I2,` (ledger line 60).
Scenario: Task 5's brief is written from the plan's task text, misses the ruling, and P7 ends up with no owner, since Task 4's test pinning it was removed.
Fix: carry the ruling into Task 5's brief with a named test (for example `test_import_changing_live_edited_entry_refused`), or amend the plan's check 1 line.
