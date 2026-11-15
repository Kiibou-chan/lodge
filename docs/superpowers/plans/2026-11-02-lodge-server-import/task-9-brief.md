# Brief: Task 9 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

You build Task 9 of the plan named above, in the worktree `/var/tmp/lodge-import-hook`, on branch `server-import-hook`.
Read `CLAUDE.md` first, then the plan's header, "Global Constraints", "Calls made", "Names this plan consumes", "Review Focus", and the section "### Task 9" in full; those are your requirements, with the exact values to use verbatim.
The plan was written for a sandbox: you have full access (d-94tynf) and network, but `Bun.spawnSync` stays the rule for spawning, and the "Coordinator" steps are not yours.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Run `sh scripts/check-ts.sh` last; it must exit 0. The structure checks (`ts/tests/structure/`, run by `bun test`) gate the finished task, not intermediate commits.
Never run `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name. `bun install --frozen-lockfile` in `ts/` is allowed.
Never edit earlier briefs, reports, or reviews in `docs/superpowers/plans/2026-11-02-lodge-server-import/` or in `docs/superpowers/plans/done/`: they are history.
Line handles in the plan drift as tasks land; re-locate them by content.
Biome runs with `--error-on-warnings`; `noTemplateCurlyInString` fires on strings holding a dollar sign and brace, so build those by concatenation. Modules stay at 300 lines or fewer; split before the structure test does.
Public repository: no personal paths, machine names, or secrets in code, tests, docs, or the report; fixtures are synthetic.
User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
Front doors: `#core`, `#app`, `#git`, `#hook`, `#store`, `#api`, `#cli`, `#viewer` (as in CLAUDE.md); tests may import a package's non-front-door files only where the structure rules allow (see `ts/tests/structure/`).
Commit when the gate is green, with explicit paths: `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, message ending with the trailer `Co-Authored-By: Codex <noreply@openai.com>`; then `git push origin server-import-hook`. Never touch `main`.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-import/task-9-report.md`: what you changed per file, each test added or carried with its first failing output (or the mutation it failed against, as a table with a `file:line` column), the commands you ran and their last lines, every deviation from the plan with the reason, anything you were unsure of. Commit the report too.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## Notes for this task

Merged names (re-alignment against the code, no meaning difference; use these over the plan's wording):
- `#hook` (`ts/src/hook/index.ts`) exports `run(read, out, context, resolve, cwd)` (returns `Promise<0>`), `respond`, and the types `HookContext` (`repoRoot, dataRoot, frozen, server`) and `Resolve`; `#git` exports `repoRootOf`, `isFolder`, `resolvePath`, `run`; `parseHookSettings(table)` is in `#app` (`ts/src/app/hook-settings.ts`), throws `LodgeError`; `isolateGit` is in `ts/tests/git/isolated.ts`.
- `Io` is in `ts/src/cli/commands.ts` (`cwd, env, fetch, out, err, version`); add `hook?: () => Promise<number>` there. Plan 3's `ts/tests/cli/settings.test.ts` has `hook_is_left_alone` at line 140 and 145: change it to `hook_is_checked` as the plan says.
- `main.ts` now carries Task 8's `open`/`listen` wiring; add `io.hook` only to the `run(argv, {...})` Io literal.
- `ts/src/cli/settings.ts` has `tomlTable` (Task 8) over which `loadSettings` runs; `hookContextFor` may use it for the parse, but must read `.lodge.toml` as bytes strictly (`readExact`) and give null on any error.
Parked minors from Task 4's review (`ts/src/hook/`, the first round touching it), take them here: M-1 the false trailing-newline comment at `post-tool-use.ts:59-60` (`(?![\s\S])` does nothing; fix the comment or the code, with a test if behaviour changes); M-2 add a test pinning "whatever `dataRoot` says" for moved projects; M-3 a moved project whose `lodge/` is a symlink gets no advice because `join(root, "lodge")` is not passed through `resolve` (lines ~73-74; make it behave as the Python hook does, with a test); M-4 the glob escape set is partly untested (add the missing cases); M-5 add a test of a path outside the repository given as an absolute path. Report: `~/.cache/lodge-work/codex/plan4/sonnet-task4-review.md` has the probes.
