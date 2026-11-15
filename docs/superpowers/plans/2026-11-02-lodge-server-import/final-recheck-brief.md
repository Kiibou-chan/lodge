# Brief: recheck of the final fix wave

Worktree `/var/tmp/lodge-import-final`, branch `server-import-final`; read-only except a disposable clone under `mktemp -d` outside the lane for mutations.
Check the fix diff `server-import..server-import-final` against only the findings it answers (`~/.cache/lodge-work/codex/plan4/sonnet-final-review.md`: Important `push_without_force`, Minors 1, 3, 6, 7, plan 3 M-a and M-c) and `final-fix-1-brief.md`, `final-fix-1-report.md`.
Confirm by running: adding `--force` at the push in `ts/src/git/export.ts` fails the new test in a scratch clone; the shared rule module is the only home of the branch, remote, and path rules and `git` imports it without loosening a structure rule; control characters are refused at set time; `round-trip.ts` exits 2 on usage; the three plan docs hold no machine path; sign-in-options flood does not evict a pending registration challenge; an add over 8 MiB, chunked or by Content-Length, gets 413 with the usage error JSON, memory stays bounded by the cap plus one chunk, and exactly the cap succeeds.
Also: modules at most 300 lines, no new dependency, `Bun.spawnSync` only, British English, no em-dashes, public-repo rule (briefs exempt), `sh scripts/check.sh` green.
Final message: `N Important, M Minor` and one line each for any finding with file:line and the command that shows it.
