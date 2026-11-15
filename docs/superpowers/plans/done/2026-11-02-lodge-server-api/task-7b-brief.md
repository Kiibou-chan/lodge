Read `CLAUDE.md` in this worktree first, then the plan header, "Global Constraints", and "### Task 7b" in full in `docs/superpowers/plans/done/2026-11-02-lodge-server-api.md` (your requirements), the parity table rows with task 7b in that file, and `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-7a-report.md` (the helpers `server.ts`, `project.ts`, `support.ts` and how the 7a tests use them).

Outcome: the writing tests of lodge 0.2's `tests/e2e` (the plan's list) run in process against `testServer()` and pass, with `held.test.ts` pinning the held and provisional lines, and each carried test seen failing against a named mutation of Task 7a's code.

Scope: the test files and `ts/tests/parity.json` and `ts/knip.json` the plan's Task 7b "Files" names; Task 7a's modules (`ts/src/cli`) only where a carried test finds them wrong, each such fix named in the report with the test that failed before it.
The sandbox rule holds: no test in the gate opens a socket.
Modules and tests stay at 300 lines or fewer; Biome runs with `--error-on-warnings`; never `bun add`; never edit earlier briefs, reports, or reviews.

Evidence: Python sources `tests/e2e/test_*.py` named in the plan; the substitutions of d-bwb1tt and the changes of d-4qv0xb as Task 7b's last two bullets spell them; Task 7a's review lessons (`task-7a-codex-review.md`): an `indexOf` comparison must first assert both operands are present, since Python's `str.index` raises, and each ported assertion must keep everything its Python test asserts.

Test-first: write the carried files and `held.test.ts`; run `cd ts && bun test tests/e2e` and mutate the code each test is to pin (the plan's examples: `readDraft` keeping `\r\n`, `added_lines` leaving out `(provisional)`, attachments sent under their full path, the 422 answer printed as an error), see each fail, revert.

Done when `sh scripts/check-ts.sh` exits 0 with the parity rows written and green again; write `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-7b-report.md` (per test the Python test it carries, the mutation that fails it with `file:line`, each fix in 7a's modules with its failing test, each substitution of d-bwb1tt and change of d-4qv0xb); commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-c`; do not run the Coordinator step.
Unsettled design goes to the ask tool.
