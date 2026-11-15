Read `CLAUDE.md` in this worktree first.

Outcome: a read-only correctness review of the range `03383f6..e40f55a` (Task 7a of `docs/superpowers/plans/done/2026-11-02-lodge-server-api.md`, report `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-7a-report.md`), written to `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-7a-codex-review.md`.

Scope: edit no source or test file; the review file is the only file you write; run mutations only in a scratch copy (`git worktree add` under a temporary folder, removed afterwards).

Evidence to check against: the plan's "### Task 7a" section (every printed line, the client's error mapping, the held lines, `guide.md`'s changed lines, `server.ts`, `project.ts`, `support.ts`, the parity rows) and lodge 0.2's `src/lodge/cli/{commands,output,thread_output,threads}.py` and `tests/e2e/*.py`.
Look for: a printed line that differs from lodge 0.2 or the plan; a function a carried test does not pin (mutate it and run its tests); a carried test that asserts less than its Python test; the order of reading drafts, settings, and message files; `fromWire` against `toWire`; the held and provisional lines; token handling (`LODGE_TOKEN` only in `Authorization`, never printed); `#cli` exporting more or less than the plan lists.

Findings: Important or Minor, each with file and line and a probe or failing test, none without; state what you checked and found sound in one short list.

Done when the file is written; commit it with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-c`.
Unsettled design goes to the ask tool.
