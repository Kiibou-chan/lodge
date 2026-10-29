# LODGE round recheck 4: part 5

Rechecked: `build-0.1` commit 954a9a6 against fb54e37, core only (`src/lodge/core/derive.py`, `src/lodge/core/feedback.py`, `tests/core/test_feedback_revival.py`), answering `lodge-round-recheck-3.md` N4 and N5 and U1's missing test.
Counts: N4 and N5 fixed, U1 pinned; new findings 0 Blocking, 0 Important, 1 Minor.
Verdict: clean.

## What I ran

Scratch copies from `git archive` of 954a9a6 and fb54e37 under `scratchpad/rcL4/{new,old}`; the build worktree was not touched.

- `sh scripts/check.sh` on 954a9a6: all gates clean, `799 passed`, exit 0 (`scratchpad/rcL4/gate.log`).
- 954a9a6's `tests/core/test_feedback_revival.py` over fb54e37's source (`scratchpad/rcL4/mix`): 3 failed, 5 passed in that file; whole suite `3 failed, 796 passed`.
  The three failures are `test_revival_of_an_unparsable_entry_does_not_crash` (`KeyError: 's-aaaaaa'`), `test_revival_of_a_dangling_entry_does_not_crash` (`KeyError: 's-zzzzzz'`), and `test_revival_line_names_only_retirements_that_were_standing` (line named `d-bbbbbb and d-cccccc`).
  `test_unparsable_decision_in_replaces_does_not_crash` passes on both, as the report says: U1 was already fixed by part 4 and the test pins it.
- Probes on both commits (`scratchpad/rcL4/probes.out`, `probes1-{new,old}.out`): `probes-rc1/{probe_lodge,probe_part4,probe_revive,probe_revive_dup,probe_editback,probe_regress}.py` and the first reviewer's `probes/*.py`.

## Probe results on 954a9a6

- U1: no crash, revival line `d-bbbbbb` (same on fb54e37).
- U2: no crash, no edit-back question (unchanged).
- U3 (unparsable revived entry): no crash, no revival line; fb54e37 raised `KeyError: 's-aaaaaa'`.
- U4 (dangling revived entry): no crash, no revival line; fb54e37 raised `KeyError: 's-zzzzzz'`.
- U5: line names only `d-cccccc`, "the last standing retirement"; fb54e37 named both.
- F1 and the rest of `probe_lodge`, `probe_revive`, `probe_revive_dup`, `probe_editback`: output identical to fb54e37.
- `probe_regress`: identical to fb54e37; its two DIFF lines (R5, R7) are the known open items (R7 owned by Task 5, R5 parked with M2).
- `probes/*.py` (crash, flag, retire, p1 to p3c): output identical to fb54e37.

## Findings

### N4: fixed

`derive.py:72` builds the public `Derived.revived` from known entries only (`_known`, `derive.py:99-100`); the internal `revived` still feeds `touches` (`derive.py:43`), so the flag over dangling targets is unchanged, and `changed_by` and `touched_by_flagged` filter by `known` in `_reverse` and at `derive.py:63`.
`feedback.py:109` reads `d.status.get(entry) != "current"`, which also skips an entry that ends retired, as before.
Tests: `test_revival_of_an_unparsable_entry_does_not_crash`, `test_revival_of_a_dangling_entry_does_not_crash`, red on fb54e37 as above.

### N5: fixed

`feedback.py:115` keeps a retirement only when `d.replaced_by.get(t, ())[-1:] == (decision.id,)`.
`replaced_by` is newest first, ties by larger ID (`derive.py:_reverse`), so `[-1:]` is the minimum of `(date, id)`, the same quantity as `first` in `_revived` (`derive.py:92-93`).
Test: `test_revival_line_names_only_retirements_that_were_standing`, red on fb54e37.

### U1: pinned

`test_unparsable_decision_in_replaces_does_not_crash` asserts the line names `d-bbbbbb` with the unparsable `d-zzzzzz` listed first; the unparsable file is made by the `titel:` rewrite, so lodge reports problem 1 as in the probe.

## Other consumers of `Derived.revived`

`grep -rn revived src/lodge`: the only reader outside `derive.py` is `feedback.py:108` (`_revival_message`).
Nothing in `views.py`, `app/`, `viewer/`, or `hook/` reads it, and no spec or other test does.
The filtered map therefore changes nothing beyond the revival line, and there every key is now a known entry, so the `.get` is defence rather than a needed guard.

## New findings

### Minor: the `Derived` docstring does not say `revived` holds known entries only

Handle: `src/lodge/core/derive.py:19-21`.
The ruling at ledger line 61 (dangling IDs dropped from derived maps) is why the filter exists; the docstring still reads as if every retired entry is listed.
Fix: add "known entries only" to that sentence.
Park for the next round touching `derive.py`.
