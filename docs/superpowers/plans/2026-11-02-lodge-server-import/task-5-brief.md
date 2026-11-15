# Brief: Task 5 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

You build Task 5 of the plan named above, in the worktree `/var/tmp/lodge-import-import`, on branch `server-import-import`.
Read `CLAUDE.md` first, then the plan's header, "Global Constraints", "Calls made", "Names this plan consumes", "Review Focus", and the section "### Task 5" in full; those are your requirements, with the exact values to use verbatim.
The plan was written for a sandbox: you have full access (d-94tynf) and network, but `Bun.spawnSync` stays the rule for spawning, and the "Coordinator" steps are not yours.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Run `sh scripts/check-ts.sh` last; it must exit 0. The structure checks (`ts/tests/structure/`, run by `bun test`) gate the finished task, not intermediate commits.
Never run `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name. `bun install --frozen-lockfile` in `ts/` is allowed.
Never edit earlier briefs, reports, or reviews in `docs/superpowers/plans/2026-11-02-lodge-server-import/` or in `docs/superpowers/plans/done/`: they are history.
Line handles in the plan drift as tasks land; re-locate them by content.
Biome runs with `--error-on-warnings`; `noTemplateCurlyInString` fires on strings holding a dollar sign and brace, so build those by concatenation. Modules stay at 300 lines or fewer; split before the structure test does.
Public repository: no personal paths, machine names, or secrets in code, tests, docs, or the report; fixtures are synthetic.
User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
Front doors: `#core`, `#app`, `#store`, `#api`, `#cli` (each `index.ts`); tests may import a package's non-front-door files only where the structure rules allow (see `ts/tests/structure/`).
Commit when the gate is green, with explicit paths: `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, message ending with the trailer `Co-Authored-By: Codex <noreply@openai.com>`; then `git push origin server-import-import`. Never touch `main`.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-import/task-5-report.md`: what you changed per file, each test added or carried with its first failing output (or the mutation it failed against, as a table with a `file:line` column), the commands you ran and their last lines, every deviation from the plan with the reason, anything you were unsure of. Commit the report too.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## Notes for this task

- Lane `import` (worktree `/var/tmp/lodge-import-import`) builds Task 5; another lane builds Task 2 (`git`) beside you; touch nothing of `git`.
- Check each name in "Names this plan consumes" against the merged code (`ts/src/app`, `ts/src/core`, `ts/tests/app/fakes.ts`: `MemoryStore`, `FixedClock`, `START`); if one differs in meaning, ask through the ask tool. `Projects` is in `ts/src/app/ports.ts`.
- Task 1's `ZERO_TWO_STORE` is at `ts/tests/core/zero-two-store.ts`.
- Add the new names to `ts/src/app/index.ts` and `ts/tests/app/front-door.test.ts`'s allowed additions.
