Read `CLAUDE.md` in this worktree first, then the "Global Constraints" and "### Task 9: The page" sections of `docs/superpowers/plans/2026-11-02-lodge-server-api.md` (your requirements, with the exact headers and policy to use verbatim), and probe 3 in `docs/superpowers/plans/2026-11-02-lodge-server-api/probes.md` (text imports, d-5kskm3).

Outcome: `handler` answers `GET /` with the page and `GET /page.js` with its script, under the plan's headers and content security policy; every other `GET` stays `not-found`; the script calls only `/api/v1/<operation>` and writes no HTML.

Scope: create `ts/src/api/page.html`, `page.js`, `page.ts`, `text.d.ts`; edit `ts/src/api/http.ts` (two `GET` routes only) and `ts/tests/api/page.test.ts` (new).
`ts/src/api/index.ts` gains no export; `ts/src/cli`, `ts/src/main.ts`, and plan 4's files are out of scope.
Biome lints `page.js` and `page.html` too.

Evidence: the plan's Task 9 "Interfaces" lists the sections the page holds, the operations the script calls, and the `held` kinds it shows (Task 6's `held` answer, `ts/src/api/person.ts`); the sandbox rule of the plan holds: no test opens a socket.

Test-first: the seven tests of Step 1 (`page_is_served_with_its_policy`, `script_is_served_as_javascript`, `other_paths_are_not_found`, `page_loads_only_its_script`, `script_writes_no_html`, `script_calls_only_the_api`, `every_operation_the_script_names_exists`); run `cd ts && bun test tests/api/page.test.ts` and see them fail before the code.
Mutate each of the two `GET` routes and the two checks on the script so you see the tests fail, then restore.

Done when `sh scripts/check-ts.sh` exits 0 (modules stay at 300 lines or fewer, Biome `--error-on-warnings`, `bun install --frozen-lockfile` allowed, never `bun add`); write `docs/superpowers/plans/2026-11-02-lodge-server-api/task-9-report.md` (per file what changed, each test with its first failing output, deviations); commit with explicit paths as `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, trailer `Co-Authored-By: Codex <noreply@openai.com>`, and push `server-api-d`.
Never edit earlier briefs, reports, or reviews.
Unsettled design goes to the ask tool.
