# Brief: recheck of Task 11a fix round 1

Worktree `/var/tmp/lodge-import-records`, branch `server-import-records`; read-only (no `lodge add`, no edits; probe `lodge add --dry-run` or a disposable clone under `mktemp -d` outside the lane only).
Check the fix diff `3601469..f0e5fee` against only the findings it answers (`~/.cache/lodge-work/codex/plan4/sonnet-task11a-review.md`: Important I1 and Minors M1 to M9) and `task-11a-fix-1-brief.md`; read records through `uv run --frozen --quiet lodge show ID [--reasoning]`.
Confirm: I1's entry states both environments' rules and loses nothing the pre-3601469 text held; each corrected entry is now true against `ts/src` (M2, M3); M8's step numbers match the design's Build order; the new decisions are coordinator decisions, narrow or replace no author decision, and carry only the numbers they use; the report names each dropped sentence (M6) and the parked items; `lodge check` prints ok.
Also check the fix introduced nothing new (prose rules: British English, no em-dashes, Oxford comma, one sentence per line; entries within 150 words).
Final message: `N Important, M Minor` and one line each for any finding with the record ID and the command that shows it.
