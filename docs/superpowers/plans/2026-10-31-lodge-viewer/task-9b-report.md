# Task 9b report

BLOCKED.
The first section dry run emitted check 4 lines, so the Global Constraints require stopping.
No Task 9b add ran, no record was added, and no entry was edited or retired.
All work remains under `.drafts/task9b/`.
No code or tests changed, so no new tests or first-failure outputs apply.

## Prepared records, not published

The two decision drafts have no permanent IDs.
The dry run's d-k6bbzx is provisional and was never used as a link.

| Reserved entry | Decision draft | Design lines | Claim |
| --- | --- | --- | --- |
| s-m4esa0 | rests-decision.md | 104-105 | Entries store the dependencies they require |
| s-7wbv0e | rests-decision.md | 106-107 | Link changes preserve freshness and review state |
| s-wvza5q | rests-decision.md | 108-109 | Dependency checks reject invalid targets and cycles |
| s-63mwy2 | rests-decision.md | 110 | Mentioned entries prompt dependency feedback |
| s-kba448 | rests-decision.md | 112,114 | Reads show dependency risks and reverse links |
| s-sjqg5k | rests-decision.md | 113 | Reaffirm an entry after its dependency changes |
| s-yj4r17 | threads-decision.md | 76-81 | Threads record doubts and questions |
| s-ejjpek | threads-decision.md | 83-84,90 | Open and read threads on a record |
| s-4wna3s | threads-decision.md | 84-85 | Thread commands append replies and closing messages |
| s-77krr7 | threads-decision.md | 81,86-87 | Author messages retain verbatim words and provenance |
| s-nda0br | threads-decision.md | 88-89 | Waiting separates agent and author work |
| s-r7c3wn | threads-decision.md | 92-94 | Doubts propagate while questions mark their record |
| s-nxakwv | threads-decision.md | 96-98 | Acting on a thread requires a decision |
| s-3e6zp3 | threads-decision.md | 100 | Open threads do not fail the gate |

## Prepared edits, not applied

| Entry | Intended edit and reason |
| --- | --- |
| s-a67fqm | Three record kinds, including threads. |
| s-evv024 | Thread storage under `lodge/threads/`. |
| s-0s9m2d | Separate waiting groups for agent and author. |
| s-ms14fq | Check 5 covers immutable published thread content and closure. |
| s-wcv4en | Level 1 carries doubt, question, and dependency marks. |
| s-7ah5n7 | Insert the brief's thread exception after its first sentence; otherwise unchanged. |
| s-0yzshh | Add the link action and its check 4 restriction. |
| s-01k42c | Link changes raise no review flag. |
| s-j70a0k | Eight checks, including dependency cycles. |
| s-edgt71 | Reads run all eight; altered threads join check 5. |
| s-8f6scf | Store rests_on on entries; derive reverse links. |
| s-aw5a1j | Check 6 covers edited entries newly resting on retired entries. |

The Rests on draft proposes narrowing d-zerbz9's decision-only storage claim and d-3epcjd and d-4032xv's seven-check claims.
None was narrowed.
No author decision is proposed for narrowing.

## Dry-run feedback and answers

Exact output is preserved in `.drafts/task9b/threads-dry.txt`.
The draft was submitted with all eight new thread entries and the six required edited entries.

Related decisions: d-a16d4m, d-96n7j6, and d-a3e8kb.
Answer: no to each; the dependency links and Markdown storage statements stay true, while threads extend the existing model.
Numeric feedback requested handles for 78, 5, and 1 in the decision reasoning.
Answer: these refer to design line 78 and the named checks, rather than measurements; before any later add, explicit design or record handles should be supplied to remove ambiguity.
Area-order notes are expected insertions.

The stopping checks were:

```text
check 4: d-96n7j6: lists link for s-0s9m2d, which changes more than rests_on; list it with action edit
check 4: d-96n7j6: lists link for s-ms14fq, which changes more than rests_on; list it with action edit
check 4: d-a16d4m: lists link for s-0s9m2d, which changes more than rests_on; list it with action edit
not published: the check failed
```

These are existing dependency-migration decisions, not the proposed decision, whose changes already use edit.
Changing those existing decisions or check implementation is beyond this records task and the explicit stop rule.
The Rests on section was drafted but not dry-run or added after the stopping check.
Its changed-since reaffirmation pass remains to be prepared from the actual state after a successful thread add.

## Changed since and verification

Counts use `lodge spec | grep -c ', changed since)'`, matching the warning suffix rather than prose.
Before Task 9b: 0.
After the stopped dry run: 0.
Both reads are retained under `.drafts/task9b/`.
Task 9a's fix used the Global Constraints sandbox index and object recipe; Task 9b performed no real add.
Records were read only through lodge.
No record file was hand-edited, staged through the real index, committed, or pushed.

The shared final builder gate passed: `ruff format --check` reported 479 files formatted, `ruff check` passed, mypy found no issues in 194 source files, and vulture exited 0.
The non-socket pytest run passed 1363 tests in 35.90 seconds.
The separately required port test passed, with six deselected.
`lodge check` and `lodge check --gate` printed `ok`; the gate also printed expected area-order and uncommitted-record notes.
Socket-bound `tests/viewer/test_server.py` and the server-starting tests in `tests/e2e/test_view.py` remain for the coordinator's outside-sandbox gate.
`lodge show d-mzkt6e` now shows current without a narrowing mark.
The final actual dependency-warning count is 0.

The concern is the check 4 refusal on the first Task 9b batch, despite that batch using edit for its entry changes.
The existing-state gate remains green because the refused batch published nothing.
