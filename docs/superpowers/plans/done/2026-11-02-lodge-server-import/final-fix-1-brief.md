# Brief: final fix wave for `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Worktree `/var/tmp/lodge-import-final`, branch `server-import-final`; read `CLAUDE.md` first (test-first, structure rules, modules at most 300 lines, `Bun.spawnSync` only, no new dependency, Biome `--error-on-warnings`, British English, no em-dashes, public repository).
The whole-branch Sonnet review is `~/.cache/lodge-work/codex/plan4/sonnet-final-review.md`; read it for the probes.
Each fix starts with a test that fails first (for the Important: it must fail when `--force` is added at `ts/src/git/export.ts:124`; run that mutation and show it red, then revert).

1. Important: `push_without_force` (`ts/tests/git/export.test.ts:112-120`) does not catch a force push. Use a `git` shim on `PATH` that logs its arguments, or advance the remote between fetch and push, so adding `--force` fails the test.
2. Minor 1: one rule module in `app` for the branch-name rule, the remote `-` rule, and the "outside lodge/" path rule, and one outcome and target type, imported by `ts/src/git/export.ts` (the structure rules allow `git` to import `#app`; check `ts/tests/structure_rules` and `ts/tests/structure/` first, and if an edge would need a loosened rule, leave this item parked and say so); the two Proxy bodies in `exportingProjects` share one bind step.
3. Minor 3: `exportTargetProblem` rejects control characters (NUL included) at set time.
4. Minor 6: `ts/scripts/round-trip.ts` exits 2 for a usage error, as `CliError` does; test the exit code.
5. Minor 7: replace the machine-layout paths in `plan-review-practice.md`, `plan-recheck-1.md`, and `preflight.md` (folder `docs/superpowers/plans/2026-11-02-lodge-server-import/`) with `<worktree>`; briefs and the ledger are exempt.
6. Plan 3 parked M-a: a flood of unauthenticated `sign-in-options` must not evict a pending challenge (`ts/src/api/passkeys.ts:16,46-56`): give sign-in-options its own cap, or per-source limits within what the code already knows, without changing any request or response shape.
7. Plan 3 parked M-c: an add over the 8 MiB limit answers with the API's usual error body and content type instead of Bun's bare 413 (`ts/src/api/serve.ts:16`, `http.ts:56`); keep the status 413 and add only the body.
Left parked, named in the report: minors 2 beyond M-a and M-c, 4, 5, 8, 9.
Write a report `docs/superpowers/plans/2026-11-02-lodge-server-import/final-fix-1-report.md` (each fix, its first failing output, commands and last lines, deviations).
Gate: `sh scripts/check.sh` exit 0. Commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`; push `server-import-final`; never touch `main` or `server-import`.
If you must choose between readings, choose and note it in the report; do not stop.
Final message: DONE, one line on the checks, and what you left parked.
