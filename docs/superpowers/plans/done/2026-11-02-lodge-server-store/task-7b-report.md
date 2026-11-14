# Task 7b report

Implemented the SQLite store and projects on `server-store-b`.

## Files

| File | Change |
|---|---|
| `ts/src/store/sqlite-store.ts` | Implements the asynchronous Store port, transactional reads, compare-and-set publication, preflight refusals, exact UTF-8 bytes, attachment reads, and the server's gate, freshness, and commit answers. |
| `ts/src/store/projects.ts` | Validates names, creates projects with write-first transactions, lists members in code-point order, rejects duplicate members and names used as roles, and supplies stores with the actor's text. |
| `ts/src/store/read-tree.ts` | Shares the transactional project read, revision, decoded record files, and undecoded attachment paths. |
| `ts/src/store/index.ts` | Exports SqliteStore and SqliteProjects through the front door. |
| `ts/knip.json` | Removes events.ts from temporary entry points because production modules now consume its exports. |
| `ts/tests/store/support.ts` | Supplies isolated in-memory projects, ordered event reads, and database cleanup. |
| `ts/tests/store/projects.test.ts` | Covers creation, members, names, missing projects, separate database connections, and roles used in decisions and threads. |
| `ts/tests/store/sqlite-store.test.ts` | Covers state identity, ordered events, exact bytes, stale bases, attachment reads, passive methods, and Lodge.add with an entry and attachment. |
| `ts/tests/store/sqlite-store-refusals.test.ts` | Covers invalid paths, lone surrogates, immutable attachments, and immutable decision rendering, including an unchanged decision being accepted. |
| `ts/tests/store/rebuild.test.ts` | Covers replay equivalence for every existing derived table and preservation of all events. |

No schema, event replay implementation, existing test, Python source, or historical document required a change.
The parity table has no Python rows assigned to this new SQLite task, so it remains unchanged.
Its existing plan 1 task 7b rows belong to confirmation and ordering.

## Test-first evidence

All four new test files were written before the three implementation modules and front-door exports.
The first `cd ts && bun test tests/store` run reported `9 pass`, `4 fail`, and `4 errors`, with `Ran 13 tests across 5 files. [116.00ms]`.
Each new file failed to load with `SyntaxError: Export named 'SqliteProjects' not found in module '/var/tmp/lodge-store-b/ts/src/store/index.ts'.`.
This is the missing-export failure allowed by the brief; no targeted mutation was needed because none of these tests carries an earlier implementation.

| New test title | First failing output |
|---|---|
| create_writes_the_project_and_its_owner | Missing SqliteProjects export, projects.test.ts |
| existing_project_conflicts | Missing SqliteProjects export, projects.test.ts |
| names_are_checked, all five cases | Missing SqliteProjects export, projects.test.ts |
| add_member_needs_a_new_name | Missing SqliteProjects export, projects.test.ts |
| unknown_project_is_not_found | Missing SqliteProjects export, projects.test.ts |
| a_second_create_conflicts_across_connections | Missing SqliteProjects export, projects.test.ts |
| a_name_used_as_a_role_cannot_join | Missing SqliteProjects export, projects.test.ts |
| trees_give_one_state | Missing SqliteProjects export, sqlite-store.test.ts |
| a_write_is_one_event_per_file | Missing SqliteProjects export, sqlite-store.test.ts |
| file_bytes_survive_exactly | Missing SqliteProjects export, sqlite-store.test.ts |
| stale_base_is_rejected_and_writes_nothing | Missing SqliteProjects export, sqlite-store.test.ts |
| attachments_are_listed_not_read | Missing SqliteProjects export, sqlite-store.test.ts |
| gate_compares_the_current_state_with_itself | Missing SqliteProjects export, sqlite-store.test.ts |
| freshness_is_null_and_commit_is_refused | Missing SqliteProjects export, sqlite-store.test.ts |
| lodge_adds_through_the_store | Missing SqliteProjects export, sqlite-store.test.ts |
| lone_surrogate_outside_the_escapes_is_refused | Missing SqliteProjects export, sqlite-store-refusals.test.ts |
| path_outside_lodge_is_refused, all eight cases | Missing SqliteProjects export, sqlite-store-refusals.test.ts |
| a_path_holding_a_surrogate_is_refused, both lone surrogates and an accepted astral character | Missing SqliteProjects export, sqlite-store-refusals.test.ts |
| an_attachment_is_never_overwritten | Missing SqliteProjects export, sqlite-store-refusals.test.ts |
| a_published_decision_is_never_rewritten | Missing SqliteProjects export, sqlite-store-refusals.test.ts |
| rebuild_gives_the_same_tables | Missing SqliteProjects export, rebuild.test.ts |
| rebuild_keeps_every_event | Missing SqliteProjects export, rebuild.test.ts |

All requested tests hold in TypeScript.
There are no skipped tests or TypeScript exceptions to report.

## Commands and results

| Command | Result or last output |
|---|---|
| `cat`, `rg`, `sed`, `ls`, and `wc -l` inspections of the brief, CLAUDE.md, ports, model, fixtures, schema, and configuration | Confirmed the existing interfaces, dependencies, and modules below 300 lines. |
| `uv run --frozen --quiet lodge waiting` | `nothing`, for both agents and the author. |
| `cd ts && bun test tests/store`, before implementation | `Ran 13 tests across 5 files. [116.00ms]`, with four missing-export failures. |
| `cd ts && bun test tests/store`, after implementation | `Ran 44 tests across 5 files. [211.00ms]`, 44 pass, zero fail. |
| `cd ts && bunx biome check --write src/store tests/store knip.json` | Fixed formatting and imports; identified one non-null assertion warning, subsequently removed. |
| `sh scripts/check-ts.sh`, initial attempts | First identified the assertion warning, then the empty event array's implicit type; both corrected. |
| `sh scripts/check-ts.sh`, after corrections | 1,040 pass, zero fail, 2,560 assertions, with Biome, TypeScript, dependency-cruiser, and knip passing. |
| Exploratory store run with trailing-newline name and revision cases | 46 pass, zero fail; these temporary cases were removed to retain the requested test-first suite. |
| `cd ts && bunx biome check --write tests/store/sqlite-store-refusals.test.ts` | `Checked 1 file in 5ms. No fixes applied.` |
| `git diff --check` | No output, successful. |

The final validation command is `sh scripts/check-ts.sh`, repeated after the report and final test refinement.
The decision immutability fixture uses a valid rendered decision and changes only its trailing whitespace.
No packages were installed or added.
No network or real repository was used by tests.
The whole Python gate and coordinator merge remain the coordinator's work.

## Concerns and interpretation

No outstanding implementation concerns.
The brief's opening instruction explicitly authorises committing and pushing this task, superseding the generic builder restriction repeated in its Global Constraints.
Only explicit task paths are staged; the pre-existing untracked task log is left alone.
