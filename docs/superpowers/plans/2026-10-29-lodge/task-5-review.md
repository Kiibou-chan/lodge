# Task 5 review: the check

Reviewer: `reviewer` (Opus), three passes, correctness, then practice, then design.
Under review: `build-0.1` at ca82fc8 against BASE 22c91e1.
Scratch copy: `git archive ca82fc8` extracted into the reviewer's scratchpad (`t5src/`); probes in `probes-t5/`.
`sh scripts/check.sh` in the scratch copy: exit 0, 525 passed.

## Verdicts

Spec compliance: no.
Gaps: check 4 lets any entry carrying `imported_from` be edited without a decision (B1), and check 5 lets an agent decision's reasoning be rewritten at equal length with no problem and no note (I1).
Task quality: not approved; 1 Blocking, 2 Important, 5 Minor.

## What I ran

All probes read states through `load` from files written by `write_record`, as the gate will, not through `snapshot_of`.
Scripts in `probes-t5/` (scratchpad), run with `uv run python <script>` from the scratch copy.

- `p1_imported_entry.py`: edits of imported entries and laundering a live entry through `imported_from` (B1).
- `p2_decisions.py`: rewriting her statement, reasoning, quote, date, `decided_by`, `imported_from`; a shadow file with her ID; back-dating; a future date; self-replacement; `create` on an existing entry.
- `p3_published_problems.py`: a published state with nine problems (parse error, stray file, shared code, missing quote, unresolved link, missing attachment, two area-order problems) under an unrelated change, a change in the same broken area, and a repair; area notes; an entry moved between areas.
- `p4_state.py`: blank quote text, ID prefix against folder, file name, attachment forms.

What held, each run: her statement, reasoning (rewritten or shortened), quote, date (same instant, other offset), `decided_by`, and an added `imported_from` each fail check 5 (p2 2a to 2g); a shadow file with her ID fails checks 2 and 5 (2j); an agent edit back-dated before her decision fails check 1 (2k); all nine published problems become notes under an unrelated change, under a change in the same area, and under a repair of the broken file, and none blocks (p3 3a to 3c); blank quote text, a decision whose ID has the `s-` prefix, and a file named for another ID each fail check 1 (p4).

## Pass 1: correctness

### B1 (Blocking): check 4 lets an imported entry be edited, or a live entry be laundered, without a decision

Handle: `src/lodge/core/check_entries.py:29` and `:32-34`; test `tests/core/test_check_compare.py:89-93` asserts the hole.
`_text_of` compares title, statement, and code only, so adding or removing `imported_from` on a published entry is no edit; and `exempt` holds for any entry imported in both states.
Scenario, run (`p1_imported_entry.py`):
1a: an entry created by an imported author decision, statement rewritten by hand with no decision: `ok`.
1b: her live entry; change 1 adds only `imported_from: {file: old/spec.md, ...}`: `ok`; change 2 rewrites its statement with no decision: `ok`.
1d: `imported_from` removed from an imported entry: `ok`, no note.
Only 1c, both steps in one change, fails.
Consequence: after the rollout most of the first user's specification is imported, so any agent can rewrite any of it, including entries her decisions created, with no decision, no flag (the flag needs a decision), and the old decisions still listed as the entry's reasoning; that is must-not 2 and must-not 1, and it defeats the carried I2 rule (an import may not change a live-edited entry), since editing the entry directly needs no import at all.
Spec: check 4 exempts a change "unless it is imported", that is the creation or edit arriving by import; an imported *entry* being edited later is not an import.
Fix: exempt only a new entry (`before is None`) carrying `imported_from`; for a published entry compare the whole `SpecEntry` (title, statement, code, `imported_from`, area) and require a new decision listing it with `edit` when any differs.
A later import of a changed section then passes through an imported decision listing the entry with `edit`, which check 4 already counts and `_imports_over_live` already polices.
Flip the second half of `test_check_4_imported_entry_needs_no_decision` into a failing case, and add the two-step laundering pair.
Builder's raised point 6 (exempt only if imported in both states): rejected for this reason.

### I1 (Important): an agent decision's reasoning can be rewritten at equal length with no problem and no note

Handle: `src/lodge/core/check_immutable.py:30-36`; test `tests/core/test_check_compare.py:170-173` asserts it.
Scenario, run (`p2_decisions.py` 2h): reasoning `one two three four five six` becomes `six five four three two one`: `ok`, notes `()`.
Spec, check 5: "decisions are immutable ... reasoning may be shortened, and the check lists such edits"; an equal-length rewrite is not a shortening and is not listed, so a reader sees a published decision's reasoning changed with no trace (must-not 1).
Fix: when reasoning differs, fail unless it has fewer words; a shrink stays a note.
If whitespace reflow should pass, compare `reasoning.split()` lists first and treat equal lists as unchanged.
Replace the test with its failing form.

### I2 (Important): one future-dated decision blocks every later change to what it touches

Handle: `src/lodge/core/check_change.py:56-77` (the date rule) with no upper bound on a new decision's date anywhere in the check.
Scenario, run (`p2_decisions.py` 2m to 2o): an agent decision dated `2027-10-28T11:00:00+01:00` (a year typo) editing her entry passes its own change; afterwards her live edit of that entry dated today fails check 1 (`d-gggggg: dated 2026-10-29T10:00:00+01:00, no later than d-ffffff, which shares s-aaaaaa with it`), and so does a decision replacing the bad one (`... which it replaces`).
Since `lodge add` fills dates from the clock, nothing can change that entry or replace that decision until the date passes, and editing the published file is check 5.
How it arrives: a hand-written record in checkout mode, or an import (imports are exempt from the date rule, and an old file's date typo is plausible).
This breaks the plan's "one bad record never blocks everyone" (plan, Calls made, The gate) for that entry and every decision linking to it.
Fix: check 1 also fails a new decision, imported or not, dated after the time of the change; `core` takes that time as a parameter (spec, Structure: "the time and ID entropy come in as parameters"), so `check_change` gains `now: str` and Task 8 passes `clock.now()`.
This changes the plan's signature, so it needs a coordinator ruling; cost if wrong: one parameter through Task 8's check operation.
Not fixable inside the current signature: no state-only bound exists.

### M1 (Minor): a new or removed area gives no note

Handle: `src/lodge/core/check_change.py:107-112` iterates only areas in both states.
Scenario, run (`p3` 3d): a new empty area `empty` added: `ok`, no note.
The plan's call (Calls made, Area files): "every add that changes them lists the change as a note"; a new area is such a change and appears in the rendered specification.
Fix: notes `area <name>: added` and `area <name>: removed` for the symmetric difference.
Builder's raised point 5: rejected for this reason.

### M2 (Minor): an entry moved to another area passes silently

Handle: `src/lodge/core/check_entries.py:44-45` leaves out `area`; nothing else compares it.
Scenario, run (`p3` 3e): her entry moved from `core` to a new area `other`, both orders adjusted, no decision: `ok`, one note (`area core: order changed`).
The plan's call "entries do not move between areas in 0.1" has no test.
Fix: B1's whole-entry comparison covers it as an edit; or report a changed area as problem 4 naming both areas.

### M3 (Minor): the attachment forms accepted do not include the spec's own layout

Handle: `src/lodge/core/check_state.py:92`.
Scenario, run (`p4` 4e): `d-aaaaaa` lists `run.log`, the file is at `lodge/attachments/d-aaaaaa/run.log` as the spec's Storage layout places it (`lodge/attachments/<id>/`): check 2 fails, `lists attachment run.log, which does not exist`; listing `d-aaaaaa/run.log` passes, and so does another decision listing that path into d-aaaaaa's folder (4f).
Builder's raised point 4: the two forms accepted (the bare string as a full path, or `lodge/attachments/<name>`) are both guesses, and neither is the one the spec's layout implies.
Fix: resolve a listed name as `lodge/attachments/<decision id>/<name>`, one form, and say so in the guide (Task 13); record it as a ruling for Task 9.

### M4 (Minor): self-links and a `create` on an existing entry pass

Handle: `src/lodge/core/check_state.py:60-71`, `src/lodge/core/check_entries.py:15-20`.
Scenario, run (`p2` 2p): a new decision with `replaces: [<its own ID>]` passes and is at once `replaced` in `derive`, so reads show it superseded by itself (must-not 1); the same holds for `narrows` and an author `confirms` of itself.
Scenario, run (`p2` 2q): a new decision listing `create` for an existing, unchanged entry passes, and `changed_by` then shows the entry created twice.
Fix: check 2 fails a decision naming its own ID in `replaces`, `narrows`, or `confirms`; check 4 fails `create` for an entry the published state already holds.

## Pass 2: practice

### M5 (Minor): small duplications across the five modules

Handles: `check_change.py:41-42` `_key` is `check_state.py:38-39` `sort_key` again; `check_state.py:61,90,97,109` repeat `map(s.decisions.__getitem__, sorted(s.decisions))` beside the `records` helper at `:47-50`; `check_change.py:52-53` `_new_decisions` and `check_entries.py:15-20,51-54` each rebuild "decisions new in this change".
Failure: a later rule change (for example B1's notion of "new") edited in one copy and not the other.
Fix: use `sort_key` for the comparison, add a `decisions(s)` iterator beside `records`, and export one `new_decisions(published, after)` that `check_entries` uses.

Otherwise: names say what they hold, docstrings state facts, every module is under 300 lines (largest 113), tests follow `test_check_<n>_<defect>` and include every name the brief requires, including the carried `test_check_1_import_changes_entry_changed_live` and its passing pair; no test exists only for the builder.
The split into five source modules and three test files, beyond the brief's two and two, keeps each under the size rule; it is fine.

## Pass 3: design

- Boundaries hold: all five modules are in `core`, import only `core` modules, `datetime`, `dataclasses`, and `collections.abc`, and read no clock (`datetime.fromisoformat` only); the structure test passes.
- Published-problem policy: comparison by (path, check, message) with one problem per offending item holds under every published defect probed (p3); messages carry no counts or neighbour IDs, so they stay stable as other problems join.
- Plan rule no test enforces: "entries do not move between areas" (M2).
- Plan assumption against the code: "one bad record never blocks everyone" fails for a future-dated record (I2).
- `derive` runs five times per `check_change` (twice inside each `check_state` call through `check_areas`, twice in `check_entries`, once in `_links_to_dead`); harmless at hundreds of records, noted only.

## Builder's raised points

1. File-name rule in `check_state`, not `load`: accepted; it is still check 1 and runs on every read.
2. Check 5 compares `statement`: accepted; spec check 5 names the statement first.
3. Check 7 requires retired entries to leave the order: accepted; the plan's reading ("exactly the current entries") is stricter than the spec's wording but consistent with it, and Task 7's add edits the order.
4. Attachment under its bare name or `lodge/attachments/<name>`: not accepted as it stands (M3).
5. A new or removed area gives no note: rejected (M1).
6. Check 4 exempts an edited imported entry only if imported in both states: rejected (B1).

## Rulings for Task 5 (ledger lines 72 and 73)

- Check 7, retirements edit the order: stands, for point 3's reason.
- Check 5 compares `date` as the stored string, and `statement`: stands; probe 2e shows a same-instant reformat fails, which is the intended cost.

## Files read

`.claude/agents/reviewer.md`; `CLAUDE.md` (via the dispatch's context); spec, whole; plan lines 1 to 72 and 105 to 264 (Global Constraints, Process, Calls made, Review Focus, Tasks 3 to 5); ledger lines with `Ruling` or Tasks 4 and 5; `task-5-brief.md`; `task-5-report.md`; `src/lodge/core/{check_state,check_change,check_entries,check_immutable,check_areas,snapshot,derive}.py`; the diff of `src/lodge/core/__init__.py` and `tests/core/builders.py`; `tests/core/checks.py`; the test names of all three test files and the bodies of `test_check_state.py:1-60`, `test_check_change.py:1-60`, `test_check_compare.py:85-108,160-180`.

## Files not read

`src/lodge/core/{model,fileformat,drafts,yamlio,settings,ids}.py` (Task 3, behaviour taken from the probes); the remaining test bodies; the review package diff file as a whole (the same content read per file); Task 4's review and rechecks.
The role asks for a scratch worktree under `.claude/worktrees/`; the dispatch's hook rule put the scratch copy in the scratchpad instead, from `git archive ca82fc8`.
