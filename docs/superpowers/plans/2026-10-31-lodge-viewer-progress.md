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
