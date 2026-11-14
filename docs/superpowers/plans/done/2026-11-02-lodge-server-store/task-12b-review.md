# Task 12b review

Reviewed commit 4395942 on `server-store`, in a scratch worktree at that commit (removed after; `ts/node_modules` was a symlink to the build worktree's).
Gate `sh scripts/check-ts.sh` there: exit 0, 1266 pass, 2 todo, 0 fail.
`sh scripts/check.sh` (the Python half, run by the coordinator) was not run.
Method: read the diff and the code it touches, ran one differential probe, then applied 36 one-edit mutations to `src` (31 and 5), running `bun test tests/app tests/store` and `tsc --noEmit` after each and reverting.
Killed by a test: 24; killed only by `tsc` (an unused name): 3 more; survivors: M11, M13, M15, M16, M17, M18, M19, M22, M23, M24, M26, M30, N03, N05 (below, merged into findings).

## Differential probe: both stores give the same answers

I ran one scenario over `MemoryStore` and over a real `SqliteStore` from `SqliteProjects.storeFor` (project owned by `ada`, `bo` added as owner): an agent's add held with `awaits` `ada`; `bo` and an agent refused `approve` with `Forbidden`; `bo` refused `decline`; an unknown number `NotFound`; `ada` approves (`PUBLISHED`, `held()` empty); a second approval and a late decline both `NotFound`; a second add declined, then `approve` `NotFound`; an add with an attachment held, approved, and its attachment text stored.
The two answer lists are identical except the hold number (the SQLite store numbers a hold by its event `seq`, 4 after the project and two member events, where `MemoryStore` numbers by `rev`); no test pins a number, so this is not a finding.
The probe was a scratch file and is gone.

## Pass 1: correctness

The behaviour matches the plan's Task 12b rule and d-znagqe, d-thvvzx for what the code does.
- A hold is made after the check passes and before anything is published (`ts/src/app/writes.ts:158-176`); a dry run answers `DRY_RUN` with `awaits` and holds nothing (`:149-157`); a failing check answers `CHECK_FAILED` and holds nothing (`:135-144`); two persons are refused (`ts/src/app/awaits.ts:15-18`).
- `approve` refuses an unknown or settled number with `NotFound` and a wrong approver or an agent with `Forbidden` (`ts/src/app/held.ts:15-20`), re-reads the hold at each attempt, runs the add as that person at the approval's own clock, and publishes with `approves` so the files and the approval land in one transaction (`ts/src/app/writes.ts:84-97`, `:177-184`); `ts/src/store/sqlite-store.ts:135-152` checks the hold inside the transaction, so the second of two racing approvals answers `REJECTED` and the app turns that into `NotFound` after the final refresh (`writes.ts:99`).
- A failing check or a refusal at approval leaves the hold open (`approval_runs_the_check_again` shows it).
- `decline` is refused for another person and for an agent by the same `authorised` as `approve`, cleans the reason, refuses an empty one, and calls `store.decline`, which settles once.
- Confirmation (`ts/src/app/confirm.ts:67`) calls `add` with the actor's own name as `decided_by`, so it is never held; `AddOutcome.HELD` reaches no other caller.
- The gate and stale-list interplay: a hold moves `heads.rev` in both stores, which only makes an in-flight publish on an older tree `REJECTED` and retried (three attempts); `StaleList` in `confirm.ts:59` compares IDs, not the revision, so a hold never stales a confirmation list.
- Dry-run and importing paths: `importing` is stored in the hold and read back at approval (`held.ts:32`, `writes.ts:90`); it works, but see I-1.
- Agents and non-owners: an agent or a non-owner person who drafts a decision naming an owner is held; a person naming themselves is published; a draft naming a name outside `people` (a role) is published as before (M2 killed).

No Blocking finding.

### I-1 (Important) What a hold keeps besides `drafts`, `person`, and `by` is asserted by no test, so approval can silently lose it

`ts/src/app/writes.ts:162-170` stores `attachments`, `importing`, and `message` in the hold, and `ts/src/app/held.ts:31-35` plus `writes.ts:88-95` read `attachments` and `importing` back at approval.
`ts/tests/app/held.test.ts:7-17` asserts only `seq`, `kind`, `person`, `by`, and `drafts`, and no approval test uses an attachment or `importing`.
Failure scenario (run): M16 stores `attachments: []`; an agent adds a decision listing `a.txt` with that attachment, it is held, and `ada`'s approval answers `CHECK_FAILED` (`requireListed` finds the decision listing `a.txt` with no attached file), nothing is published, and the hold stays open and can never be approved.
With the code as built the same scenario answers `PUBLISHED` with both paths, so the behaviour is right and only the test is missing; all 265 tests pass under M16.
M17 (`importing: false` in the hold), M18 (`message: ""`), and M22 to M24 (the approval ignoring the hold's `importing`, `attachments`, or `drafts`) survive for the same reason; M22 to M24 are also equivalent as built (see M-5).
Fix: add `a_held_add_keeps_its_attachments` (hold with an attachment, `held()` returns `attachments` and `importing` field for field, approval publishes the attachment path) and one with `importing: true` over a draft that passes the check, and assert `message` of `held()` equals what a published add of the same drafts commits with.

## Pass 2: practice

### M-1 (Minor) Hold order and the `held` wire value are not asserted at the app level

`ts/src/app/held.ts:12` returns the store's list; M26 reverses it and every test passes, because the app tests hold one add at a time.
The plan says `held()` lists oldest first.
M30 (`results.ts:5`, `HELD: "held for approval"` changed to `"held"`) also survives: tests compare through the constant, and plan 3 will map the text.
Fix: one test holds two adds and expects the order of `seq`; assert `AddOutcome.HELD` equals `"held for approval"` once in `ports.test.ts` or `held.test.ts`.

### M-2 (Minor) A wrong approver with an empty reason gets the reason's refusal, and a person's hold records the person's name, both unpinned

`ts/src/app/held.ts:40-43`: N03 moves the reason check before `authorised`, so `bo` declining `ada`'s hold with an empty reason answers `LodgeError` instead of `Forbidden`; every test passes (`decline_needs_the_person_and_a_reason` uses a valid reason for the wrong actor).
N05 sets `by` to `"agent"` for a person drafter (`writes.ts:161`); the one asserted `by` is the agent case.
Fix: add `await expect(lodge.decline(seq, " ")).rejects.toThrow(Forbidden)` and a `by: "bo"` expectation in `another_persons_add_is_held`.

### M-3 (Minor) `approve`'s in-loop refresh is redundant and untested beyond its last use

`ts/src/app/writes.ts:70-81` re-reads the hold, re-parses its drafts, and rebuilds the whole request on every attempt, though a hold is immutable, so the request equals the one built before the loop (M22 to M24 are equivalent mutants).
Only the "is it still open" part matters, and `ts/tests/app/held-approve.test.ts:101-109` kills only the final refresh (M14); removing the in-loop one (M15) changes only the number of `publish` calls against a settled hold (3 instead of 1, probed), not the answer.
The plan's "reading the holds afresh at each attempt" is therefore a rule no test enforces.
Fix: either keep the open-check per attempt and drop the re-parse (`refresh` returning nothing the loop uses), or add a test that a hold settled after the first rejection stops at the second attempt (`store.attempts` is 1).

### M-4 (Minor) `request.approves === null` in the UNCHANGED guard is unreachable

`ts/src/app/writes.ts:177`: a held add always contains a new decision, whose file always differs from the state, so `files.size` is never 0 on approval; M13 survives because no input reaches it.
Fix: drop the clause, or keep it with a comment naming the case it guards.

### M-5 (Minor) `{ ...w, actor: person(found.person) }` equals `w`

`ts/src/app/held.ts:29`: `authorised` already refuses any actor except `person(found.person)`, so M11 (passing `w`) is an equivalent mutant and the `person` import, with the rebinding, say nothing the line above did not.
Fix: pass `w`, or keep the rebinding if plan 3's service actors are expected to approve for a person (then say so and test it).

## Pass 3: design

### M-6 (Minor) `Lodge.held()` lists every person's holds to any actor

`ts/src/app/held.ts:11-13`: a drafted decision of `ada` with her quote is returned to `bo`, to an agent, and to a non-owner member alike; the plan leaves "plan 3 picks the actor's", and nothing here or in the tests says the filtering is plan 3's duty.
Failure scenario: plan 3's API forwards `held()` as is and a member reads another person's pending draft and quote.
Fix: a test or a comment-free naming that makes the contract plain, for example `held()` taking the person to filter by, or a plan 3 brief line (the coordinator's to add).

### M-7 (Minor) A retried add holds twice

`ts/src/app/writes.ts:158`: nothing detects that the same drafts are already held for the same person, so an agent that retries after a lost response leaves two holds, and `ada` can approve both, publishing two identical decisions (check 4's duplicate rules may or may not refuse the second; not probed).
Not in the plan or in d-znagqe; recorded so the coordinator can rule it before plan 3 relies on `held` numbers.
Fix: either accept it (a decline drops the extra) and say so in the ledger, or compare `drafts` of the open holds before holding.

Structure and process: `ts/src/app/writes.ts` is 265 lines, `held.ts` 44, `awaits.ts` 20, `write-attachments.ts` 28, tests 109, 70, and 17; imports run `held.ts → writes.ts → awaits.ts` and `writes.ts` imports nothing of `held.ts`, and `depcruise` and `knip` pass in the gate.
The move of `attached` and `requireListed` into `write-attachments.ts` is a pure move (the diff deletes them from `writes.ts` and adds them unchanged).
No dependency was added; no em-dash and no American spelling in the new files or the report (searched).
The plan's twelve test names are all present; `ports.test.ts` expects `awaits` and `held` null; `Approved` and `AddOutcome.HELD` are exported through `results.ts` and `front-door.test.ts` passes.
The builder committed and pushed as its brief directed; the report's table of first failures is consistent with the tests I ran.

## Files read

Read: the brief, the report, the plan's Task 12a, 12b, 12c, 9, 11 sections and "Interfaces for plans 3 and 4", `lodge show d-znagqe` and `d-thvvzx` with reasoning, `ts/src/app/{awaits,held,write-attachments,writes,results,lodge,state,confirm}.ts`, `ts/src/store/sqlite-store.ts` (first 150 lines), `ts/tests/app/{held,held-approve,held-support,fakes,support}.ts` and the `ports.test.ts` diff, `ts/tests/store/{support,seed,people.test}.ts`, `task-12a-review.md` (first 30 lines, for the form), `ts/src/core/apply.ts` (importing lines).
Not read: `ts/src/store/{events,read-tree,schema}.ts` (Task 12a's, reviewed there), `ts/tests/store/held*.test.ts`, `ts/src/app/threads.ts` (Task 12c's), Python sources, `lodge spec` in full, the other decisions the plan cites.
Not run: `sh scripts/check.sh`, `sh scripts/differential.sh`, anything over a git store.

Verdict: 0 Blocking, 1 Important, 7 Minor
