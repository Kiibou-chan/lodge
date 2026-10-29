# Task 7 recheck 1: fix round 1 (f4bf61f)

Fix diff bd95ef0..f4bf61f, against task-7-review.md and the last Task 7 `Ruling:` line of the ledger (dry run in Task 8, check 5 unchanged, M10 in the ledger, M11 to Task 8).

## Verdict

0 Blocking, 0 Important, 1 new Minor; every finding taken in this round is answered.
Clean.

## What I ran

- `git archive f4bf61f` into `scratchpad/probes-t7/srcf4`, `sh scripts/check.sh`: exit 0, 634 passed.
- New tests on the old code: f4bf61f's three test files over bd95ef0's source (`git diff 27beffe bd95ef0 -- src tests` is empty, so the old source is `probes-t7/src27`) give 15 failed, 40 passed; every added or changed test is among the 15.
- Probes rerun on f4bf61f: `probe.f4.out`, `probe2.f4.out`, `probe3.f4.out`, `probe4.f4.out` beside the earlier outputs in `scratchpad/probes-t7/`, diffed against them.
  Every difference is one of the fixed findings; no probe that passed or was refused before changes otherwise.
- Line counts: `apply.py` 253, `feedback.py` 108, `test_apply_refusals.py` 238, `test_feedback.py` 226; no em-dash in the changed sources.

## Findings

- I1: answered, `src/lodge/core/apply.py:59-61` collects only string names; probe3 now gives problem 1 `name must be a non-empty string` on the draft for a list and a mapping, where it raised `TypeError`.
- I2: answered as ruled, `src/lodge/core/feedback.py:84-86` and `:97-100` name the remedy as a change to the draft before adding it, which the dry run of the ruling makes reachable in branch mode.
- M1: answered, `src/lodge/core/feedback.py:92, 107` hides only codes held by a record of `after`, case-insensitively; probe2 flags `top-10`, `Python-3`, and `COVID-19`, and `test_numbers_ignore_ids_codes_and_dates` keeps `item-1` hidden when `ITEM-1` exists.
  A code the project does not hold is now flagged (probe2, `ITEM-1` with no such record gives `40 %, 1`), which is the intended reading.
- M2: answered, `src/lodge/core/apply.py:224`; probe "create and retire in one add" now leaves the area unwritten and passes the check.
- M3: answered, `src/lodge/core/apply.py:86-90, 140, 172`, for decisions, entries, and areas.
- M4: answered, `src/lodge/core/feedback.py:79-86`.
- M5: answered, `src/lodge/core/feedback.py:97-100`.
- M6: answered, `src/lodge/core/apply.py:205-207`.
- M7: answered, `src/lodge/core/apply.py:111, 159, 252`, for entry and decision edits; the one changed assertion (`tests/core/test_apply.py:169`, `--import` to `changes imported_from of s-aaaaaa`) follows the new message and hides nothing.
- M8: answered, `src/lodge/core/apply.py:96, 124, 146`; probe3 gives `area must be one name, not ['storage']` and a named message for `id:` empty, `~`, and upper case.
- M9: answered, `tests/core/test_feedback.py:226`.

## The builder's three deviations

- Related-message ending ("If so, set replaces or narrows in the draft before adding it"): adequate; it names the remedy the ruling makes possible, and it reads as two sentences of one message, consistent with the others having no final full stop.
- Kind-specific ID message: adequate, with N1 below.
- `base` refused on a new area draft: adequate; it matches M3 for decisions and entries, and `lodge draft area:<name>` cannot print an area that does not exist, so no lodge-printed draft reaches it.

## New Minor

- N1. `src/lodge/core/apply.py:245-250`, `_not_an_id` always adds "IDs are lower case", which misleads when the ID is lower case but of the other kind or empty: `id 's-bbbbbb' is not a decision ID; IDs are lower case, like d-3m8qk2` (probe, "decision draft with s- id").
  Fix: "id 's-bbbbbb' is not a decision ID, which is d- and six lower-case characters, like d-3m8qk2", and adjust `test_id_of_the_wrong_shape_says_so`.
  Parked for the next round touching `apply.py`.

## Text rules

Every changed message is British English, has no em-dash, and the one three-item list ("print it again with lodge draft <ref>, make the change on that print, and add it") carries the Oxford comma.

## Files read

`.claude/agents/rechecker.md`, the fix diff (`git diff bd95ef0 f4bf61f`, source and tests), the report's "Fix round 1" section, ledger lines 100 to 105.
Not read: anything outside the diff.
