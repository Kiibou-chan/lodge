# Plan fix round 2: plan 3, the API, sign-in, and the command

Planner, fix round 2, on `server-api` from 5be9524, answering `plan-recheck-1.md` (new: 0 Blocking, 2 Important, 4 Minor) and the coordinator's two renamed rulings.
Status: done; 6 fixed, 0 rejected, 0 parked; no new ruling, so nothing added to lodge.

## Findings

- N-1: the recheck's first fix; Task 7a's parity bullet sets `tests/test_wheel.py`'s row back to `planned` with `plan` 3 before widening the `ported_files_*` tests, so they never read `ts/tests/e2e/binary.test.ts` before Task 8 creates it; Task 8's Step 4 flip to `changed` with `dropped` now describes a real flip. Chosen over the `dropped`-key scope because it touches one row and leaves every `changed` row's shape as plans 1 and 2 write it.
- N-2: Task 7a's guide changes keep line 26 as lodge 0.2 has it, which `guide_says_waiting_first` asserts verbatim (`tests/e2e/test_guide.py:58`), and put the refusal of `--by author` through a token in a clause of line 24, which no carried test asserts; the guide keeps 60 lines.
- N-3: Task 8's d-amxk94 bullet names plan 4's plan on `origin/server-import` and has the coordinator paste its "Names consumed" table, as of the brief's day, into Task 8's brief.
- N-4: Task 4's `AgentToken.id` comment reads `from tokenId (Task 5)`.
- N-5: Task 6's `held` reads a decision's `title`, `statement` (without its reasoning), and `quote` through `parseDraft` then `recordFromDraft(draft, "", null, null)`, an entry's or area's as `{name, kind, title, text}`, and a `Problem` from either call as `problem` and the raw text; Task 6 consumes `recordFromDraft`.
- N-6: Task 5's operation list writes `check` (`gate` false, passed positionally, as plan 2's `check(gate)` takes it).
- Recheck's note on `plan-fix-1.md`: the correctness review's M-6 to M-9 now sit under "Correctness review, remaining".

## Renamed rulings (coordinator)

- d-pmaw3a is replaced by d-j28rp0 on `server-store` (narrowed by d-n9nm8h, the import's check): the plan's six citations now name d-j28rp0 (Global Constraints' Porting bullet, Calls made 15, "Names consumed from plan 2", the parity rows of `test_broken_agent_decision_warns_above_show.py` and `test_check_and_gate.py`, and Task 7a's `handEdit`).
- d-4zg8q3 is replaced by d-d0vca9 on `server-core`: the plan's four citations now name d-d0vca9 (Global Constraints, the Structure bullet, `ApiOptions.log`'s comment, and Task 8's `main.ts`).
- The records d-81ps01 and d-amxk94 cite d-pmaw3a and plan 4's lines 64-76 in their reasoning; they are left as written, since a record never changes and neither statement depends on the citation.
