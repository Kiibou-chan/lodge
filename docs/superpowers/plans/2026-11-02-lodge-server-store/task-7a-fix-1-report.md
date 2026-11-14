# Task 7a fix round 1 report

Implemented I-1 and I-2, plus m-1, m-3, m-5, m-6, m-7, and m-9.

## Changes

- `ts/src/store/schema.ts`: migration 1 now refuses an insert whose explicit sequence already exists, including both SQLite REPLACE forms, with `events are append-only`.
- `ts/tests/store/database.test.ts`: both REPLACE forms must reject and preserve the actor; stale rows in all three derived tables must disappear; a second member event changes the role; an unknown event rejects rebuild and preserves all three tables row for row.
- `ts/tests/core/fileformat.test.ts`: the undecodable-byte hash test decodes its raw bytes before hashing, matching Python.
- `ts/tests/core/bytes.test.ts`: leading U+FEFF decoding and byte round trip are covered.
- `ts/src/core/text.ts`: masks and minimum code points are indexed by sequence size instead of repeating ternary chains.
- `ts/tests/structure/imports.test.ts`: parametrised confinement rows supply their expected findings directly.

## First failures

Every mutation was restored immediately after its run.
The new REPLACE tests ran before the trigger was added.

| Test or group | Original code or targeted mutation | Observed failure |
|---|---|---|
| `events_refuse_insert or replace`, `events_refuse_replace` | Original migration | Both promises resolved instead of rejecting; 7 pass, 2 fail |
| `rebuild_removes_stale_rows` | Remove only the heads delete | Stale head remains; 2 pass, 1 fail |
| `rebuild_removes_stale_rows` | Remove only the files delete | Stale file remains; 2 pass, 1 fail |
| `rebuild_removes_stale_rows` | Remove only the members delete | Stale member remains; 2 pass, 1 fail |
| `rebuild_derives_the_tables_from_raw_events` | Member conflict uses `doNothing()` | Role remains owner instead of member; 2 pass, 1 fail |
| `unknown_event_rolls_back_rebuild` | Unknown-kind throw becomes return | Rebuild resolves instead of rejecting; 2 pass, 1 fail |
| BOM decode and round trip | Drop the first three bytes when the leading byte is 239 | Both BOM cases fail; 0 pass, 2 fail |
| `hash_covers_undecodable_bytes` | Hash with TextEncoder instead of encodeUtf8 | Expected 01ce0241d2a0, received 05087813392e; 0 pass, 1 fail |

## Validation

- `uv run --frozen --quiet lodge waiting`: nothing waiting for an agent or the author.
- `bun test tests/store tests/core/bytes.test.ts tests/core/fileformat.test.ts`: 74 pass, 0 fail.
- Biome formatting of changed TypeScript files completed successfully.
- First `sh scripts/check-ts.sh`: 978 pass, 1 fail because the added import took fileformat.test.ts to 301 lines.
  Removed a blank line to retain the 300-line limit.
- `uv run --frozen --quiet python` confirmed Python content_hash of the escaped text is `01ce0241d2a0`.
- `git diff --check`: clean.
- Final `sh scripts/check-ts.sh`: exit 0, 979 pass, 0 fail; Biome, TypeScript, dependency-cruiser, and knip all green.

## Deferred minors and ledger note

m-2 is deferred: a reliable first-open contention regression needs a separate process and synchronisation, beyond the cheap local fixes in this round.
The existing journal-mode and timeout order is unchanged, so the review's contention concern remains.

m-4 is deferred: changing codec fast paths merits the review's extensive Python comparison and performance measurement rather than a small unmeasured optimisation.
The codec retains its existing performance characteristics.

m-8 is deferred to Task 7b or plan 3, as the review requests, because this task implements neither publish nor API input validation.
Those tasks should refuse text for which `decodeUtf8(encodeUtf8(text)) !== text` before writing.

m-9 ledger note for the coordinator: Task 7a's plan Files list omitted the contentHash expectation edit in plan 1's `hash_covers_undecodable_bytes` test.
That edit is justified: Python gives `01ce0241d2a0`, matching the raw bytes, and plan 1's previously unrepresentable expectation now holds.
No earlier brief, report, or review was edited, and the coordinator retains ownership of the ledger.
No test cannot hold in TypeScript in this round.
