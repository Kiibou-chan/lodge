# Progress: docs/superpowers/plans/2026-10-31-lodge-viewer.md
Plan: written by the planner (3311c74); reviews correctness 2B/14I/16M and practice 3B/11I/10M (4f07618); advisor d-a3h9f3 on three findings held for the author; fix round 1 (61d91d1); recheck 1: 32 closed, 0 open, N1 Important and five Minors (`plan-recheck-1.md`).
Plan: N1 closed by the coordinator: 09:37 is right (her message of 2026-10-30 is stamped 09:37), so the design's range is corrected to 09:34 to 09:47; M-a and M-b fixed in the plan; M-c, M-d, and M-e passed to the builders of Tasks 4 and 9 as notes.
Preflight: the recheck's "Produces and Consumes after the splits" table (`plan-recheck-1.md`) is the scan; it found no mismatch.
Task 1: built by Codex (a3b7ebd); review 0 Blocking, 2 Important, 9 Minor (`task-1-review.md`); fix round 1 by Codex, each new or stronger test shown failing against the variant the review named (report, "Fix round 1"); gate green.
Task 1: complete; the fix round is rechecked by the final review, since each fix is a test with its recorded failing run.
Task 2: built by Codex (f23dd1d); review 0 Blocking, 1 Important, 8 Minor (`task-2-review.md`).
Task 3: built by Codex (68c4572).
Task 2: fix round 1 by Codex: I1 the reverse of `rests_on` reads "supports", and the design's line 114 says so too; M1 to M8 fixed; gate green.
Task 2: complete; the fix round is rechecked by the final review.
Task 3: review 0 Blocking, 3 Important, 7 Minor (`task-3-review.md`); fix round 1 by Codex, all fixed with failing-first evidence in the report, the CR rule kept once in core and called by Task 4's code; gate green.
Task 3: complete; the fix round is rechecked by the final review.
Task 4: built by Codex (a64c88e).
Task 4: review 0 Blocking, 1 Important, 10 Minor (`task-4-review.md`); the git layer passed every probe in scratch repositories.
Ruling d-wez56g: a thread whose subject no longer resolves is shown, not refused (`ThreadShown.about` is `Level1 | None`), fixed with Task 5's `thread_head` in one round.
Task 6a: built by Codex; the builder notes the stale-list check is not atomic with publication, which Task 6b's write lock covers.
Task 6b: built by Codex; the builder says test-first was not followed throughout, so its review checks that each security test fails on a gate without its rule.
Task 5: review 0 Blocking, 3 Important, 7 Minor (`task-5-review.md`).
Tasks 4 and 5: fix round 1 by Codex in one round, with ruling d-wez56g; all Importants and the cheap Minors fixed with failing-first evidence in both reports; gate green.
Task 4: complete. Task 5: complete. Both fix rounds are rechecked by the final review.
Task 6a: review 0 Blocking, 3 Important, 7 Minor (`task-6a-review.md`).
Task 6a: fix round 1 by Codex, each test shown failing against the review's mutation; a race between two viewer processes stays out of scope and is documented in the code; gate green.
Task 6a: complete; the fix round is rechecked by the final review.
Task 6b: review 0 Blocking, 2 Important, 8 Minor (`task-6b-review.md`), the gate probed with requests the tests do not send.
Task 7: built by Codex.
Task 6b: fix round 1 by Codex: a short body is refused with 400 and writes nothing, the size and thread-ID refusals each have a test that fails without them, a doubled Host or Origin is refused; m5 (a routing refactor) parked for the final wave; gate green.
Task 6b: complete; the fix round is rechecked by the final review.
Task 7: review 0 Blocking, 2 Important, 6 Minor (`task-7-review.md`); I2 was a `vulture_allow.py` line left out of the Task 7 commit, committed with the 6b fix.
Task 7: fix round 1 by Codex: the entry tree shows each entry once, with a later occurrence as a reference, tested on 26 entries each resting on the two before it; the Minors fixed with failing-first evidence; gate green.
Task 7: complete; the fix round is rechecked by the final review.
Ruling d-mkstz5: `lodge-on-itself` merged into `main` (f28eb5c, gate green there) so the entries are published and Task 8's `link` changes pass check 4; its final review folds into this plan's final review.
Task 8: first run blocked on check 4 before the merge; rerun after it.
Task 8: built by Codex after the merge: 27 links on 20 entries in 7 link decisions, 14 proposals dropped as mentions; `lodge waiting` unchanged.
Task 8: review 0 Blocking, 2 Important, 3 Minor (`task-8-review.md`): a false 'changed since' from a timestamp tie broken by ID, and about nine missed links.
Task 9a: built by Codex: six author decisions with her quotes at their minutes (37 author records, reasoning equal to quote in all), two coordinator decisions, 22 entries; 'changed since' 1 to 0.
