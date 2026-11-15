# Task 7a, fix round 1 recheck

Verdict: all four answered findings are resolved, with no new Important or Minor finding identified.
Reviewed `git diff 1b5751c 189dd27`, treating the review files as history.
The worktree's TypeScript files match `189dd27`, verified with `git diff --exit-code 189dd27 -- ts`.
Read `CLAUDE.md` first, the fix brief and report, both original reviews, and the plan's Task 7a requirements.
`lodge waiting` reported nothing waiting for an agent or the author.

## Answered findings

### Important: Codex finding 1, resolved

Handles: `ts/tests/app/thread-fix-paths.test.ts:30`, `:52`; mutation at `ts/src/cli/thread-output.ts:22` and `:25`.
The test retains its synthetic MemoryStore and Lodge, constructs the orphaned subject there, and now calls `run(["waiting"], io)` with that Lodge's `waitingAll()` response encoded through `toWire`.
The client decodes that response, and the test requires exit 0, empty stderr, and `about s-zzzzzz, not found` on stdout.
The added CLI project supplies the temporary repository directory and settings, while the response comes from the existing synthetic Lodge.

Ran the report's mutation, replacing both `threadHead(t, waiting.titles.get(t.about))` calls with `threadHead(t, waiting.titles.get(t.about) ?? "unknown")`.
`cd ts && bun test tests/app/thread-fix-paths.test.ts` exited 1: 3 passes and 1 failure, at line 52 in `orphaned_thread_outputs`.
The received output printed `unknown` instead of the required orphan subject sentence.
Restored the original bytes immediately afterwards.

### Important: Codex finding 2, resolved

Handles: `ts/tests/e2e/show-levels.test.ts:22`, `:30`; `ts/tests/e2e/waiting.test.ts:43`, `:49`, and `:88`.
Read every `indexOf` occurrence under `ts/tests/e2e`, not just the two original handles.
There are five ordering comparisons, and all five now require both operands' presence in the same string before comparing their positions.
This includes both show headings, the entry's Reasoning heading and decision, both waiting group headings in each waiting test, and the flagged decision and thread within the author subgroup.
The subgroup assertions also reject an absent subgroup before optional `indexOf` could conceal it.

Ran probe A exactly as reported: replaced `section("Reasoning", shown.level2)` in `ts/src/cli/output.ts:42` with `section(shown.level1.id.startsWith("s-") ? "Wrong" : "Reasoning", shown.level2)`.
`cd ts && bun test tests/e2e/show-levels.test.ts` exited 1: 2 passes and 1 failure, at line 30 in `show_entry_reasoning_lists_its_decisions`.
The required `## Reasoning` was absent and `## Wrong` was present.
Restored the original bytes before probe B.

Ran probe B exactly as reported: replaced `...listed.items.map(formatLevel1),` in `ts/src/cli/thread-output.ts:24` with `...(waiting.forAuthor.length ? [] : listed.items.map(formatLevel1)),`.
`cd ts && bun test tests/e2e/waiting.test.ts` exited 1: 1 pass and 1 failure, at line 49 in `waiting`.
The author subgroup lacked the flagged decision, so the presence assertion failed before the ordering comparison.
Restored the original bytes immediately afterwards.

### Important: Sonnet I-1, resolved

Handles: `ts/tests/cli/client.test.ts:113`, `:126`; mutation at `ts/src/cli/commands.ts:77`.
`init_sends_core_settings` configures non-default `[length]` and `[import]` values and spies on the request.
It requires one POST to the project's `project-create` URL and exactly `{project: "work", settings: {length: {title_chars: 40}, import: {sources: ["notes.md", "archive.md"]}}}`.
Thus the assertion covers the core table and excludes the local server settings.

Ran the report's mutation, replacing `{ settings: settings.core }` with `{ settings: {} }`.
`cd ts && bun test tests/cli/client.test.ts` exited 1: 35 passes and 1 failure in `init_sends_core_settings`, at line 138.
The request-body assertion inside the fetch spy throws, the client's fetch guard converts that into a CLI error, and the outer assertion rejects the resulting exit 2 instead of 0.
This still reliably kills the named mutation.
Restored the original bytes immediately afterwards.
The count differs from the report's intermediate 15 passes because the final file also contains the 20 malformed-envelope cases.

### Minor: Sonnet M2, resolved

Handles: `ts/src/cli/client.ts:46`, `:49`, `:54`, and `:57`; `ts/tests/cli/client.test.ts:141`, `:162`.
The implementation requires a non-null, non-array object envelope, an own `result` key for 200, a non-array error object with string `kind` and `message` for error answers, and an own `result` key for check-failed.
It raises the requested `CliError` sentence for an unusable envelope.
This matches the coordinator's supplied envelope-only ruling, including allowing null results.
Operation-specific decoding is outside that ruling.

Ran the report's old-implementation control by temporarily restoring only `ts/src/cli/client.ts` from `1b5751c`.
`cd ts && bun test tests/cli/client.test.ts` exited 1: 16 passes and all 20 malformed-envelope cases failed.
The failures include uncaught TypeErrors for null bodies, successful `undefined` output for missing results, and wrong error sentences for malformed errors.
Each new case asserts exit 2, empty stdout, and exactly the one-line lodge-answer error through `run`.
Restored the original bytes immediately afterwards.

An additional file-free `bun --eval` probe called the client with 200 `{result: null}` and 422 `{error: {kind: "check-failed", message: "failed"}, result: null}` and verified that both return null.
The same probe supplied response objects whose `result` was inherited and verified that both statuses raise the exact malformed-envelope `CliError`.
The committed init spy also exercises a valid 200 null result, and the existing error-kind tests exercise valid check-failed decoding and normal error mappings.

## New-problem scan

No new Important or Minor finding identified.
The production change is confined to envelope validation in `client.ts`, preserving the plan's version checks, request construction, error-kind mappings, and decoded-result hand-off.
The existing output and read-order tests moved to `client-output.test.ts` retain their assertions, and each test file creates its own harness using the existing temporary-project cleanup.
The new fixtures use synthetic project names, settings, and tokens, with in-process fetch responses and no git command or network access in the exercised mode.
No new personal path, machine name, secret, or another project's record was found in the changes under review.
The historical review files were not edited.

All changed TypeScript files are below 300 lines: `client.ts` 67, `thread-fix-paths.test.ts` 100, `client-output.test.ts` 170, `client-support.ts` 31, `client.test.ts` 166, `show-levels.test.ts` 42, and `waiting.test.ts` 97.
`git diff --exit-code 1b5751c 189dd27 -- ts/src/cli/index.ts ts/package.json` passed, confirming that the `#cli` exports and package mappings are unchanged.
The report explicitly identifies items 1 to 3 as retrospective pins against existing code and records their red mutations, as the fix brief requires.
It records the M2 cases as failing before the production fix; this recheck reproduces that red control, but does not independently establish the historical order of uncommitted edits.
Nothing remained unsettled by the brief, plan, or supplied coordinator ruling, so no coordinator question was needed.

## Validation and restoration

`sh scripts/check-ts.sh` exited 0 on the unmutated code: 1,762 passes, 0 failures, and 4,815 expectations across 148 files.
Biome reported 27 informational suggestions; the dependency check reported no violations.
After all restorations, the five affected test files passed together: 52 passes, 0 failures, and 195 expectations.
`git diff --check 1b5751c 189dd27` passed.
After each of the five mutation runs, `git status --short --untracked-files=no` was empty.
Final `git status --short` shows no tracked changes; this report is untracked alongside the five pre-existing untracked review-output files.
Only this report is retained from the recheck, and nothing was committed.
