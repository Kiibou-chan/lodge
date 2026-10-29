# Task 4 review: snapshot and derived facts

Reviewed: `build-0.1` at 25c7180, range e47afb1..25c7180.
Counts: 2 Blocking, 4 Important (two of them for the author), 2 Minor.

## Verdicts

Spec compliance: **no**.
Gaps: an imported decision with `decided_by: author` that replaces a live author decision is never flagged, against the plan's "Calls made" (B2); the flag clears on any author decision, where the spec says "a later author decision" (I1).
Task quality: **not approved** (B1 crashes every read on one bad record; B2).

## What I ran

All runs in a scratch copy (`git archive 25c7180`) with its own environment; the build worktree was not touched (`git status --short` empty afterwards).

- `sh scripts/check.sh` in the copy: ruff format, ruff, mypy, vulture clean, `433 passed`.
- `probe_flag.py`: fifteen scripted histories of author, agent, and imported decisions on one shared entry and on replace, narrow, and confirm chains; each asserts the decisions that must be awaiting the author.
  Holes found in P3, P4, P5, P6, P7, P12, and P13; P1, P2, P8 to P11, P14, and P15 behave as the spec says.
- `probe_crash.py`: `derive` on an agent decision whose changed entry is missing from the snapshot (dangling ID, and an entry file failing to parse); a naive date in a decision file.
- `probe_retire.py`: author creates an entry, an agent retires it, the author replaces the agent decision.

The probe scripts are kept in the reviewer's scratch directory.

## Pass 1: correctness

### B1 (Blocking): `derive` raises `ValueError` when an agent decision changes an entry the snapshot does not hold

Handle: `src/lodge/core/derive.py:102-106` calls `_latest_before(d, changed_by.get(entry, ()))`, and `derive.py:121` runs `newest_first.index(d.id)`; `changed_by` holds known entries only (`derive.py:37`, `_reverse` at `derive.py:79`), so for an unknown entry the tuple is empty.
Scenario, run: an agent decision with `changes: [{entry: s-zzzzzz, action: edit}]` and no such entry gives `ValueError: tuple.index(x): x not in tuple`.
Worse, run: one entry file with a misspelt header key (`titel:`) is problem 1, the entry drops out of the snapshot, and every agent decision that ever changed it crashes `derive` for the whole store.
The spec's answer to must-not 1 is that "a record failing the check is shown as failing"; here one failing record stops every read, the viewer, the add feedback ("an agent decision that will raise a review flag"), and the gate's notes policy ("one bad record never blocks everyone").
Fix: compute the latest earlier change from an index of every target, known or not, and filter to known IDs only when building `Derived.changed_by`; then an agent edit after an author edit of an unparsable entry is still flagged, and a dangling target has no earlier change.
Tests: `test_agent_change_to_missing_entry_does_not_crash`, `test_agent_after_author_edit_of_unparsable_entry_flagged`.

### B2 (Blocking): an imported decision with `decided_by: author` that replaces or narrows a live author decision is never flagged

Handle: `src/lodge/core/derive.py:94`, `if is_author(d) or ...: continue`, skips every author decision before the import rule at `derive.py:112-116` is reached.
Binding text: the plan's "Calls made", "an imported decision that replaces or narrows a non-imported author decision is flagged like any agent decision" (`docs/superpowers/plans/done/2026-10-29-lodge.md:51`).
The brief narrowed this to "an agent decision D … when D is imported" (`task-4-brief.md`, Flag), and the builder followed the brief; the plan governs the brief.
Scenario, run (P5): live author decision `d-aaaaaa`; `lodge add --import` of `d-bbbbbb` with `decided_by: author`, `imported_from` set, `replaces: [d-aaaaaa]`; `awaiting_author` is empty and nothing shows on `d-aaaaaa`.
Check 3 exempts imported author decisions from the quote (spec, "The check", item 3), so an agent running the importer can replace her live decision with no quote and no flag; this is must-not 2 exactly.
The same holds for an imported author decision that edits an entry whose latest change was a live author decision.
Fix: treat an imported decision as an agent decision for raising the flag whatever its `decided_by`, that is skip only `is_author(d) and d.imported_from is None`, keeping `_counts_for` so only non-imported author decisions raise it.
Test: `test_imported_author_replacing_live_author_decision_flagged`, plus the entry variant.

### I1 (Important): the flag clears on any author decision, including imported and earlier-dated ones

Handle: `src/lodge/core/derive.py:38` (`confirmed_by` counts every author decision) and `derive.py:94-97` (clears on any author confirm or replace, with no date test).
Binding text: "It clears when a **later** author decision names it in `confirms` or `replaces`" (spec, "Review flag").
Scenario, run (P6): live author `d-aaaaaa`, live agent `d-bbbbbb` replaces it (flagged), then an imported `d-cccccc` with `decided_by: author`, dated 2026-01-01, `confirms: [d-bbbbbb]`; the flag clears although the confirmation is dated before the decision it confirms and carries no quote.
Live decisions cannot hit this, since Task 5's check 1 dates a new non-imported decision after what it links to (plan, Task 5, check 1); imports are exempt, and nothing bounds an import's date from above.
Fix: clear only on an author decision ordered after D (the spec's "later") that is not imported, the second half by symmetry with the plan's import call; record the second half as a ruling.
Test: `test_imported_author_confirm_does_not_clear`, `test_confirm_dated_before_does_not_clear`.

### I2 (Important): a back-dated imported agent edit of her live entry is unflagged and reads as older than her edit

Handle: `src/lodge/core/derive.py:102-106` orders by date, as the brief says; the plan's Task 5 check 1 exempts imports from the date rule.
Scenario, run (P7): live author `d-aaaaaa` creates `s-aaaaaa` at 2026-10-28; an import `d-bbbbbb`, agent, dated 2026-01-01, edits `s-aaaaaa`.
The entry file now holds the import's text, yet the import sorts first, has no earlier change, and is not flagged; `changed_by["s-aaaaaa"]` lists her decision as the newest, so the entry's reasoning reads as hers (must-not 1 and 2).
During the pilot, converting further old decisions after live ones on the same entry is the expected case (spec, Rollout 3 and 4).
Fix: an imported D that changes an entry is flagged when any non-imported author decision changed that entry, whatever its date, since an import is always added after live records; or a ruling extending Task 5's check 1 to refuse an imported decision that changes an entry a non-imported decision already changed.
The first keeps the fix inside Task 4 and needs no ruling beyond the brief's import clause.
Test: `test_backdated_import_editing_live_author_entry_flagged`.

### I3 (Important, for the author): an agent change to something she confirmed is not flagged

Handle: `src/lodge/core/derive.py:100` and `:103` test `is_author` on the target or the latest change, never whether she confirmed it.
Scenario, run (P3): author creates `s-aaaaaa`, agent `d-bbbbbb` edits it (flagged), author `d-cccccc` confirms `d-bbbbbb`, agent `d-dddddd` edits `s-aaaaaa` again: nothing is flagged, so the text she just approved is rewritten silently.
P4 is the same with decisions: she confirms an agent's narrowing, a second agent replaces it, no flag.
This follows the spec's letter ("replaces or narrows an author decision", "whose last change was an author decision"), so the code is compliant; whether a confirmed decision counts as "a decision she made" (must-not 2) is a reading of the spec, so it goes to the author.
Recommendation: a decision confirmed by a later non-imported author decision counts as an author decision for raising the flag.
Cost if wrong: every confirmation makes the confirmed text agent-editable without notice, which is the opposite of what confirming signals.

### I4 (Important, for the author): rejecting an agent's retirement leaves her entry retired for good

Handle: `src/lodge/core/derive.py:39` retires an entry when any decision retires it, replaced or not.
Scenario, run (`probe_retire.py`): author creates `s-aaaaaa`, agent `d-bbbbbb` retires it (flagged), author `d-cccccc` replaces `d-bbbbbb`; result `s-aaaaaa: retired`, `d-bbbbbb: replaced`, nothing awaiting.
Task 5's check 6 refuses any later `create` or `edit` of a retired entry (plan, Task 5, check 6), and Task 7 removes it from the area order, so her rejection cannot bring the entry back; the record reads retired although the only retirement was overturned (must-not 1).
The spec's wording ("an entry is retired when a decision lists it in `changes` as retired") gives this result, so it is the author's call.
Recommendation: an entry is retired when a decision that is not replaced retires it.

## Pass 2: practice

### M1 (Minor): `earlier_target` names an ordering the code does not test

Handle: `src/lodge/core/derive.py:99`.
Scenario: a reader assumes a date comparison for `replaces` and `narrows`, as for entries, and misjudges P8 (a back-dated import narrowing a live decision, correctly flagged).
Fix: rename to `touches_author_decision`, and `earlier_change` to `follows_author_change`.

Tests otherwise read cleanly: one rule per test, the builders give fixed dates and IDs, and no test needs only the builder.
`vulture_allow.py:9-11` states the fact; the module docstrings state facts.
The added problem 1 for a record in the wrong folder (`snapshot.py:80-83`) is a sound reading: without it, as the report says (not run), a decision under `lodge/spec/` would load as an entry of an area named after the folder.

## Pass 3: design

### M2 (Minor): two decisions dated the same second order by ID, so the flag on a shared entry depends on random IDs

Handle: `src/lodge/core/derive.py:62-63`.
Scenario, run (P13): author `d-bbbbbb` and agent `d-aaaaaa` both at 10:00:00 change `s-aaaaaa`; the agent sorts first and is not flagged.
Task 5's check 1 catches this only against a published decision; two new decisions in one add get the same second from the clock (plan, "Calls made", dates "to the second").
Fix: park for Task 7 or 8, where `apply_drafts` fills dates, so that decisions of one add sharing an entry get distinct ordered dates, or check 1 reports a same-second pair sharing an entry.

Boundaries hold: `snapshot.py` and `derive.py` are pure, import only `core` modules and allowed standard modules, and stay under 300 lines (92 and 122).
The plan's assumption that all dates are aware after Task 3 holds, run: a decision file with a naive date is problem 1 and never reaches `derive`.
Plan rules no test enforces: the import clause of the plan's "Calls made" (B2) and the spec's "later" in clearing (I1).

## Files

Read: `.claude/agents/reviewer.md`, `CLAUDE.md`, `task-4-brief.md`, `task-4-report.md`, the plan's Global Constraints, Process, Calls made, Review Focus, Tasks 4 and 5 (`docs/superpowers/plans/done/2026-10-29-lodge.md:15-72,197-263`), the spec's Must nots to Review flag and Rollout (`docs/superpowers/specs/2026-10-29-lodge-design.md:53-175,218-230`), `src/lodge/core/derive.py`, `src/lodge/core/snapshot.py`, `src/lodge/core/model.py`, the `src/lodge/core/__init__.py` and `vulture_allow.py` diffs, `tests/core/builders.py`, `tests/core/test_derive.py`, `tests/core/test_snapshot.py`.
Not read: the review package diff as a file (read the same range through the files), `src/lodge/core/fileformat.py` beyond its definitions, `headers.py`, `fields.py`, `drafts.py`, `settings.py`, `yamlio.py`, and the plan's Tasks 6 to 14 beyond the lines cited.
