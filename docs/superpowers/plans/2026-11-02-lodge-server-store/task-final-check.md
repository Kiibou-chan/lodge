# Final check of plan 2 (`server-store`, HEAD a6a4897)

Reviewer: rechecker and last independent read.
Incremental notes; the verdict line closes the file.
Scratch worktree `/var/tmp/lodge-review-final2` (detached at a6a4897) holds every gate run and mutation.

## Part A, recheck of fix wave 456071c

Each mutation was applied alone in the scratch worktree, the whole `bun test` suite run, and the file restored (`git status` clean afterwards).

| Finding | Mutation | Failing tests | Result |
| --- | --- | --- | --- |
| I-1 | `threads.ts:169` `if (!check.ok)` to `if (false)` | `ask_` and `reply_checks_against_the_published_tree` | killed |
| I-2 | `threads.ts:168` `load(state.published)` to `load(state.current)` | the same two | killed |
| I-2 | `writes.ts:124` the same swap | `add_refuses_a_rewrite_already_present_in_current` | killed |
| I-3 | `read-tree.ts:32` files project filter dropped | `trees_members_and_attachments_are_confined_to_the_project` | killed |
| I-3 | `read-tree.ts:44` owners project filter dropped | the same | killed |
| I-3 | `projects.ts:52` `members()` project filter dropped | the same | killed |
| I-3 | `sqlite-store.ts:69-71` attachment project filter, lower bound, upper bound, each dropped | the same | 3 killed |
| M-5 | `sqlite-store.ts:99` `path.includes("\\")` dropped | `path_outside_lodge_is_refused` | killed |
| M-7 | `sqlite-store.ts:40` held `orderBy("seq", "asc")` to `desc` | `holds_are_returned_in_event_order` | killed |
| M-7 | `projects.ts:56` member sort dropped | `members_are_sorted_by_name` | killed |
| M-7 | `read-tree.ts:21` `rev: eb.ref("rev")` to `rev: 0` | `touching_a_head_keeps_its_revision` | killed |
| M-7 | `projects.ts:90` `actorText(actor)` to `"author"` | `store_for_attributes_events_to_its_actor` | killed |
| M-1 | `close?: boolean` put back on `MessageOptions` | `tsc`: three unused `@ts-expect-error` at `tests/app/message-options.test.ts:5,7,9` | killed (by the gate's `tsc`, not by `bun test`) |

The staged-drift fixture tests what its names say: `project()` holds one decision (`FIRST`, `tests/app/support.ts:28-29`), so in the `add` test the restored rewrite is the only difference between `current` and `published`, and in the `ask` and `reply` tests the missing `FIRST` is.
The I-3 test's own files `lodge/a` and `lodge/attachments0` sit just below and just above the attachment range, which is why both bounds are killed.
M-6 removed the guard (`sqlite-store.ts:129` before the fix); see A-1 below for what that changed.

I-4: the brief's `git grep` for the user path and the build directory prints the I-4 finding's own text (`final-review.md:58`, `final-fix-1-codex.log:108`) and the eight `pamac-build-user/...` lines of the four `task-1{1,2a,2b,2c}-fix-1-codex.log` files, nothing else.
A case-blind `git grep` of the login name outside `Kiibou-chan` (the public GitHub identity, ruled acceptable in `done/2026-10-29-lodge/final-review-design.md:105`) and `git grep` of the host name print nothing.
The tree is clean; history is not, see A-3.

### A-1 (Minor) · Deleting the `base.rev` guard made `SqliteStore` accept non-canonical spellings of the head

Handle: `ts/src/store/sqlite-store.ts:130` (`touchHead(tx, this.project, Number(base.rev))`), with the removed line `if (base.rev === null || !/^[0-9]+$/u.test(base.rev)) return PublishOutcome.REJECTED;`.
The review's M-6 premise was that the malformed cases at `tests/store/sqlite-store.test.ts:55-59` fail through `NaN`; only `"x"` does.
`Number(null)` is 0 and `Number("2.0")` is 2, so `null`, `"2.0"`, and `"-1"` are refused there only because they are stale (the head is 3 after the first publish), and the guard's real behaviour, refusing a different spelling of the current head, was never tested and is now gone.
Verified by running a probe test in the scratch worktree: on a fresh store with head `2`, `publish` with `rev` set to `"2.0"`, `" 2"`, `"0x2"`, or `"2e0"` (each spelling the head at that moment) returns `published` for all four.
`MemoryStore.publish` compares strings (`ts/tests/app/fakes.ts:112`, `base.rev !== String(this.rev)`), so the fake refuses what the real store now accepts, which is a differential the app tests cannot see.
Scenario: plan 3 or 4 carries the base revision as client text (an HTTP field or header), a client sends `"7.0"` or `" 7"`, and the server publishes against it where the Python git store and the fake both refuse.
Bounded by the parked Task 7b D-1 (publish trusts the caller's base), hence Minor.
Fix: restore the guard as `if (base.rev === null || String(Number(base.rev)) !== base.rev) return PublishOutcome.REJECTED;` (or the old regex), and add to the stale-base test one case that spells the live head differently, `${current.rev}.0` read after the first publish, so the mutation dies.

### A-2 (Minor) · `close` is hidden from the types of `ask` and `reply` but still honoured at run time

Handle: `ts/src/app/lodge.ts:73-89` passes the caller's `options` object straight to `threads.writeMessage`, which destructures `close` from it (`ts/src/app/threads.ts:118`).
The fix answers M-1 at the type level only; `tests/app/message-options.test.ts` checks the types and nothing at run time.
Verified by running a probe test in the scratch worktree: `lodge.reply(id, "coordinator", "Because.", JSON.parse('{"close": true}'))` compiles (`JSON.parse` gives `any`) and returns `published` with the thread's `state` `"closed"`.
Scenario: plan 3's HTTP handler passes a parsed request body as the options of `reply`, and a reply closes its thread without going through `Lodge.close`.
Fix: in `Lodge.ask` and `Lodge.reply` pass `{ where: options.where, when: options.when, commit: options.commit }` rather than `options`, and add one run-time test that a `reply` given `{ close: true } as never` leaves the thread open.

### A-3 (Minor) · The scrubbed user path is still in the pushed branch history

Handle: `git log --oneline -S` of the user path over `main..server-store` gives 5d96603 (Task 12a, adds it) and 12a0e39 (removes it); `git branch -r --contains 5d96603` gives `origin/server-store`.
Scenario: a merge commit (not a squash) of `server-store` into `main` carries 5d96603 into `main`'s history on the public repository, and the remote branch already serves it.
The content is a login name close to the public `Kiibou-chan` identity, so the harm is small.
Fix: the author's call, recorded in the ledger: squash-merge plan 2 and delete `origin/server-store` afterwards, or accept it.

## Part B, last independent read of the branch against main

Gate: `sh scripts/check.sh` in the scratch worktree at a6a4897 exits 0 (ruff and ruff format pass, mypy strict no issues in 195 files, pytest 1399 passed, `lodge check --gate` ok, dependency-cruiser 201 modules with no violations, knip, `bun test` 1299 pass, 2 todo, 0 fail, `differential.sh` 0 differences).

### B-1 (Important) · Another person's confirmation makes a flagged decision unconfirmable for the person it waits for

Handle: `ts/src/core/confirmation.ts:16-25` (`confirmableIds` drops a decision once `d.confirmedBy.has(id)`, a confirmation by anyone), read by `ts/src/app/confirm.ts:40` (`expectedIds`), by `behindArea` (`confirmation.ts:28`), and by `Shown.confirmable` (`ts/src/app/reads.ts:57`); the flags themselves clear per person (`ts/src/core/derive-flags.ts:99-113`).
The seam is between Task 13 (flags per person, d-4spcem) and the carried confirm path of Tasks 6 and 11, where lodge 0.2 had one person, so "confirmed by anyone" meant "confirmed by the author".
Verified by running two probe tests over `MemoryStore` with people `{ada, bo}` in the scratch worktree (deleted afterwards):
- An agent decision `d-bbbbbb` replacing `ada`'s `d-aaaaaa` awaits `["ada"]`; `bo` confirms it (`published`), the flag still awaits `["ada"]`, and `ada`'s `confirm(["d-bbbbbb"], …)` then throws `StaleList: the list changed since the page was loaded; nothing was written`.
- The plan's own case `touching_two_people_waits_for_both` (Task 13, plan line 680): `d-bbbbbb` replaces `ada`'s decision and narrows `bo`'s, awaiting `["ada", "bo"]`; `ada` confirms and it awaits `["bo"]`; `bo`'s `confirm` then throws the same `StaleList`, and the flag stays `["bo"]`.
So through `Lodge`, a flag can be cleared by confirmation for at most one person, and any other owner can block it, against the Goal's "a review flag on a person's decision clears only when that person confirms" and d-4spcem's "that person's later confirmation or replacement clears their part"; the only way left is a replacement, which changes the record the person wanted to approve.
The core test `touching_two_people_waits_for_both` passes because it builds the second confirmation as a record, never through `confirm`; no app test confirms a decision twice with two people.
Scenario: in plan 3's viewer, `bo` confirms an agent decision on `ada`'s entry; `ada` then sees it still awaiting her, with no confirm button (`Shown.confirmable` false) or, from a page loaded earlier, a "list changed" refusal on every retry.
Fix: give `confirmableIds` (and so `behindArea` and `Shown.confirmable`) the person, and drop a decision only when a confirmation of that person names it (the per-person reading `confirmedByPeople` of `derive-flags.ts:30` already makes); pass `w.actor.name` from `confirm.ts`, and the reading actor's name, or each person's set, from `reads.ts`.
Test: in `ts/tests/app/people.test.ts`, the two-person case above through `Lodge.confirm`, `ada` then `bo`, ending with `derive(...).awaiting` empty, and the one-person case where `bo` confirms first and `ada` still can.
Since it changes what a confirmation means for a second owner, the reading belongs to d-4spcem; record the fix's rule with `lodge add` (scope `process`, work item the plan) before the code.

### B-2 (Minor) · The concurrent-writers parity row says `ported` where the plan says `changed`

Handle: `ts/tests/parity.json:565-570` (`"status": "ported"` with a `why` citing design line 72), against plan Task 8's Files line (plan line 452, "changed, design line 72") and Task 14 Step 1 (plan line 693, "`tests/gitstore/test_concurrent.py` is `changed`").
`held()` in `ts/tests/parity.test.ts:14-15` accepts both statuses, so no test sees the difference, and Task 14 Step 1 was ticked against the wrong status.
Scenario: plan 3 or a later audit counts the rows the server changed against Python by status, and the store's one deliberate behaviour change is counted as a straight port.
Fix: set the row's `status` to `changed`; the `why` already says what changed.

### B-3 (Minor) · The ledger does not close the plan

Handle: `docs/superpowers/plans/2026-11-02-lodge-server-store-progress.md:51` is the last line ("Task 14 minors: complete"); there is no line for Task 14's closing checks, the final review, fix wave 456071c, or this check, though plan Task 14 Step 5 (plan line 697) says the ledger line says the plan ends.
Task 14's Steps 1 to 3 hold apart from B-2, verified by running them: the `planned` rows name only plan 3 (`tests/app/test_thread_fix_paths.py` among them), `knip.json`'s entry is plan 1's two patterns, and `git grep -n "Bun.serve\|fetch(" ts/src/app ts/src/store` prints nothing.
Scenario: the plan is moved to `done/` and a later session reads the ledger as stopping at Task 14's minors, with no record of the final review's verdict or of which findings were parked.
Fix: the coordinator adds the Task 14 line, the final-review line (`final-review.md` verdict, fix wave 456071c, this check's verdict), and the parked items, before the move to `done/`.

### Checked and not reported

- The plan's "Interfaces for plans 3 and 4" (plan lines 89 onwards), in part: `Lodge` takes its actor in the constructor and every operation is `async` (`ts/src/app/lodge.ts:24-109`), `ask` and `reply` no longer type `close` (A-2 covers run time), and no module under `ts/src/app` or `ts/src/store` calls `Bun.serve` or `fetch(`; I did not compare every exported name against the interface block.
- `awaitsPerson` (`ts/src/app/awaits.ts`), `held.ts`'s approve and decline (a person only, `Forbidden` otherwise), and the hold path of `writeMessage` read as the plan and d-vwsnz5 say; a member who is not an owner is treated as a role by that decision, so it is not reported.
- A person may write under a role name; plan Task 11 allows it.
- Public-repository scan: no personal path, host name, or user name in the tree beyond A-3's history and the I-4 lines above; fixtures use made-up names (`ada`, `bo`, `storage`, `other`).
- The parked items (final review M-2 to M-4 and M-8 to M-13, Task 7b D-1, codec speed) were not re-reported.

## Files read

`final-review.md`, `final-fix-1.md`, `final-fix-1-report.md`, the diff of 456071c (`ts/src/app/threads.ts`, `ts/src/store/sqlite-store.ts`, and the tests `message-options`, staged drift, `held`, isolation, `projects`, `sqlite-store-refusals`, `touch-head`), the plan (lines 1-230, 447-483, 556-580, 666-697), the ledger, `lodge spec` (model, writing, and check sections), `lodge search --by author`, `lodge show d-4spcem`, `ts/src/app/{writes,threads,held,awaits,confirm,lodge}.ts`, `ts/src/store/read-tree.ts`, `ts/src/store/projects.ts` (40-92), `ts/src/store/sqlite-store.ts` (40-144), `ts/src/core/derive-flags.ts` (1-120), `ts/src/core/confirmation.ts` (16-39), `ts/tests/store/sqlite-store.test.ts` (1-80), `ts/tests/app/support.ts`, `ts/tests/app/people.test.ts` (in part), `ts/tests/app/fakes.ts` (searched), `ts/tests/app/builders.ts` (in part), `ts/tests/parity.test.ts` (1-60), `ts/tests/parity.json` (searched), `knip.json`.

## Files not read

`ts/src/app/reads.ts` beyond a search, `write-attachments.ts`, `state.ts`, `results.ts`, `ports.ts`, the store's `events.ts` and `schema.ts`, most of `ts/tests`, the structure rule sources, the per-task briefs, reports, and reviews (searched only), the Python sources, `docs/research`, and the server design document.

Scratch worktree removed after the last run.

Verdict: 0 Blocking, 1 Important, 5 Minor
