# Brief: Task 3 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

You build Task 3 of the plan named above, in the worktree `/var/tmp/lodge-import-git`, on branch `server-import-git`.
Read `CLAUDE.md` first, then the plan's header, "Global Constraints", "Calls made", "Names this plan consumes", "Review Focus", and the section "### Task 3" in full; those are your requirements, with the exact values to use verbatim.
The plan was written for a sandbox: you have full access (d-94tynf) and network, but `Bun.spawnSync` stays the rule for spawning, and the "Coordinator" steps are not yours.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Run `sh scripts/check-ts.sh` last; it must exit 0. The structure checks (`ts/tests/structure/`, run by `bun test`) gate the finished task, not intermediate commits.
Never run `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name. `bun install --frozen-lockfile` in `ts/` is allowed.
Never edit earlier briefs, reports, or reviews in `docs/superpowers/plans/2026-11-02-lodge-server-import/` or in `docs/superpowers/plans/done/`: they are history.
Line handles in the plan drift as tasks land; re-locate them by content.
Biome runs with `--error-on-warnings`; `noTemplateCurlyInString` fires on strings holding a dollar sign and brace, so build those by concatenation. Modules stay at 300 lines or fewer; split before the structure test does.
Public repository: no personal paths, machine names, or secrets in code, tests, docs, or the report; fixtures are synthetic.
User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
Front doors: `#core`, `#app`, `#git`, `#hook`, `#store`, `#viewer`, `#cli` (as in CLAUDE.md); tests may import a package's non-front-door files only where the structure rules allow (see `ts/tests/structure/`).
Commit when the gate is green, with explicit paths: `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, message ending with the trailer `Co-Authored-By: Codex <noreply@openai.com>`; then `git push origin server-import-git`. Never touch `main`.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-import/task-3-report.md`: what you changed per file, each test added or carried with its first failing output (or the mutation it failed against, as a table with a `file:line` column), the commands you ran and their last lines, every deviation from the plan with the reason, anything you were unsure of. Commit the report too.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## Notes for this task

Task 2 is merged into your branch (read `ts/src/git/`, `ts/tests/git/` first; its report is `task-2-report.md`).
Also fix three Minors from Task 2's review in the files Task 3 touches, each test-first (see the failing test first):
1. `ts/tests/git/read-store.test.ts` (invalid-`rev` case, about line 35): pass a valid settings revision with the invalid primary revision, so deleting only the primary-revision guard in `read-store.ts` makes the test fail. Prove it by that mutation, then restore.
2. `ts/src/git/paths.ts` `resolvePath` (about line 26): follow a dangling symlink as Python's non-strict `resolve` does. Failing probe: `linked -> missing/child`, `resolvePath(<root>/linked/../file.md)` must be `<root>/missing/file.md` (now `<root>/file.md`). Add a test in `ts/tests/git/paths.test.ts` (or the file that holds the resolvePath tests); keep every existing resolvePath test passing.
3. `ts/tests/git/repos.ts` (about line 18): the `git` helper uses `.trim()`; use `strip` from `#core`, matching Python `.strip()` (U+0085 and U+FEFF). Add a test that stores `"\u0085record\u0085"` as a blob and reads it through the helper expecting `"record"`.
List these three in the report under their own heading.
