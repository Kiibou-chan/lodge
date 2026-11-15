# Task 7a, fix 1 report

The three missing pins are restored, and malformed JSON answer envelopes produce a one-sentence CLI error.
The two review files are unchanged, and the other minors are left alone.

## 1. Orphaned waiting output

Test: `ts/tests/app/thread-fix-paths.test.ts:11`, with the new `run(["waiting"], io)` assertion at `:52`.
The existing synthetic Lodge and MemoryStore supply `waitingAll()` through `toWire`, the response, and the client's decoder; the CLI project fixture supplies only the local settings and repository directory.
The test requires `about s-zzzzzz, not found` in the waiting output.
After writing the assertion, replacing both `threadHead(t, waiting.titles.get(t.about))` calls in `ts/src/cli/thread-output.ts` with `threadHead(t, waiting.titles.get(t.about) ?? "unknown")` made `orphaned_thread_outputs` fail at the new assertion.
The focused run had 3 passes and 1 failure, and the mutation was restored.
This assertion was written after the existing formatter code; no formatter implementation change was needed.

## 2. Ordering assertions

Tests: `ts/tests/e2e/show-levels.test.ts:19` and `:30`, and `ts/tests/e2e/waiting.test.ts:43`, `:49`, and `:88`.
Every `indexOf` ordering comparison in those files now requires both operands to be present first, including the author subgroup's decision and thread.
After writing the assertions, probe A replaced `section("Reasoning", shown.level2)` in `ts/src/cli/output.ts` with `section(shown.level1.id.startsWith("s-") ? "Wrong" : "Reasoning", shown.level2)`.
`show_entry_reasoning_lists_its_decisions` failed at the heading presence assertion, with 2 passes and 1 failure in the file.
Probe B replaced `...listed.items.map(formatLevel1),` in `ts/src/cli/thread-output.ts` with `...(waiting.forAuthor.length ? [] : listed.items.map(formatLevel1)),`.
`waiting` failed at the flagged decision presence assertion, with 1 pass and 1 failure in the file.
Both mutations were restored.
These assertions were written after the existing output code; no output implementation change was needed.

## 3. Init settings body

Test: `ts/tests/cli/client.test.ts:113`, with the request body assertion at `:126`.
The spy requires POST to `project-create` with project `work` and exactly the core settings, including `[length]` title_chars 40 and `[import]` sources notes.md and archive.md.
After writing the test, replacing `{ settings: settings.core }` in `ts/src/cli/commands.ts` with `{ settings: {} }` made `init_sends_core_settings` fail, with 15 passes and 1 failure in the file.
The mutation was restored.
This test was written after the existing init implementation; no command implementation change was needed.

## 4. Malformed answer envelope

Test: `ts/tests/cli/client.test.ts:141`, with the parameterised assertion at `:162`.
All 20 cases were written and run before changing `ts/src/cli/client.ts`; the file then had 16 passes and 20 failures.
The old client implementation is the failing control: null and other non-object bodies, missing results on success and check-failed, and unusable errors all fail the new expectation.
The corrected client raises `CliError("<url> answered something other than a lodge answer")`, rendered through `run` as exit 2, empty stdout, and one stderr sentence.
The coordinator ruled to validate only the envelope: a non-array object, an own result key for 200 and check-failed with null allowed, and an error object with string kind and message for error answers.
No operation-specific result validation was added.
The new malformed-answer cases were written before the production fix; the valid null result is also exercised by the init spy.

## Organisation and validation

Existing output and file-order cases moved unchanged to `ts/tests/cli/client-output.test.ts`, with shared response and invocation helpers in `ts/tests/cli/client-support.ts`.
Each test file creates its own harness so the existing project cleanup remains local to that file.
`ts/tests/cli/client.test.ts` is 166 lines, and `#cli` exports are unchanged.
The final focused run passed all 52 tests across the five affected test files.
`sh scripts/check-ts.sh` exited 0: 1,762 tests passed, 0 failed, and 4,815 expectations ran across 148 files.
Biome reported informational literal-key suggestions, and the dependency check found no violations.
`git diff --check` passed.
The tests for items 1 to 3 are retrospective pins against already implemented behaviour, each demonstrated red with its named mutation before restoration.
The item 4 tests preceded the client fix, and no tests were added after that fix.
