# Task 5 report

Task 5 implements preparation and publication of a lodge 0.2 import.
The branch is `server-import-import`.

## Changes by file

| File | Change |
|---|---|
| `ts/src/app/importing.ts` | Adds `ZeroTwoCopy`, `prepareImport`, and `importStore`, keeping the result types private. |
| `ts/src/app/index.ts` | Exposes the three new names through `#app`. |
| `ts/tests/app/front-door.test.ts` | Adds precisely those three names to the existing allowed additions. |
| `ts/tests/app/importing.test.ts` | Adds 16 preparation tests using the synthetic `ZERO_TWO_STORE`. |
| `ts/tests/app/import-store.test.ts` | Adds ten publication cases, including both occupied-project cases. |
| `docs/superpowers/plans/2026-11-02-lodge-server-import/task-5-report.md` | Records the implementation, failing evidence, verification, and rulings. |

Preparation checks the original store against an empty state with its own settings and default author identity, checks writer round trips before mapping author decisions and messages, and then checks the mapped state with the project's settings and people.
The source snapshot supplies the parsed records and threads, so parsing uses the existing `load` implementation.
Both attachment paths and attachment text survive, including undecodable attachment bytes represented by the codec's surrogate escapes.
Only files ending in `/.gitkeep` are omitted.
Every refusal returns no prepared files or performs no publication, as appropriate.
Publication verifies the one owner, requester, and empty current tree before preparing the import, and publishes once through that owner's store.
The result counts paths and reports mapped decision and thread IDs.
The implementation is 172 lines, and both new test modules are below 300 lines.

## Consumed names

The Task 5 names were checked against `ts/src/app/ports.ts`, `errors.ts`, `time.ts`, and `index.ts`, the core front door and its implementations, and `ts/tests/app/fakes.ts`.
`Projects` is in `ports.ts`, as the brief states.
`Clock`, `stampOf`, `Store`, `PublishOutcome`, `Role`, `person`, `Projects.members`, `Projects.storeFor`, `Tree.people`, the settings wrapper, the check functions, and the writers match the required meanings.
`MemoryStore` accepts `people` and records publishes, `FixedClock` supplies the chosen stamp, and `START` is `2026-10-29T09:30:00+01:00`.
No dependency was needed or added.

## Test-first evidence

The initial batch was written before the implementation and run with `bun test tests/app/importing.test.ts tests/app/import-store.test.ts` from `ts/`.
Its first output was `0 pass`, `2 fail`, and `2 errors`, because the two modules could not import the missing functions.
In the table, A means `SyntaxError: Export named 'prepareImport' not found in module` at the app front door, and B means the equivalent missing `importStore` export.
The errors are reproduced without the machine's absolute checkout path.
Two additional cases were checked against targeted mutations, which were then reverted before verification.

| file:line | Test | First failing output or mutation |
|---|---|---|
| `ts/tests/app/importing.test.ts:49` | `clean_store_prepares_every_file` | A |
| `ts/tests/app/importing.test.ts:57` | `author_decisions_name_the_owner` | A |
| `ts/tests/app/importing.test.ts:67` | `agent_decision_is_unchanged` | A |
| `ts/tests/app/importing.test.ts:72` | `author_message_names_the_owner` | A |
| `ts/tests/app/importing.test.ts:79` | `ids_dates_codes_and_imported_from_are_kept` | A |
| `ts/tests/app/importing.test.ts:95` | `failing_store_prepares_nothing` | A |
| `ts/tests/app/importing.test.ts:106` | `store_dated_after_now_is_refused` | A |
| `ts/tests/app/importing.test.ts:113` | `stray_file_fails_the_check` | A |
| `ts/tests/app/importing.test.ts:122` | `undecodable_record_refuses_the_import` | A |
| `ts/tests/app/importing.test.ts:130` | `file_the_writer_would_not_give_back_is_refused` | A |
| `ts/tests/app/importing.test.ts:147` | `mapped_state_is_checked_with_the_project_settings` | A |
| `ts/tests/app/importing.test.ts:155` | `owner_name_used_as_a_role_fails_the_server_check` | A |
| `ts/tests/app/importing.test.ts:166` | `undecodable_name_is_refused` | A |
| `ts/tests/app/importing.test.ts:184` | `owner_named_author_changes_nothing` | A |
| `ts/tests/app/importing.test.ts:193` | `undecodable_attachment_is_preserved` | A |
| `ts/tests/app/importing.test.ts:200` | `thread_the_writer_would_not_give_back_is_refused` | Restricted the unchanged-writer comparison to decisions, bypassing threads: expected stage `lodge 0.2`, received `null`. |
| `ts/tests/app/import-store.test.ts:38` | `owner_imports_into_an_empty_project` | B |
| `ts/tests/app/import-store.test.ts:59` | `requester_must_be_the_owner` | B |
| `ts/tests/app/import-store.test.ts:68` | `project_with_two_owners_is_refused` | B |
| `ts/tests/app/import-store.test.ts:84` | `project_with_no_owner_is_refused` | B |
| `ts/tests/app/import-store.test.ts:93` | `project_with_records_is_a_conflict`, decision path | B |
| `ts/tests/app/import-store.test.ts:93` | `project_with_records_is_a_conflict`, attachment path | B |
| `ts/tests/app/import-store.test.ts:108` | `failed_check_publishes_nothing` | B |
| `ts/tests/app/import-store.test.ts:116` | `rejected_publish_is_a_conflict` | B |
| `ts/tests/app/import-store.test.ts:129` | `now_is_the_clocks` | B |
| `ts/tests/app/import-store.test.ts:140` | `project_with_separate_attachments_is_a_conflict` | Removed `current.attachments.size` from the emptiness guard: expected a rejecting promise, received a resolved promise. |

The mutation run ended with `24 pass`, `2 fail`, and `107 expect() calls`.
After reverting both mutations, the targeted suite ended with `26 pass`, `0 fail`, and `111 expect() calls`.
The existing front-door assertions are unchanged, with only their permitted additions extended as required by the task.
No Python tests were carried by this task.

## Commands and results

Commands below are relative to the repository root unless they explicitly say `cd ts`.
Read-only inspection used `cat`, `sed`, `rg`, `nl`, `wc`, and `git diff` to inspect guidance, requirements, signatures, fixtures, and changes.
An initial broad search for `AGENTS.md` encountered permission refusals in unrelated temporary directories and found no applicable repository instructions.

| Command | Result and last lines |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Exit 0: `waiting for the author`, then `nothing`, with nothing waiting for an agent either. |
| `git status --short --branch` | Initially exit 0: `## server-import-import`, with a clean worktree. |
| `cd ts && bun test tests/app/importing.test.ts tests/app/import-store.test.ts` | Initial exit 1: `0 pass`, `2 fail`, `2 errors`, and `Ran 2 tests across 2 files`. |
| Same targeted suite after implementation | Exit 1: `22 pass`, `2 fail`; the fixture path helper selected the attachment before its decision, so both affected assertions were corrected to select decision paths. |
| Same targeted suite after correcting the helper | Exit 0: `24 pass`, `0 fail`, and `104 expect() calls`. |
| `cd ts && bunx --no-install biome check --write --error-on-warnings` on the five changed TypeScript files | Exit 0: `Checked 5 files`, with the formatter and import organiser applying fixes. |
| `cd ts && bunx --no-install tsc --noEmit -p .` | Initially exit 2 for test TOML values typed as `object` and an unnarrowed parsed record; after explicit fixture annotations and narrowing, exit 0 with no output. |
| `cd ts && bunx --no-install knip` | Exit 0 with no output. |
| Targeted suite against the two mutations | Exit 1: `24 pass`, `2 fail`, and `107 expect() calls`. |
| Targeted suite after reverting the mutations | Exit 0: `26 pass`, `0 fail`, and `111 expect() calls`. |
| `cd ts && bunx --no-install depcruise src tests scripts --config .dependency-cruiser.cjs` | Exit 0: `no dependency violations found (322 modules, 1186 dependencies cruised)`. |
| `cd ts && bun test` | First full run: `1888 pass`, `1 fail`, and `6547 expect() calls`, because the structure rule requires explicit people for `writeThread`. |
| `cd ts && bunx --no-install biome check --write --error-on-warnings src/app/importing.ts` | Exit 0 after passing `original.people` explicitly to the source thread writer: `Checked 1 file`, with formatting applied. |
| `cd ts && bun test` | Exit 0: `1889 pass`, `0 fail`, `6549 expect() calls`, and `Ran 1889 tests across 171 files`. |
| `git diff --check` | Exit 0 with no output. |
| `wc -l` on the three new TypeScript modules | Implementation 172 lines, preparation tests 215 lines, and publication tests 155 lines. |
| `sh scripts/check-ts.sh` | Exit 0: Biome with `--error-on-warnings`, strict TypeScript, dependency-cruiser, knip, and the entire test suite passed; last lines were `1889 pass`, `0 fail`, `6549 expect() calls`, and `Ran 1889 tests across 171 files`. |

Biome printed 30 informational diagnostics in existing files, with no warning or error that failed the gate, and none in the new import files.
The final check is rerun after this report is written, before committing the explicit task paths and pushing the lane branch.

## Deviations and uncertainties

The coordinator ruled through `coord.ask_coordinator`: "Option A: implement Task 5 directly, test-first, no sub-agents. The skill line in the plan header is for the coordinator, not for you."
The source thread writer receives `original.people` explicitly because the structure rule requires it, while preserving the plan's default `{author}` semantics.
The source records and threads are read from the checked snapshot rather than parsed twice.
Four extra cases cover undecodable attachment text, zero owners, a non-canonical thread, and attachments supplied separately by a store's tree.
The last two extra cases used reverted mutations of already implemented guards to demonstrate failure.
The brief's authorisation to commit and push the lane supersedes the plan's sandbox restrictions.
No coordinator-only whole-project gate, other lane, historical report, frozen document, Python implementation, package manifest, or lockfile was changed.
There is no unresolved uncertainty or material concern.
