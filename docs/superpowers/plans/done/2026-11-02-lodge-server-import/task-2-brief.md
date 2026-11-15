# Brief: Task 2 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

You build Task 2 of the plan named above, in the worktree `/var/tmp/lodge-import-git`, on branch `server-import-git`.
Read `CLAUDE.md` first, then the plan's header, "Global Constraints", "Calls made", "Names this plan consumes", "Review Focus", and the section "### Task 2" in full; those are your requirements, with the exact values to use verbatim.
The plan was written for a sandbox: you have full access (d-94tynf) and network, but `Bun.spawnSync` stays the rule for spawning, and the "Coordinator" steps are not yours.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Run `sh scripts/check-ts.sh` last; it must exit 0. The structure checks (`ts/tests/structure/`, run by `bun test`) gate the finished task, not intermediate commits.
Never run `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name. `bun install --frozen-lockfile` in `ts/` is allowed.
Never edit earlier briefs, reports, or reviews in `docs/superpowers/plans/2026-11-02-lodge-server-import/` or in `docs/superpowers/plans/done/`: they are history.
Line handles in the plan drift as tasks land; re-locate them by content.
Biome runs with `--error-on-warnings`; `noTemplateCurlyInString` fires on strings holding a dollar sign and brace, so build those by concatenation. Modules stay at 300 lines or fewer; split before the structure test does.
Public repository: no personal paths, machine names, or secrets in code, tests, docs, or the report; fixtures are synthetic.
User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
Front doors: `#core`, `#app`, `#store`, `#api`, `#cli` (each `index.ts`), and the new `#git`; tests may import a package's non-front-door files only where the structure rules allow (see `ts/tests/structure/`).
Commit when the gate is green, with explicit paths: `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, message ending with the trailer `Co-Authored-By: Codex <noreply@openai.com>`; then `git push origin server-import-git`. Never touch `main`.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-import/task-2-report.md`: what you changed per file, each test added or carried with its first failing output (or the mutation it failed against, as a table with a `file:line` column), the commands you ran and their last lines, every deviation from the plan with the reason, anything you were unsure of. Commit the report too.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## Notes for this task

- Lane `git` (worktree `/var/tmp/lodge-import-git`) builds Task 2; Task 3 follows in the same lane and a fresh brief. Another lane builds Task 5 beside you; touch nothing of `app`.
- Task 1's `ZERO_TWO_STORE` is at `ts/tests/core/zero-two-store.ts`. `decodeUtf8`/`encodeUtf8` are exported by `#core`; `LodgeError` by `#app`. Check each name in "Names this plan consumes" against the merged code; if one differs in meaning, ask through the ask tool.
- Add `"#git": "./src/git/index.ts"` to `ts/package.json` `imports`; check `ts/tests/structure/` and `.dependency-cruiser.cjs` for where the package must be registered (the structure table names every package; plan 1, Task 3). Extend the table minimally as the plan's Global Constraints "Structure" line says.
- `ts/tests/parity.json`: flip the two rows as Step 3 says.
