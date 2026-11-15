Read `CLAUDE.md` in this worktree first.

Outcome: a read-only correctness review of the range `372b49d..65030ce` (Task 8 of `docs/superpowers/plans/2026-11-02-lodge-server-api.md`, report `docs/superpowers/plans/2026-11-02-lodge-server-api/task-8-report.md`), written to `docs/superpowers/plans/2026-11-02-lodge-server-api/task-8-codex-review.md`.

Scope: edit no source or test file; the review file is the only file you write; run mutations only in a scratch copy (`git worktree add` under a temporary folder, removed afterwards).

Evidence to check against: the plan's "### Task 8" section in full, probes 4 and 5 of `probes.md`, `ts/knip.json`, `ts/tests/parity.json`, and plan 4's consumed names in `task-8-brief.md`.
Look for: `main.ts` not clearing `LOG_TOKENS` and `LOG_STREAM` before any other statement after the imports (mutate and run `environment.test.ts`); `open(data)` not awaiting `openDatabase`, or building `ApiOptions` with a different clock, entropy, or `log` than the plan names; `listen` leaking a signal handler, resolving before `server.stop()` settles, or starting a second shutdown on a repeated signal; the exit code and the exact streams of `run` through `main.ts` differing from lodge 0.2; an export knip no longer reports because it was tagged `/** @public */` although something in this branch reads it, or removed although plan 4 consumes it; a `/** @public */` tag on a name that plan 4 does not consume and that no front-door test reads; the parity rows (`tests/test_entry_point.py` ported, `tests/test_wheel.py` changed with a `dropped` entry that names what the binary test replaces); the binary test leaving a temporary folder or inheriting more than `PATH` from the environment; a socket opened by a test of the gate; a structure check loosened.

Findings: Important or Minor, each with file and line and a probe or failing test, none without; list what you checked and found sound.

Done when the file is written; commit it with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-c`.
Unsettled design goes to the ask tool.
