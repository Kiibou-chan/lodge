# Task 12a report

Implemented held drafts in the port, SQLite store, and memory fake.

## Files

| File | Change |
|---|---|
| `ts/src/app/ports.ts` | Added `HeldAdd`, `HeldMessage`, `HeldDraft`, and `Held`, the three hold methods, and optional `publish` approval number. |
| `ts/src/app/index.ts` | No edit required: its existing wildcard export exposes the new port types. |
| `ts/src/store/schema.ts` | Added the unexported `HeldTable`, `Tables.held`, and migration 1 creating the table; schema version is now 2. |
| `ts/src/store/events.ts` | Added hold insertion and guarded settlement replay, and included holds in transactional rebuild. |
| `ts/src/store/sqlite-store.ts` | Added hold creation, ordered open-hold listing, transactional decline, and approval in the file publication transaction after compare-and-set. |
| `ts/tests/app/fakes.ts` | Added in-memory open holds, revision changes, isolated returned values, and settle-once approval and decline. |
| `ts/tests/store/interleaving.ts` | Forwarded all hold methods and the optional approval number through both wrappers. |
| `ts/tests/store/database.test.ts` | Updated both schema-version expectations and added migration from a raw version-1 database with an existing event. |
| `ts/tests/store/held.test.ts` | Added event, approval, decline, message, rebuild, and rollback tests. |
| `ts/tests/app/fakes-held.test.ts` | Added memory-store settlement coverage. |

## Test-first evidence

All tests below were written and run before implementation.
The first app/store run ended with 235 pass, 2 todo, and 11 fail.
The migration test was added and run separately before implementation; that run ended with 7 pass and 3 fail.

| Test | First failing output |
|---|---|
| `a_hold_is_an_event_and_not_a_file` | `TypeError: store.hold is not a function` |
| `approval_and_files_land_together` | `TypeError: store.hold is not a function` |
| `a_declined_hold_cannot_be_approved` | `TypeError: store.hold is not a function` |
| `a_hold_is_approved_once` | `TypeError: store.hold is not a function` |
| `a_settled_hold_cannot_be_declined` | `TypeError: store.hold is not a function` |
| `a_held_message_round_trips` | `TypeError: store.hold is not a function` |
| `holds_rebuild` | `TypeError: store.hold is not a function` |
| `rebuild_refuses_an_impossible_history` | `TypeError: store.hold is not a function` |
| `memory_store_settles_a_hold_once` | `TypeError: store.hold is not a function` |
| `schema_is_created_once` | Expected `user_version: 2`, received `user_version: 1`. |
| `newer_schema_is_refused` | Expected the error to end in `this lodge's 2`, received `this lodge's 1`. |
| `schema_1_is_migrated_to_2` | Expected `user_version: 2`, received `user_version: 1`. |

The migration test is in `database.test.ts` alongside the existing temporary-database lifecycle helpers rather than duplicating those helpers in `held.test.ts`.
It writes migration 0 out verbatim, sets version 1, inserts an event, and checks version 2, the new table, and event preservation.
No Python parity rows belong to this new store capability, so `parity.json` is unchanged.
No requested test is impossible in TypeScript.
The two existing TODOs remain unchanged.

## Commands and results

| Command | Result or last lines |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Nothing waiting for an agent or the author. |
| `cd ts && bun test tests/app tests/store` before implementation | `235 pass`, `2 todo`, `11 fail`; `Ran 248 tests across 30 files`. |
| `cd ts && bun test tests/store/database.test.ts` before implementation | `7 pass`, `3 fail`; `Ran 10 tests across 1 file`. |
| `cd ts && bun test tests/app tests/store` after implementation | `247 pass`, `2 todo`, `0 fail`; `Ran 249 tests across 30 files`. |
| `cd ts && bunx biome check --write` with the nine changed TypeScript files explicitly listed | `Checked 9 files in 9ms. Fixed 7 files.` |
| First `sh scripts/check-ts.sh` | Found an optional event timestamp in the new test expectation; changed the expectation to the fixed clock's exact timestamp. |
| `git diff --check` | Exit 0, no output. |
| Final `sh scripts/check-ts.sh` | Exit 0; Biome, TypeScript, dependency-cruiser, knip, and Bun tests passed; `1248 pass`, `2 todo`, `0 fail`, `3186 expect() calls`, `Ran 1250 tests across 98 files`. |

## Concerns and scope

No outstanding implementation concerns.
The task-specific instruction to commit and push takes precedence over the repeated sandbox-builder prohibition in the global constraints.
The coordinator's whole Python and TypeScript gate, merge, and ledger update remain with the coordinator.
No packages were installed, no historical briefs or reports were edited, and no Python source or tests were changed.
