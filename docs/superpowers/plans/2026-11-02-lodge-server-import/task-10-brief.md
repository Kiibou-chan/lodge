# Brief: Task 10 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

You build Task 10 of the plan named above, in the worktree `/var/tmp/lodge-import-roundtrip`, on branch `server-import-roundtrip`.
Read `CLAUDE.md` first, then the plan's header, "Global Constraints", "Calls made", "Names this plan consumes", "Review Focus", and the section "### Task 10" in full; those are your requirements, with the exact values to use verbatim.
The plan was written for a sandbox: you have full access (d-94tynf) and network, but `Bun.spawnSync` stays the rule for spawning, and the "Coordinator" steps are not yours.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
Run `sh scripts/check-ts.sh` last; it must exit 0. The structure checks (`ts/tests/structure/`, run by `bun test`) gate the finished task, not intermediate commits.
Never run `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name. `bun install --frozen-lockfile` in `ts/` is allowed.
Never edit earlier briefs, reports, or reviews in `docs/superpowers/plans/2026-11-02-lodge-server-import/` or in `docs/superpowers/plans/done/`: they are history.
Line handles in the plan drift as tasks land; re-locate them by content.
Biome runs with `--error-on-warnings`; `noTemplateCurlyInString` fires on strings holding a dollar sign and brace, so build those by concatenation. Modules stay at 300 lines or fewer; split before the structure test does.
Public repository: no personal paths, machine names, or secrets in code, tests, docs, or the report; fixtures are synthetic.
User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.
Front doors: `#api`, `#app`, `#cli`, `#git`, `#store`; tests may import a package's non-front-door files only where the structure rules allow (see `ts/tests/structure/`).
Commit when the gate is green, with explicit paths: `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, message ending with the trailer `Co-Authored-By: Codex <noreply@openai.com>`; then `git push origin server-import-roundtrip`. Never touch `main`.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-import/task-10-report.md`: what you changed per file, each test added or carried with its first failing output (or the mutation it failed against, as a table with a `file:line` column), the commands you ran and their last lines, every deviation from the plan with the reason, anything you were unsure of. Commit the report too.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.

## Notes for this task

Merged names (re-alignment against the code, no meaning difference; use these over the plan's wording):
- `zeroTwoRepository(layout, extra)` in `ts/tests/git/zero-two.ts` returns `{ repository, rev, settingsRev }`; `isolateGit` in `ts/tests/git/isolated.ts`; `world()` in `ts/tests/api/world.ts` returns `exporters`, `targets`, `createProject(project, settings)`, `asPerson(operation, body)`, `clock`; `FixedClock` in `ts/tests/app/fakes.ts`.
- `readStore(repository, rev, settingsRev?)` from `#git` returns a `StoreRead` (files, attachments, settings text); `zeroTwoCoreTable(text)` from `#cli`; `importStore(copy, project, requester, projects, settings, clock)` and `ZeroTwoCopy` from `#app` (`coreSettings(table)` there is the throwing one); `exportFiles(current, attachmentTexts)` and `exportMessage(files)` from `#app`; `exportStore(target, files, message)` from `#git` takes a `Target` (`repository`, `branch`, `remote`).
- `ts/scripts/` does not exist yet; check how `ts/package.json`, knip, and `scripts/check-ts.sh` treat scripts, and keep the gate green (knip must not flag the script as unused).
- Parity: `held` in `ts/tests/parity.test.ts` defaults to `plans = [2, 3]`; make plan 4's `changed` rows held too (the plan's Task 10 `parity.test.ts` paragraph, including `ported_files_exist` and `rowMissing` for the hook row against `post-tool-use.test.ts` alone); the three hook rows are `tests/hook/test_post_tool_use.py`, `tests/e2e/test_hook_feedback_after_hand_edits.py`, and `tests/gitstore/repos.py` is a plan 4 `changed` row too: run the test and fix rows whose Python test names the TypeScript files no longer carry only if the plan says so, else report it.
- The coordinator runs Steps 3 and 4 (`scripts/round-trip.sh` on a scratch clone); you write the script and may run it once yourself on a clone to see it work, but it must never write into this repository (`git status --short lodge/` empty afterwards).
