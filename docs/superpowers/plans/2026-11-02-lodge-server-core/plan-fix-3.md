# Plan fix round 3: lodge server core

Answers `plan-recheck-2.md` (N2-r, m-a, m-b, m-c, and the mismatch rows of its preflight) of the plan at `2e7acf6`.
Line numbers are those of the plan after this round.
New probes are items 26 and 27 of `probes.md`, their sources in `probes/fix3/`.
Ruling made in this round, scope `process`, work item the plan: d-ca6wbw (narrows d-hshapm).

## Important

| Finding | What changed |
|---|---|
| N2-r default-filling functions outside `model.ts` | The suggested fix was checked against the calls before it was applied, and two of its eleven names fell away. Probe 26 counts, over `src/lodge` and `tests`, the calls of each core dataclass that leave a defaulted field out: `LengthGuidance` 6, `CoreSettings` 12, `Tree` 32, and `Filters` 45, but `Draft` 0 (built only at `src/lodge/core/drafts.py:45`, with all five fields) and `Snapshot` 0 (built only at `src/lodge/core/snapshot.py:70` and `tests/core/builders.py:94`, with all seven; `threads` is the argument at `builders.py:101`, so the recheck's reading of `builders.py:94` as filling it does not hold). d-ca6wbw: a dataclass gets a default-filling function only where a call leaves a defaulted field out, defined beside its type, so `draft` and `snapshot` would be functions nothing calls, which the porting rule refuses (line 27) and knip would not report behind the front door (line 44). Line 33 now says so; line 92 adds the ruling to "Calls made"; line 716 allows the default-filling function of a `PascalCase` name of `__all__` defined in the module that defines the type, and names the nine (`decision`, `specEntry`, `area`, `problem`, and `message` of `model.ts`, `coreSettings` and `lengthGuidance` of `settings.ts`, `tree` of `snapshot.ts`, and `filters` of `search.ts`); Task 4's Produces (line 431) adds `coreSettings` and `lengthGuidance` (`tests/core/test_settings.py:10`), Task 6's (line 531) adds `tree` (`tests/core/test_check_threads.py:52`, `tests/core/test_apply.py:61`) and says `Snapshot` has none, Task 5b's (line 511) says `Draft` has none, and Task 9b's (line 669) adds `filters` (`tests/core/test_search.py:38`). The carried constructions the recheck cites were each read: `LengthGuidance()` and `CoreSettings(length=LengthGuidance(), import_sources=())` at `test_settings.py:10`, `CoreSettings()` at `test_check_threads.py:29`, `Tree(None, files)` at `test_check_threads.py:52` and `test_apply.py:61`, and `Filters()` at `test_search.py:38`, all imported from `lodge.core`. |

## Minor

| Finding | What changed |
|---|---|
| m-a `isDigit`'s comment | Line 442 ends "Python's 808 characters and the 90 of the isDigit item below (probe 23)". |
| m-b `\d` in `feedback.py` | Line 694, in Task 10: `\p{Nd}` takes the 90 code points of probe 23 that Python's `\d` refuses, and the report lists them for `_CODE`, `_DATE`, and `_NUMBER`. Probe 27: Python's `\d` on a `str` matches exactly the 680 code points `isdecimal` takes, so the 90 are the same set. |
| m-c a forgotten `entry` removal | Each Step 4 of a task that takes a file out of `ts/knip.json`'s `entry` now checks that `entry` no longer names it: Task 5a (line 498, `yamlio.ts`), 5b (line 518, `headers.ts`), 6 (line 540, `document.ts` and `fields.ts`), 7b (line 579, `derive.ts`), 8b (line 620, `check-state.ts`), and 8c (line 637, `checks.ts`). Task 5a is not among the recheck's lines but takes `yamlio.ts` out like the others, so it gets the same check. |

## Preflight mismatches

| Row | Answer |
|---|---|
| 4 and 11 | N2-r: `coreSettings` and `lengthGuidance` in Task 4's Produces (line 431) and allowed by line 716. |
| 6 and 11 | N2-r: `tree` in Task 6's Produces (line 531) and allowed by line 716; `Snapshot` has no default-filling function (d-ca6wbw), so `snapshot` is neither produced nor allowed. |
| 9b and 11 | N2-r: `filters` in Task 9b's Produces (line 669) and allowed by line 716. |
| Task 4 against itself | Line 33 and line 431 now agree (N2-r), and the comment and the item on `isDigit` give one count (m-a). |
| Task 11 against itself | Line 716 allows each default-filling function line 33 makes (N2-r). |
| 5b and 7b (agreed, `draft` named for completeness) | `Draft` has no default-filling function (line 511, d-ca6wbw). |

## Not changed

- d-hshapm's own text: d-ca6wbw narrows which dataclasses its "default-filling function of each dataclass among them" covers.
- The raw U+200B in `plan-recheck-1.md` and U+2028 in `plan-review-practice.md`: review records, which the recheck reports and does not count.
- The design and `lodge spec`: no finding asks for a change to either.
