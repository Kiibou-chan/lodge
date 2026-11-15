# Task 7a report

Implemented the surrogateescape codec, SQLite schema, append-only events, derived-table replay, and store import rules.

## Changes by file

| File | Change |
|---|---|
| `ts/src/core/text.ts` | Added `encodeUtf8` and `decodeUtf8`, preserving escaped bytes, rejecting other lone surrogates with `ValueError` and `pyRepr`, and validating UTF-8 sequence boundaries. |
| `ts/src/core/fileformat.ts` | Hashes normalised text through `encodeUtf8`. |
| `ts/src/store/schema.ts` | Added table types, the Bun SQLite adapter, WAL and busy timeout, transactional versioned migration, append-only triggers, newer-schema refusal, and asynchronous close. |
| `ts/src/store/events.ts` | Added JSON byte encoding, event append and application, project/member/file projection, unknown-kind refusal, and transactional rebuild in sequence order. |
| `ts/src/store/index.ts` | Exposes `LodgeDatabase`, `Tables`, `openDatabase`, and `rebuild`. |
| `ts/package.json` | Added the `#store` front door, with no dependency changes. |
| `ts/knip.json` | Removed the Kysely ignore and added the events module as an entry until Task 7b reads its exports. |
| `ts/.dependency-cruiser.cjs` | Added `store-imports` for built-ins and external dependencies, allowing Kysely and `bun:sqlite`. |
| `ts/tests/structure/table.ts` | Added `STORE_NPM`. |
| `ts/tests/structure/table.test.ts` | Checks the exact store dependency list. |
| `ts/tests/structure/imports.test.ts` | Tests denied and allowed store imports, and updates the existing store filesystem expectation to include the new finding. |
| `ts/tests/core/bytes.test.ts` | Tests all ten probe sequences, inverse encoding, rejected surrogates, and the specified hash. |
| `ts/tests/core/fileformat.test.ts` | Corrected the existing undecodable-byte hash expectation to hash the original byte instead of U+FFFD. |
| `ts/tests/store/database.test.ts` | Tests reopen/version preservation, newer-schema refusal, append-only events, repeatable projections, and no head for a projectless event. |
| This report | Records implementation, failure evidence, commands, and concerns. |

## Test-first evidence

The initial focused run happened before the implementation.
Missing exports or modules prevented the byte and database suites from loading, as permitted by the brief.
All mutations below were reverted.

| Test or named group | First failure or targeted mutation |
|---|---|
| `decode_utf8_like_surrogateescape`, all ten cases | `SyntaxError: Export named 'encodeUtf8' not found` when loading the new byte suite. |
| `encode_utf8_reverses_decode`, all ten cases | Same missing codec export. |
| `encode_refuses_a_lone_surrogate_outside_the_escapes`, both cases | Same missing codec export; also asserts that hashing rejects both lone surrogates. |
| `content_hash_encodes_escaped_bytes` | Same missing codec export. |
| `schema_is_created_once` | `Cannot find package '#store'`. |
| `newer_schema_is_refused` | Same missing store module. |
| `events_are_append_only` | Same missing store module. |
| `rebuild_derives_the_tables_from_raw_events` | Same missing store module; final test rebuilds twice and checks events remain unchanged. |
| `an_event_of_no_project_adds_no_head` | Same missing store module. |
| `store_npm_matches_ruling` | `SyntaxError: Export named 'STORE_NPM' not found`. |
| `store_importing_another_package` | Expected the YAML `store-imports` finding, received `[]`. |
| `store_importing_node_builtin` | Expected both findings, received only `file-confinement`. |
| `store_imports_its_own` | Mutation replaced both allow-list alternatives with non-matching names; expected `[]`, received findings for Kysely and `bun:sqlite`. |
| Existing `fs_outside_git_and_cli`, store case | Mutation removed `store-imports`; expected both findings, received only `file-confinement`. |
| Existing `hash_covers_undecodable_bytes` | After correcting the assertion, restoring the old TextEncoder hash produced `05087813392e`, while the byte-based assertion expected `01ce0241d2a0`. |

## Commands and results

| Command | Result or last lines |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Nothing waiting for an agent or the author. |
| `cd ts && bun test tests/store tests/core/bytes.test.ts tests/structure/imports.test.ts tests/structure/table.test.ts`, before implementation | `25 pass`, `5 fail`, `3 errors`; missing codec/store/table exports and absent import findings. |
| Same focused command, after implementation | `57 pass`, `0 fail`, `74 expect() calls`. |
| `cd ts && bun test tests/structure/imports.test.ts -t store_imports_its_own`, against the allow-list mutation | `0 pass`, `1 fail`, `26 filtered out`. |
| `cd ts && bun test tests/core/fileformat.test.ts -t hash_covers_undecodable_bytes`, against the old encoder | `0 pass`, `1 fail`, `39 filtered out`. |
| `cd ts && bun test tests/structure/imports.test.ts -t fs_outside_git_and_cli`, without the new rule | `1 pass`, `1 fail`, `25 filtered out`. |
| `cd ts && bunx biome check --write .` | Formatted the implementation and tests. |
| `cd ts && bunx tsc --noEmit -p .` | Initially found a readonly tuple assertion mismatch; fixed by copying expected code points into an array. |
| Targeted Biome format/check commands | Fixed formatting after assertion edits. |
| Intermediate `sh scripts/check-ts.sh` runs | Exposed the readonly assertion, formatting, obsolete hash expectation, and the 300-line limit; all corrected. |
| Final `sh scripts/check-ts.sh` | Exit 0; Biome clean, TypeScript clean, no dependency violations, knip clean, `973 pass`, `0 fail`, `2376 expect() calls`. |

Read-only inspection used `cat`, `rg`, `sed`, and Git status/diff commands.
No dependency installation, Python source changes, whole Python gate, coordinator merge, or ledger edit was performed.

## Parity and concerns

No new Python parity rows belong to Task 7a, so `ts/tests/parity.json` is unchanged.
The existing fileformat row remains ported by plan 1, Task 5a.
No requested test is impossible in TypeScript.

The existing `hash_covers_undecodable_bytes` expected replacement encoding, which cannot coexist with the explicitly required surrogateescape hash.
I treated the brief's specific codec and hash requirements as authority to correct that expectation, despite the general restriction on editing existing tests.
The existing store filesystem test likewise needs the additional finding required by the new rule.
These are the only existing test expectation changes.

The brief's opening instruction explicitly requires committing and pushing this branch, whereas its repeated global constraints describe an older builder sandbox that forbids both.
I followed the task-specific opening instruction.
The unrelated, pre-existing untracked `task-7a-codex.log` is excluded from the commit.
