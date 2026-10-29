# LODGE round recheck 3: part 4

Rechecked: `build-0.1` commit ba2f6a5 against 473ccb4, the core changes only (`src/lodge/core/derive.py`, `src/lodge/core/feedback.py`, and their tests), answering `lodge-round-recheck-2.md` N1 to N3.
Counts: N1 to N3 answered; new findings 0 Blocking, 1 Important, 1 Minor.
Verdict: not clean; part 4 moves N1's crash from a bad decision in `replaces` to a revival of an entry that is not in the snapshot.

## What I ran

Fresh scratch copies of ba2f6a5 and 473ccb4 under `scratchpad/rcL3/{new,old}`; the build worktree was not touched.

- `sh scripts/check.sh` on ba2f6a5: all gates clean, `795 passed`, exit 0 (log `scratchpad/rcL3/gate.log`).
- ba2f6a5's `tests/` over 473ccb4's source: `5 failed, 790 passed`, the four new tests plus the reworded edit-back test.
- The only changed test line is that edit-back test's expected text ("latest change to" becomes "latest edit of"); no assertion was weakened.
- Every probe on both commits: the first reviewer's (`probes/`), mine (`probes-rc1/probe_regress.py`, `probe_lodge.py`, `probe_revive.py`, `probe_revive_dup.py`, `probe_editback.py`), and a new `probes-rc1/probe_part4.py` (U1 to U5: unparsable records in `replaces`, revivals of unparsable or dangling entries, and a replacement of an already replaced retirement).

## Probe results on ba2f6a5

- F1 (dangling ID first in `replaces`): no crash; the revival line names `d-bbbbbb` (N1).
- U1 (an unparsable decision file first in `replaces`): no crash, problem 1 reported, revival line given; on 473ccb4 it raised `KeyError: 'd-zzzzzz'`.
  This covers the untested case the coordinator named, since an unparsable record is absent from `after.decisions` just as a dangling one is (`feedback.py:111`).
- U2 (an unparsable agent edit in `replaces`): no crash and no edit-back question, which is right, since lodge cannot read the edit; the record fails check 1.
- E1: the edit-back question for `d-bbbbbb` and the revival line for `d-cccccc` both appear (N2).
- V3: one line naming `d-bbbbbb and d-cccccc`, and `Derived.revived` holds the entry once (N3).
- F2: no revival line when another decision of the add retires the entry again (N3).
- Unchanged: P1 to P6, P8 to P12, P14, P15, R1 to R4, R6, R8, H1 to H7, V1, V2, V4 to V8, crash probes A to C.
- Still open and owned: P7 and R7 (Task 5), P13 and R5 (parked with M2).

## Judgements asked for

The new wording, "still the latest edit of that entry", is accurate.
The question fires only when the replaced decision lists the entry with `edit` (`feedback.py:86`) and that decision is the entry's newest create or edit (`_newest_text_change`, `feedback.py:96-102`), so "edit" names exactly what it tested; the old wording, "latest change", became false once retirements and revivals are passed over.

The missing test for an unparsable record in `replaces` is covered by U1 as a probe, and the code path is the same as the dangling ID that `test_dangling_replaces_leaves_the_revival_line_and_does_not_raise` pins.
Adding U1 as a test is cheap (`probe_part4.py`, U1) and worth taking with the fix below.

## New findings

### N4 (Important): the revival line raises `KeyError` when the revived entry is not in the snapshot

Handle: `src/lodge/core/feedback.py:107`, `d.status[entry] == "retired"`; `Derived.revived` (`derive.py:72`) keeps every entry a retirement names, known or not, because `_revived` (`derive.py:85-105`) reads `c.entry` from `changes` without checking `s.entries`.
Scenario, run (U3): her retirement `d-bbbbbb` of `s-aaaaaa`, whose entry file fails to parse (problem 1); a new decision replacing `d-bbbbbb`; `feedback` raises `KeyError: 's-aaaaaa'`.
U4, run: the retirement names a dangling `s-zzzzzz`; `KeyError: 's-zzzzzz'`.
On 473ccb4 both gave a revival line without raising, so part 4 introduced this.
`app/writes.py:73-75` computes feedback before it returns `CHECK_FAILED`, so the add raises instead of reporting check 1 or check 2, as in N1.
The ruling at ledger line 61 drops dangling IDs from derived maps, and `revived` is the one public map that keeps them.
Fix: build the public `Derived.revived` from known entries only (`derive.py:72`), keeping the full map internal for the flag as B1 does; and use `d.status.get(entry) != "current"` in `feedback.py:107`.
Tests: U3 and U4, expecting no exception.

### N5 (Minor): the revival line can call an already replaced retirement "last standing"

Handle: `feedback.py:108-115` lists every retirement in `decision.replaces` that retires the entry, including one that an earlier decision already replaced.
Scenario, run (U5): `d-bbbbbb` and `d-cccccc` retire `s-aaaaaa`; `d-dddddd` replaces `d-bbbbbb`; `d-eeeeee` replaces both; the line says "it replaces d-bbbbbb and d-cccccc, the last standing retirements", but only `d-cccccc` was standing.
Fix: keep only the retirements whose earliest replacement is this decision (as `_revived`'s `first` computes), or drop "standing" from the wording.
Park for the next round touching `feedback.py`.
