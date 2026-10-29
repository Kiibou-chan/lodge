# Task 5 recheck 1: the check, fix round 1

Rechecker: `rechecker` (Opus).
Under review: `build-0.1` fix commit cdb45ca against pre-fix 02e3292.
Scratch copies: `git archive cdb45ca` and `git archive 02e3292` in the scratchpad (`t5r1/new`, `t5r1/old`); no worktree was created, so none needs removing.
`sh scripts/check.sh` in `t5r1/new`: exit 0, ruff format, ruff, mypy, and vulture clean, 542 passed.

## Verdict

All eight findings answered (B1, I1, I2, M1 to M5).
New: 0 Blocking, 0 Important, 2 Minor.

## Probes

The first reviewer's probes, copied to `probes-t5r1/` with `common.run` passing `now = 2026-10-29T12:00:00+01:00` (`NOW` in `common.py`), run with `uv run python` from `t5r1/new`.
`p5_regressions.py` is new: legitimate changes after the fix, and the `now` bound.
The same scripts with the three-argument call are in `probes-t5r1-old/`, run from `t5r1/old`.

## Findings of the first review

### B1: answered

Handle: `src/lodge/core/check_entries.py:25` (`elif before != entry`, whole `SpecEntry`) and `:29` (`exempt = before is None and entry.imported_from is not None`).
p1: 1a (hand edit of an imported entry), 1b step 1 (`imported_from` added to her live entry), 1b step 2 (rewrite after laundering), 1c, and 1d (`imported_from` removed) each fail check 4 with `edited, but no new decision in this change lists it with action edit`; before the fix 1a, 1b, and 1d passed.
Tests `test_check_compare.py:93-145` (imported edit, laundering in one and two steps, removal, area move, create on an existing entry) fail on 02e3292's source; the two passing pairs (`new_imported_entry_needs_no_decision`, `imported_entry_edit_through_an_import_passes`) pass on both, as passing pairs should.
Regressions looked for, none found (p5, same result on 02e3292): an order swap alone (5a), one decision creating C and editing A (5b), create and a second decision's edit of the new entry in one change (5c), one decision listing create and edit for a new entry (5d), a retirement with its order edit (5e), an imported entry retired by an import with its order edit (5g), and a re-import changing text and `imported_from` through an imported `edit` decision (5h) each pass with at most the order note; a retirement that also rewrites the statement fails as an edit (5f), as it should.
A published problem on an entry (5i, entry missing from the order) stays a note under an unrelated change.

### I1: answered

Handle: `src/lodge/core/check_immutable.py:24-38`.
p2 2h (`one two three four five six` to `six five four three two one`) now fails, `reasoning of a published agent decision was changed`; 2i (contrary text, fewer words) stays a note, as the spec's "reasoning may be shortened" (spec:160) allows.
`test_check_5_agent_reasoning_reworded_at_the_same_length_fails` fails on 02e3292.
The equal-word-list rule also reaches author decisions; see N1.

### I2: answered as ruled

Handle: `src/lodge/core/check_change.py:29-31` (fourth parameter `now: datetime`) and `:60-62` (`datetime.fromisoformat(d.date) > now`, before the imported skip, so imports are bounded too).
p2 2m (agent decision dated 2027) now fails check 1, `dated 2027-10-28T11:00:00+01:00, which is after the time of this change`, so the record that blocked 2n and 2o can no longer be published.
Boundary (p5): a decision dated exactly `now` passes in the same offset (5l) and in another offset (5k), and when `now` carries microseconds after the second (5m); an imported bare-day date of today passes (5p) and of tomorrow fails (5o).
`test_check_1_new_decision_dated_after_the_time_of_the_change` fails on 02e3292; `test_check_1_a_decision_dated_exactly_now_passes` and `test_published_future_dated_decision_is_not_dated_again` pass on both, as boundary pairs.
Dates cannot be naive (`fields.py` `read_date` requires an offset, a bare day becomes `T00:00:00+00:00`), so the new comparison raises nothing on loaded records; a naive `now` raises `TypeError` (5q), which the plan's `Clock` excludes (plan:355, `timezone-aware`).

### M1: answered

Handle: `src/lodge/core/check_change.py:112-115`.
p3 3d gives `area empty: added`; 3a gives `area other: added`; `test_area_added_and_removed_are_notes` fails on 02e3292.

### M2: answered

Handle: B1's whole-entry comparison (`check_entries.py:25`); p3 3e now fails check 4 for the moved entry; `test_check_4_entry_moved_to_another_area_is_an_edit` fails on 02e3292.

### M3: answered

Handle: `src/lodge/core/check_state.py:104`, one form, `lodge/attachments/<decision id>/<name>`.
p4 4e (the spec's layout) passes; 4f (another decision naming `d-aaaaaa/run.log`) fails.
`test_check_2_listed_attachment_resolves_below_the_decision_folder` and the `lodge/attachments/run.log` case fail on 02e3292.

### M4: answered

Handles: `src/lodge/core/check_state.py:80-81` (`replaces itself`, and the same for `narrows` and `confirms`), `src/lodge/core/check_entries.py:36-40` (`lists create for <entry>, which already exists`).
p2 2p and 2q now fail; the four tests fail on 02e3292.

### M5: answered

Handles: `check_change.py:37,42` use `sort_key`; `check_state.py:47-54` (`decisions`, `new_decisions`) used by `_dates`, `_imports_over_live`, `_links_to_dead`, `check_entries`, and `_unlisted_sources`; no `map(s.decisions.__getitem__, ...)` remains.
Largest module 125 lines.

## New findings

### N1 (Minor): a published author decision's reasoning can now be re-paragraphed with no problem and no note

Handle: `src/lodge/core/check_immutable.py:24` (`if before.reasoning.split() == now.reasoning.split(): continue`) runs before the author branch at `:27`; test `tests/core/test_check_compare.py:234-235` asserts it for an author decision.
Scenario, run (p5 5r): her reasoning `First point.\n\nSecond point, separate paragraph.` becomes one paragraph: `ok`, no note; on 02e3292 it fails, `reasoning of a published author decision was changed`.
Every word stays, so nothing she said is lost, but her published record changes with no trace, and spec:160 lists only shortening as allowed; the first review offered word-list equality for the agent case (I1) only.
Fix: compare an author decision's reasoning exactly, as before; keep the word-list rule for agent decisions; drop the author half of `test_check_5_reasoning_reflowed_is_unchanged`, or turn it into a failing case.

### N2 (Minor, for Task 8's brief): `now` must be read no earlier than the dates it bounds

Handle: `src/lodge/core/check_change.py:60`; plan:381 (dates are `clock.now()` to the second).
Scenario, run (p5 5n): `now = 12:00:00.999999`, a decision dated `12:00:01` by a later clock reading: check 1 fails, `which is after the time of this change`.
If Task 8 reads `now` for the check before `apply_drafts` reads the clock for dates, an add that crosses a second boundary is refused for nothing.
Fix: in Task 8's brief, pass one reading taken after the dates are filled (or the same reading used for them, which truncation keeps no later than itself).
The same bound applies in checkout mode's gate, where dates were filled on the agent's machine and `now` is the gate's clock; a clock ahead of the gate's by more than the time between add and gate would be refused, which is the intended reading of I2 and needs no change.

## Observed, not introduced

Repairing a broken published entry file reads as a creation (p5 5j): check 4 asks for a decision listing `create`, which now passes M4's rule since the published state holds no parsed entry; the result is the same on 02e3292.
