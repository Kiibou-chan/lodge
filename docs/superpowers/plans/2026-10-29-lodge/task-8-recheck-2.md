# Task 8 recheck 2: fix round eb81709 and 76397bf

Rechecked: 76397bf against 2d22d19, for R1 to R3 of task-8-recheck-1.md.
Counts: 0 Blocking, 0 Important, 1 Minor (R4, new); R1 and R2 answered, R3 answered differently and adequately for the case it names.
Verdict: clean for Task 8 (0 Blocking, 0 Important); R4 can be parked as a Minor for the next round touching `tests/app/test_writes_retry.py`.

## What I ran

- Fresh `git archive` copies of 76397bf and 2d22d19 in `scratchpad/recheck2-t8/{fix,old}`.
- `sh scripts/check.sh` on 76397bf: exit 0, 688 passed (`scratchpad/recheck2-t8/check.txt`).
- 76397bf's `tests/app` files against 2d22d19's source: 4 failed, 50 passed (`test_not_found_does_not_call_a_missing_file_unreadable` and the three `test_unhashable_names_are_usage_errors` cases).
  The report says 7 failures; I see 4, and the renamed guard test passes on both; the count in the report looks wrong, which does not affect the code.
- My R1 probe (`test_probes_r1.py`): all four shapes, including `name: {a: 1}`, which the new test does not cover, are `LodgeError` exit 2 naming the file, as on 82de76c.
- My R2 probe (`test_probes_r2.py`): `show d-zzzzzz` with only a missing `_area.md` now says "no record named d-zzzzzz".
- My 19 first-review probes, diffed against recheck 1's run: the only difference is p13 (`draft area:storage` with no area file) losing the "could not read" clause, as R2 intends; every concurrency probe is unchanged.

## Findings

- R1: answered, `src/lodge/app/writes.py:112` and `:116` (`isinstance(..., str)` guards); `tests/app/test_writes_retry.py` `test_unhashable_names_are_usage_errors`.
- R2: answered, `src/lodge/app/state.py:71` (`p.check == 1`); `tests/app/test_reads.py` `test_not_found_does_not_call_a_missing_file_unreadable`.
- R3: answered differently but adequately: the test is renamed to what it checks and asserts `attempts == 0`.

On whether the untested retry-only usage error matters: it does not.
`apply_drafts` is a function of the snapshot, the tree, and the drafts, so a refusal that appears only on a retry comes from what changed between the two reads.
lodge never deletes a file (plan, "Calls made", Paths), so the changes another add can make are new records and areas, which `_raced` turns into `Conflict`, and edits, which `StaleBase` turns into `Conflict`.
What stays exit 2 on a retry needs a hand edit such as a deleted area file, which is rare, and exit 2 is defensible for it, so the negative direction carries no risk worth a test.

### R4 (Minor, new): the entry branch of `_raced` is untested

Only the area branch has a test (`test_area_created_by_another_add_is_a_conflict`).
Mutation: replacing `elif draft.kind == "spec":` with `elif False:` in `src/lodge/app/writes.py:114` leaves every builder test passing (57 passed); only my construction below fails.
Scenario: a later edit drops or breaks the entry branch, and a race on the same new entry ID exits 2 with "an edit draft needs a base key" again, unnoticed.
Construction (`scratchpad/recheck2-t8/fix/tests/app/test_probes_r3.py`, passes on 76397bf): `MemoryStore(AREA)`; `reject_next(files_of(entry(id="s-bbbbbb", area="storage", title="Theirs"), decision(id="d-cccccc", changes=(Change("s-bbbbbb", Action.CREATE),), date=at(20))))`; `add(NEW)` raises `Conflict` exit 1 with `attempts == 1` and no publish.
Fix: add that test beside the area one, as `test_entry_created_by_another_add_is_a_conflict`.

## Files read

Read: the fix diff for `src/lodge/app/{state,writes}.py` and `tests/app/{test_reads,test_writes_retry}.py`, and the report's "Fix round 2".
Not read: anything else; 76397bf changes only a docstring's line length, which `check.sh` covers.
