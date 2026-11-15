# Brief: recheck of Task 10 fix round 1

Worktree `/var/tmp/lodge-import-roundtrip`, branch `server-import-roundtrip`; read-only except disposable copies under `mkdtemp` outside the lane.
Check the fix diff `ed56761..a143fc9` against only the findings it answers (`~/.cache/lodge-work/codex/plan4/sonnet-task10-review.md`: Important I-1, the Minors on the printed difference and the `bun` guard) and `task-10-fix-1-brief.md`.
For I-1, mutate each exit (the decision `1`/`0`, the import-refused exit, the usage exit) in a disposable copy and confirm a test fails.
Also check the fix introduced nothing new (modules at most 300 lines, no personal paths, no em-dashes).
Final message: `N Important, M Minor` and one line each for any finding with file:line.
