# Task 4 recheck 1: fix round 1

Rechecked: `build-0.1` fix commit 4fb80cc against 2f158dc, findings B1, B2, I1, I2, and M1 of `task-4-review.md`, and the Task 4 rulings (progress ledger, lines 58 to 61 and 65).
Counts: 5 of 5 answered; new findings 0 Blocking, 1 Important (conflicts with the I2 ruling, so for the integrator), 2 Minor.
Verdict: the five findings are fixed as ruled; the I2 rule as built raises flags on imported records that her own later live edit overwrote, including her own imported author decisions.

## What I ran

All runs in scratch copies (`git archive 4fb80cc` and `git archive 2f158dc`) under `scratchpad/rc1/{new,old}`; the build worktree was not touched (`git status --short` empty, HEAD 5680b41).

- `sh scripts/check.sh` on 4fb80cc: ruff format, ruff, mypy, vulture clean, `440 passed`, exit 0.
- `probe_flag.py`, `probe_crash.py`, `probe_retire.py` (first reviewer's) on both commits.
- The seven new tests with 4fb80cc's `tests/core/test_derive.py` copied over 2f158dc: `7 failed, 18 passed` (two `ValueError: tuple.index(x)` at old `derive.py:121`, five `assert frozenset() == {'d-bbbbbb'}`); on 4fb80cc `25 passed`.
- The test diff only adds tests; no existing test changed.
- `probes-rc1/probe_regress.py` (mine, R1 to R8) on both commits.

## Probe results on 4fb80cc

- P1, P2, P8 to P11, P14: ok on both commits, unchanged.
- P5, P6, P7: hole at 2f158dc, closed at 4fb80cc.
- P15: now flags `d-bbbbbb` (a confirm dated before the agent decision no longer clears it), which is the I1 ruling; the probe expected nothing either way.
- P3, P4 (I3) and `probe_retire.py` (I4): holes remain, as expected.
- P13 (M2, left): hole remains, as expected.
- P12 (author replaces agent A1 without restoring the entry, agent A2 edits again): hole remains on both commits; the review lists it among the holes but assigns it to no finding.
  It belongs with I3 and I4 (whether her rejection makes the entry's state hers), so it should go to the author with them rather than be dropped.
- `probe_crash.py` A (dangling entry) and B (unparsable entry): crash at 2f158dc, `ok` at 4fb80cc; C (naive date) unchanged, problem 1.

## Findings

### B1: answered

`src/lodge/core/derive.py:86-89` indexes changes over every entry ID, known or not, and `derive.py:131` looks `d` up in that list, which always holds it; `Derived.changed_by` still filters to known entries (`derive.py:37`, `_reverse` at `:79`).
Run: `probe_crash.py` A and B no longer raise; `test_agent_change_to_missing_entry_does_not_crash` and `test_agent_after_author_edit_of_unparsable_entry_flagged` fail on the old code and pass on the new.

### B2: answered

`derive.py:93` skips only `is_author(d) and d.imported_from is None`; `_counts_for` (`:118-122`) keeps imports flagged only by non-imported author decisions.
Run: P5 flagged; R6 (imported author replacing imported author) not flagged, as the ruling wants.

### I1: answered

`derive.py:107-115` clears only on a non-imported author decision whose `(date, id)` order is after the target's, the same `_order` key the sort uses (`:33`, `:62-63`), so "later" and the list order agree.
Run: P6 and P15 stay flagged; R3 (live confirm later) and R4 (live replace later) clear.
`Derived.confirmed_by` is unchanged, per the ruling at ledger line 65.

### I2: answered as ruled

`derive.py:129-130`: an imported decision is flagged when any change to the entry by a counting decision exists, whatever its position.
Run: P7 flagged; R7 (live author, back-dated import, live agent) now flags both, where 2f158dc flagged only the live agent.
See N1: the ruling's premise does not hold in every rollout order.

### M1: answered

`derive.py:96` `touches_author_decision`, `:99` `follows_author_change`.

## New findings

### N1 (Important, conflicts with the I2 ruling): an import is flagged by her own later live edit of the same entry, her own imported author decisions included

Handle: `derive.py:129-130` flags an imported `d` when any non-imported author decision changed the entry, before or after it; with B2 (`derive.py:93`) this now applies to imported author decisions too.
The ruling (ledger line 60) rests on "imports are always added after live records (spec, Rollout 3 and 4)".
Rollout 3 converts a sample of the first user's past and then replays rulings with lodge in the same scratch copy (spec, `docs/superpowers/specs/2026-10-29-lodge-design.md:222`), so there the imports come first and the live decisions after.
Rollout 2 (dogfood, `:221`) starts with "this brainstorm's" decisions, which predate lodge; if they go in with `--import` (my reading, not stated), imports again precede live work, the order `CLAUDE.md` line 5 ("the spec's 'Her decisions' until lodge holds its own records") implies.
Scenario, run (R1): imported `d-aaaaaa`, `decided_by: author`, dated 2026-01-01, creates `s-aaaaaa`; live author `d-bbbbbb` edits `s-aaaaaa` later; `awaiting_author == {d-aaaaaa}`, so her own imported decision waits for her because she edited her own entry.
Scenario, run (R2): add an imported agent edit `d-cccccc` dated 2026-02-01 between them; both imports are flagged, although her live edit overwrote the agent's text.
On 2f158dc neither was flagged.
Cost: every imported record that changed an entry she later edits joins the "what waits for her" list, and each clears only with a live author confirm carrying a quote (check 3); in the Rollout 3 replay this also inflates the flag counts that are measured.
A single snapshot cannot tell an import added after her live edit (I2) from one added before it (R1, R2): both have the earlier date.
Fix: keep date order for imports in `derive` (the latest-earlier-change rule, as for live decisions) and enforce I2 at add time, where Task 5's check has the published snapshot: an imported decision that changes an entry a published non-imported decision already changed is refused, or listed as the feedback "will raise a review flag" and flagged by a recorded rule; this is the review's second option for I2.
If the integrator keeps the ruling, record the imports-first rollout cost in it and add a test pinning R1's behaviour, so the choice is visible.

### N2 (Minor): a same-second live confirm with the lower ID no longer clears

Handle: `derive.py:113` requires `_order(target) < _order(later)`, and `_order` breaks a same-second tie by ID (`:62-63`).
Scenario, run (R5): agent `d-cccccc` and her confirm `d-bbbbbb` both at the same second (one add, where the clock gives every decision the same second, plan "Calls made", Dates); the flag stays; 2f158dc cleared it.
Check 1 does not catch it, since the agent decision is not yet published.
This is M2's same-second ordering reaching the clearing rule; park it with M2 for Task 7 or 8.

### N3 (Minor): `_flagged`'s docstring says agent decisions

Handle: `derive.py:85`, "The agent decisions awaiting the author"; after B2, imported author decisions are flagged too.
Fix: "The decisions awaiting the author".
Parked for the next round touching `derive.py`.

## Files

Read: `.claude/agents/rechecker.md`, `task-4-review.md`, the ledger's Task 4 rulings, the report's "Fix round 1", the fix diff, `src/lodge/core/derive.py` at 4fb80cc, the spec's Must nots answers, Review flag, and Rollout (`:61-65`, `:169-174`, `:218-229`), the plan's "Calls made" (`docs/superpowers/plans/2026-10-29-lodge.md:45-56`).
Probes: first reviewer's under `scratchpad/probes/`; mine at `scratchpad/probes-rc1/probe_regress.py`.
