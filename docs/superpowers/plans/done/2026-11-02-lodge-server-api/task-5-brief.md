# Brief: Task 5 of `docs/superpowers/plans/done/2026-11-02-lodge-server-api.md`

You build Task 5 of the plan named above, in the worktree `/var/tmp/lodge-api-C`, on branch `server-api-c`.
Read `CLAUDE.md` first, then the plan's header, "Global Constraints", "Exports read in a later task", "Calls made", "Order and lanes", and the section "### Task 5" in full; those are your requirements, with the exact values to use verbatim.
The plan was written for a sandbox: you have full access (d-94tynf) and network, but no test opens a socket (Global Constraints), and the "Coordinator" steps are not yours.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Run `sh scripts/check-ts.sh` last; it must exit 0. The structure checks (`ts/tests/structure/`, run by `bun test`) gate the finished task, not intermediate commits.
Never run `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name. `bun install --frozen-lockfile` in `ts/` is allowed.
Never edit earlier briefs, reports, or reviews in `docs/superpowers/plans/done/2026-11-02-lodge-server-api/` or in `docs/superpowers/plans/done/`: they are history.
Line handles in the plan drift as tasks land; re-locate them by content.
Biome runs with `--error-on-warnings`; `noTemplateCurlyInString` fires on strings holding a dollar sign and brace, so build those by concatenation. Modules stay at 300 lines or fewer; split before the structure test does.
Plan 1's rules for catch guards, `ok` literals, patterns, and sorting apply to `core` only; new packages are not held to them.
Public repository: no personal paths, machine names, or secrets in code, tests, docs, or the report; fixtures are synthetic.
User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
Front doors: each package is imported only through `#core`, `#app`, `#store`, `#api`, `#cli` (its `index.ts`); tests may import a package's non-front-door files only where the structure rules allow (see `ts/tests/structure/`).
Commit when the gate is green, with explicit paths: `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, message ending with the trailer `Co-Authored-By: Codex <noreply@openai.com>`; then `git push origin server-api-c`. Never touch `main`.
Write your report to `docs/superpowers/plans/done/2026-11-02-lodge-server-api/task-5-report.md`: what you changed per file, each test added or carried with its first failing output (or the mutation it failed against, as a table with a `file:line` column), the commands you ran and their last lines, every deviation from the plan with the reason, anything you were unsure of. Commit the report too.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## Notes for this task

- Lane C continues from Task 4, merged into `server-api`; this worktree already holds it. Lanes A and B (Tasks 2 and 3) are separate; touch nothing in `ts/src/cli`.
- A request whose path is not under `/api/v1/` is `not-found` (`nothing here`) whatever its method: check the path first, then the method (so a `GET /` is not-found, not usage).
- `ts/tests/api/world.ts` needs an option for a server that is not set up (no `accounts.setUp`), or the `project_create_before_setup_is_usage` test builds its own handler; either way the default world is set up for `https://lodge.test` and `ada`.
- `openDatabase` is async: await it in `world.ts`.
- Plan 4 consumes `ApiOptions` and `lodgesOver` from `#api` exactly as the plan's Interfaces block spells them; do not rename or reshape them.
