# LODGE round recheck 2: part 3

Rechecked: `build-0.1` commit be90780 against 381cc34 (code as at 5815098), answering `lodge-round-recheck.md` L1 to L4, with the rewritten ruling and "Part 3" in `task-4-report.md`.
Counts: L1 to L4 answered; new findings 0 Blocking, 2 Important, 1 Minor.
Verdict: not clean; the revival feedback crashes on a dangling `replaces` before check 2 can report it, and the edit-back question misses an agent edit she rejects together with a later agent retirement.

## What I ran

Fresh scratch copies of be90780 and 381cc34 under `scratchpad/rcL2/{new,old}`; the build worktree was not touched.

- `sh scripts/check.sh` on be90780: all gates clean, `773 passed`, exit 0 (log `scratchpad/rcL2/gate.log`).
- be90780's `tests/` over 381cc34's source: `5 failed, 768 passed`, the five tests the report names; the test diff removes no line.
- Every probe on both commits: `probes/probe_flag.py`, `probe_crash.py`, `probe_retire.py`, `probes-rc1/probe_regress.py`, `probe_lodge.py` (H1 to H7), and new `probe_revive.py` (V1 to V8, F1, F2), `probe_revive_dup.py`, `probe_editback.py` (E1).

## Probe results on be90780

- H1, H1b: flagged again (L1); unflagged on 381cc34.
- H2: the entry reads `awaiting the author on d-cccccc` (L2).
- H3: `retired by d-bbbbbb`, the standing retirement (L3).
- H4: the entry reads `current`, who `author`, no flags, since its newest change is now her reviving decision; the L4 line tells her at the add.
- H6, H7: the entry carries the awaiting flag of the agent retirement (H6) or the agent revival (H7).
- P1 to P6, P8 to P12, P14, P15, R1 to R4, R6, R8, crash probes A to C: unchanged and passing.
- Still open and owned: P7 and R7 (Task 5's import refusal), P13 and R5 (parked with M2).
- V1 to V5, `_revived` on chains: two retirements replaced one at a time credit only the second replacement (V1); a revival then a new retirement then its replacement credit both (V2); a decision replacing a retirement and retiring again revives nothing (V4); of two replacements of one retirement, the earlier revives (V5).
- V6, V8: an agent edit after an agent revival is unflagged (the last change is an agent's, as in P10); an agent edit after her revival is flagged.

## Findings answered

- L1: `derive.py:132-138` skips a replaced change only when its decision is neither an author decision nor one she confirmed.
- L2: `derive.py:42-44` and `_revived` (`:85-105`); a reviving decision counts as changing the entry, so it reaches `changed_by`, the flag, and `touched_by_flagged`.
- L3: `views.py:193-205` skips replaced retirements.
- L4: `feedback.py:95-111`, but see N2 and N3 below.

## Judgements asked for

The exemption of decisions she confirmed from the skip is sound.
It follows LODGE-6, under which a confirmed decision counts as hers (spec, Review flag), and it only errs towards flagging: P3, P4, and P12 stay flagged, and no probe lost a flag.

`Derived.revived` with the reviving decision as the entry's level-1 "who" is sound for revivals by an agent (V6, H2: the flag shows on the entry) and for her own revivals of text she or a confirmed decision wrote.
It reads as more settled than it is only where her revival brings back an agent's text, which N2 covers: V7 (agent text, revived by her) reads `author`, no flags, and E1 does the same with an agent edit she meant to reject.
With N2 fixed, she is asked at the add whether to edit the text back, which is LODGE-7's answer, so the "who" can stand.

## New findings

### N1 (Important): the revival feedback raises `KeyError` on a dangling or unparsable ID in `replaces`

Handle: `src/lodge/core/feedback.py:100-106` runs `after.decisions[t]` over every `t` in `decision.replaces` until a match; an ID that does not resolve (check 2, `check_state.py:83`) or whose file fails to parse raises before the match is reached.
`app/writes.py:73-75` computes feedback before it returns `CHECK_FAILED`, so the whole add, dry runs included, raises instead of reporting check 2.
Scenario, run (F1): her retirement `d-bbbbbb` of `s-aaaaaa`; a new decision with `replaces: [d-zzzzzz, d-bbbbbb]`; `feedback` raises `KeyError: 'd-zzzzzz'`.
Fix: `after.decisions.get(t)` and skip `None`, or take the retirement from `d.replaced_by` instead of re-scanning `replaces`.
Test: F1, expecting the revival line for `d-bbbbbb` and no exception.

### N2 (Important): rejecting an agent edit together with a later agent retirement brings back the agent's text with no edit-back question

Handle: `feedback.py:86` asks only when the replaced edit is the entry's newest change (`d.changed_by.get(entry, ())[:1] == (replaced.id,)`); a later retirement, and now the reviving decision itself (part 3 puts it into `changed_by`), sits before it.
Scenario, run (E1): author creates `s-aaaaaa`; agent `d-bbbbbb` edits it; agent `d-cccccc` retires it; author `d-dddddd` replaces both.
`changed_by` is `(d-dddddd, d-cccccc, d-bbbbbb, d-aaaaaa)`, the entry is current with the agent's rejected text, level 1 reads `author` with no flag (her replacement clears `d-bbbbbb`), and feedback gives only the revival line.
On 381cc34 the question was missed too (the newest change was the retirement), but the entry read `its decision replaced by d-cccccc`; part 3 removes that last trace.
Fix: ask when the replaced decision's edit is the entry's newest create or edit, ignoring retirements and revivals, which is what decides whose text the entry holds.
Test: E1, expecting both the revival line and the edit-back question.

### N3 (Minor): the revival line repeats, and names the wrong retirement, when one decision replaces two

Handle: `derive.py:103-104` appends the entry once per retirement the decision replaces, so `Derived.revived` holds `('s-aaaaaa', 's-aaaaaa')`; `feedback.py:97` then yields the line twice, each time naming the first retirement found in `replaces`.
Scenario, run (V3, `probe_revive_dup.py`): `d-dddddd` replaces both `d-bbbbbb` and `d-cccccc`; two identical lines, each calling `d-bbbbbb` "the last standing retirement".
F2, run: a revival plus another decision in the same add retiring the entry again still says "becomes current again" while the entry ends retired.
Fix: deduplicate in `_revived`; name every replaced retirement of the entry in one line; skip the line when the entry's status in `after` is `retired`.

## Consumers of `Derived`

- Check 4 and check 6, `apply_drafts`'s `_restored`, and `render_spec` read `status`, which part 3 does not change; no probe or test moved.
- `related` and level 2 read `changed_by`, which now holds reviving decisions; level 2 lists the reviver among the entry's decisions, which is accurate.
- The edit-back question reads `changed_by[:1]`, which part 3 changed; see N2.
- `Derived` is constructed only in `derive.py:64`; no test builds one by hand.
