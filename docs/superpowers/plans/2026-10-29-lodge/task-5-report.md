# Task 5 report: the check

Status: DONE_WITH_CONCERNS.
Files: `src/lodge/core/{check_state,check_areas,check_change,check_entries,check_immutable}.py`; tests `tests/core/{test_check_state,test_check_change,test_check_compare}.py`, helper `tests/core/checks.py`; `tests/core/builders.py` gained `snapshot_of` (a snapshot built from records directly, so defects that cannot be written to a file can be built).
Front door: `CheckResult`, `check_state`, `check_change`.
Gate: `sh scripts/check.sh` green, 525 tests (302 in `tests/core`; 84 new).

## Test-first

Each of the three new test files was run before its code and failed at collection with `ImportError: cannot import name 'check_state' from 'lodge.core'` (state tests) and `cannot import name 'check_change' from 'lodge.core'` (change and compare tests).
The first run of the full change tests also failed two tests of mine, both test errors and not code errors: the base state's author decision lawfully counts as a live change to `s-aaaaaa`, and a `confirms` test used a non-author decider; both tests were corrected.

## Where each rule lives

- Check 1: `load` covers parse problems, ID prefix by kind, and the wrong folder.
  The file name starting with the ID is not in `load`, so `check_state` reports it (`<id>.md` or `<id>-…`).
  The date rule and the carried import rule (`d-x: imported, changes s-y, which a live decision already changed`) need the published state, so they run in `check_change`.
- Check 2: unresolved links one problem per ID; codes compared with `casefold`, a problem for every record in the clash and the message naming no other record, so it stays stable when a third joins; attachments; published record missing from `after`.
  Duplicate IDs come from `load`.
- Check 3, check 7: `check_state` and `check_areas`.
- Checks 4, 5, 6: `check_entries`, `check_immutable`, `_links_to_dead` in `check_change`.
- Published problems (equal by path, check, message) become notes: `already published, check <n>: <path>: <message>`.
- Notes also: shrunk agent reasoning, changed area title, intro, or order.

## Readings I chose (not fixed by the brief)

- Check 5 compares the `statement` too (spec check 5 names it; the brief's "header" list omits it), and compares `date` as the string, so a rewritten offset counts as a rewrite; the date rule compares aware datetimes.
- Check 4 "changed in text" is title, statement, or code; an entry is exempt when imported in `after` and, if published, imported there too (so an edit cannot become exempt by adding `imported_from`).
- Check 7 requires the order to omit retired entries ("exactly the current entries"); retiring an entry therefore needs the area order edited in the same change, which is then a note.
- A listed attachment exists when its name, or `lodge/attachments/<name>`, is in `Snapshot.attachments`; the spec does not say whether the header holds the full path or the part below `lodge/attachments/`.
- A new area, or a removed one, gives no note; only a changed title, intro, or order of an area in both states does.
- Check 6 reads statuses from `derive(published)`.

## Concerns

1. The attachment path form above is a guess both ways; Task 9's trees should list full paths (they do in `load`), but the author may want one form fixed.
2. Check 7's "retired entries must leave the order" is stricter than the spec's "not placed in its area's order"; if the author wants retired entries to stay listed, one condition in `check_areas.py` changes.
3. Dangling targets in a published problem's message are stable, but a record moved from one path to another (not possible in 0.1) would turn a published problem into a new one.

## Fix round 1

New tests failed first (14 on the right assertion once `now` was a parameter; before that the signature change failed 72 on TypeError); 542 passed after.

- B1: check 4 exempts only a new imported entry; any other difference in a published entry (whole `SpecEntry`, so `imported_from` and `area` too) needs a new decision listing `edit`; `test_check_4_imported_entry_needs_no_decision` replaced by failing forms, the two-step laundering test, an import-edit-through-an-import pass, removal of `imported_from`.
- I1: reasoning with unequal `split()` lists fails check 5 unless an agent decision's has fewer words (note); equal word lists are unchanged; the equal-length test now asserts the problem `reasoning of a published agent decision was changed`.
- I2: `check_change(published, after, settings, now: datetime)`; check 1 fails a new decision, imported or not, dated after `now` (`dated <date>, which is after the time of this change`); a published future-dated decision is not re-checked; tests go through `checks.check`, which passes a fixed `NOW`.
- M1: notes `area <name>: added` and `area <name>: removed`.
- M2: covered by B1 (`test_check_4_entry_moved_to_another_area_is_an_edit`).
- M3: a listed attachment resolves only to `lodge/attachments/<decision id>/<name>`; Task 9 and the guide follow this form.
- M4: check 2 fails `replaces`, `narrows`, or `confirms` naming the decision's own ID (`d-x: replaces itself`); check 4 fails `create` for an entry the published state holds (`d-x: lists create for s-y, which already exists`).
- M5: `sort_key` used for the known-problem comparison; `decisions(s)` and `new_decisions(published, after)` live in `check_state.py` and every check uses them.
