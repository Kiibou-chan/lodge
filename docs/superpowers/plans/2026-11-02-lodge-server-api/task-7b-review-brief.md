Read `CLAUDE.md` in this worktree first.

Outcome: a read-only correctness review of the range `47afa32..026243d` (Task 7b of `docs/superpowers/plans/2026-11-02-lodge-server-api.md`, report `docs/superpowers/plans/2026-11-02-lodge-server-api/task-7b-report.md`), written to `docs/superpowers/plans/2026-11-02-lodge-server-api/task-7b-codex-review.md`.

Scope: edit no source or test file; the review file is the only file you write; run mutations only in a scratch copy (`git worktree add` under a temporary folder, removed afterwards).

Evidence to check against: the plan's "### Task 7b" section and its parity rows (the substitutions of d-bwb1tt, the changes of d-4qv0xb, the exact assertions named for `add-attach`, `add-import`, `held`, `same-second`, `threads`) and lodge 0.2's `tests/e2e/test_*.py` for the carried files.
Look for: a carried test that asserts less than its Python test (every assertion, including negative ones and `str.index` semantics, where `indexOf` must first assert presence); a test that does not fail against the mutation the report names (run it); a change to `ts/src/cli` or `ts/tests/e2e/server.ts` without a test that failed before it; `held.test.ts` pinning provisional marks and the dry-run note; parity rows and `knip.json` as the plan says; a test that opens a socket or reads a real repository.

Findings: Important or Minor, each with file and line and a probe or failing test, none without; list what you checked and found sound.

Done when the file is written; commit it with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-c`.
Unsettled design goes to the ask tool.
