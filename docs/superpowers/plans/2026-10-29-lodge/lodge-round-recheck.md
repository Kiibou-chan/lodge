# LODGE round recheck: LODGE-6, LODGE-7, and replaced changes

Rechecked: `build-0.1` commits cd7a6bf and 5815098 against f8d5add (code in `src/lodge/core`, tests in `tests/core`), with the spec's LODGE-6 and LODGE-7 lines and the last two Task 4 `Ruling:` lines in the progress ledger.
Counts: I3, I4, and P12 answered; new findings 1 Blocking, 1 Important, 2 Minor.
Verdict: not clean; part 2 (5815098) unflags agent edits after she corrects her own decision, which is a must-not 2 hole on an ordinary live path; a one-line fix is trialled below with the suite green.

## What I ran

Fresh scratch copies under `scratchpad/rcL/{old,mid,new}` of f8d5add, cd7a6bf, and 5815098; the build worktree was not touched (`git status --short` empty, HEAD 241e5e9).

- `sh scripts/check.sh` on 5815098: ruff format, ruff, mypy, vulture clean, `767 passed`, exit 0 (log `scratchpad/rcL/gate.log`).
- 5815098's whole `tests/` over f8d5add's source: `10 failed, 757 passed`; the ten are the eight LODGE tests the report names as red plus part 2's two.
  Over cd7a6bf's source: `2 failed, 765 passed`, exactly part 2's `test_agent_edit_after_she_replaced_an_agent_retirement_flagged` and `test_agent_edit_after_she_replaced_an_agent_edit_flagged`.
- The test diff moves `snapshot_of` and a project-named constant from `test_derive.py` to `tests/core/derivation.py`; no assertion changed and no test was dropped.
- Every probe on all three commits: `probes/probe_flag.py`, `probe_crash.py`, `probe_retire.py`, `probes-rc1/probe_regress.py`, and a new `probes-rc1/probe_lodge.py` (H1 to H7, histories of confirmed, replaced, and revived records, printing the entry's level-1 status and flags through `level1`).

## Holes closed and behaviour changed

- P3, P4 (I3, LODGE-6): closed at cd7a6bf; the later agent decision is flagged and touches the confirmed text or decision.
- `probe_retire.py` (I4, LODGE-7): the entry is `current` from cd7a6bf, was `retired`.
- P12: closed at 5815098 only (`derive.py:98-103`, `:156-157`).
- H2, H4, H6, H7: the entry is now `current`, where f8d5add showed it `retired by` the replaced retirement; each now shows `its decision replaced by …` at level 1.
- Unchanged and still owned: P7 and R7 (Task 5's import refusal, `Ruling: I2,`), P13 and R5 (parked with M2 for Task 7 or 8).
- Unchanged and passing: P1, P2, P5, P6, P8 to P11, P14, P15, R1 to R4, R6, R8, crash probes A to C, H3, H5.

## Findings answered

- I3: `derive.py` `_confirmed_by_her` and `_counts_for(d, hers)`; P3, P4 run flagged; an imported confirmation does not count (`test_imported_confirmation_does_not_make_a_decision_hers`).
- I4: `derive.py:39-45` counts a retirement only while its decision is not replaced; `check_change.py:109` and `apply.py:238-244` follow it, so the replacing decision may edit the entry and the entry returns to its area's order (check 7 stays clean, `test_replacing_retirement_restores_order`).
- P12: answered by the ruling's skip of replaced changes, but see L1.

## New findings

### L1 (Blocking): after she corrects her own decision by replacing it, an agent edit of her entry is no longer flagged

Handle: `src/lodge/core/derive.py:98-103` puts into `undone` every decision a non-imported author decision replaces, her own included, and `_follows_author_change` (`:150-157`) then skips that decision's change when looking for the entry's last change.
Scenario, run (H1): author `d-aaaaaa` creates `s-aaaaaa`; author `d-bbbbbb` replaces `d-aaaaaa` (a correction of its statement, no entry change, the spec's "a correction is a new decision", check 5); agent `d-cccccc` edits `s-aaaaaa`; `awaiting_author` is empty and the entry reads `current` with no flag.
H1b, run: agent creates, author edits, author replaces her own edit decision, agent edits: unflagged.
Both are flagged on f8d5add and on cd7a6bf; 5815098 introduced the hole.
The ruling's text ("skips changes by a decision that a non-imported author decision replaces") covers her own decisions, but its why is LODGE-7's undoing of an agent's change, and its cost line names only the over-flag side.
Fix: skip only replaced changes that are not hers: add `if t in s.decisions and not is_author(s.decisions[t]) and t not in hers` to the `undone` comprehension (move `hers` above it).
Trialled in a throwaway copy (`scratchpad/rcL/fix`): `767 passed`, H1 and H1b flagged, P3, P4, and P12 still flagged, H2 to H7 unchanged.
Tests: H1 and H1b as `test_agent_edit_after_she_corrected_her_own_decision_flagged` and the agent-created variant.

### L2 (Important): an entry revived by an agent replacing her retirement shows no review flag

Handle: `derive.py:52-56` gives `touched_by_flagged` a flagged decision's `replaces`, `narrows`, and `changes` targets; an entry that a flagged decision brings back by replacing its retirement is in none of them.
Scenario, run (H2): author creates `s-aaaaaa`, author `d-bbbbbb` retires it, agent `d-cccccc` replaces `d-bbbbbb`; `d-cccccc` is flagged, but `s-aaaaaa` reads `current · its decision replaced by d-cccccc` with no `awaiting the author`, and `apply_drafts` puts it back into the area order, so `render_spec` shows her retired entry as a current part of the specification with no flag.
On f8d5add the entry stayed retired, so this is new with LODGE-7.
The spec says the flag shows "on the decision or entry it touched" (Review flag); the revived entry is touched.
Fix: in the `touched` loop, add the entries that a decision in `d.replaces` retired and that are now `current`.
Test: H2, asserting `touched_by_flagged["s-aaaaaa"] == ("d-cccccc",)`.

### L3 (Minor): `retired by` can name a replaced retirement

Handle: `src/lodge/core/views.py:193-205`, `_retiring` returns the newest decision in `changed_by` that retires the entry, replaced or not.
Scenario, run (H3): author retires with `d-bbbbbb`, agent retires again with `d-cccccc`, author replaces `d-cccccc`; the entry reads `retired · retired by d-cccccc · its decision replaced by d-dddddd`, naming the retirement she undid rather than `d-bbbbbb`, which keeps it retired.
Fix: skip IDs in `d.replaced_by` in `_retiring`.

### L4 (Minor): replacing a retiring decision revives the entry with only an order note

Handle: `apply.py:238-244` restores the entry silently; the add's only trace is check's `area storage: order changed` (`check_change.py:117-126`).
Scenario, run (H4): she corrects her own retiring decision by replacement without listing `retire` again; the entry is current and back in the order.
This is the spec's LODGE-7 wording ("retired while a decision that lists it … as retired is not replaced"), so it is correct, but a correction meant only for the statement brings the entry back unasked.
Fix: a feedback line beside the edit-back question, for example "replacing d-x makes s-y current again; to keep it retired, list it in changes with action retire".

## Consumers in Tasks 5 to 8

- Check 4 (`check_entries.py:27`): asks for a `retire` listing only when an entry becomes retired; a revival needs none, which matches LODGE-7.
- Check 6 (`check_change.py:96-115`): an entry counts as retired only when retired before and after, so the decision that replaces the last standing retirement, or a later one, may edit it; a same-add agent replacement of her retirement plus an edit passes check 6 and is flagged by `touches_author_decision`.
- Check 7 and `apply_drafts`: the restored entry is appended to its area's order (`apply.py:221`), so check 7 stays clean; `_restored` re-reads the whole tree only when some entry is retired.
- Feedback (`feedback.py:75-91`): the edit-back question fires only for an author decision replacing an agent decision whose edit is the entry's newest change; H5 shows the entry reading `its decision replaced by …`, so the rejected text is not shown as settled.
- Views and `render_spec`: see L2 and L3; nothing else changed.
