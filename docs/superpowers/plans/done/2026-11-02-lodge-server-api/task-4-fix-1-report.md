# Task 4, fix round 1 report

Resolved I-1, I-2, I-3, M-2, M-3, and M-4.
M-1 and M-5 to M-9 remain parked.

## Changes

Migration 2 now fills default settings for every existing project's event, inside the existing immediate migration transaction.
The historical migration fixture now contains both a project event and its head, and checks names, default settings, unknown-project settings, and event preservation.
Token issuance takes a write lock, refuses an existing ID with Conflict before appending an event, and serialises only the declared token fields.
An unknown passkey now raises NotFound, and its attempted event is rolled back.
The existing setup-code deletion and rebuild clearing remain unchanged, with regression tests that fail when those protections are removed.

## Test-first and mutation evidence

| Finding | Test and file:line | Failing implementation or mutation |
|---|---|---|
| I-1 | schema_2_is_migrated_to_3, ts/tests/store/database.test.ts:219; shared checkMigration at :175 | Before the migration backfill, settings returned null instead of {}; the version-1 sibling also failed. |
| I-2 | spent_newest_code_never_revives_older_codes, ts/tests/store/accounts.test.ts:186 | Removed delete-all on spending a setup code: expected false, received true for the old code; isolated run exited 1. |
| I-3 | rebuild_clears_stale_%s, ts/tests/store/accounts.test.ts:215 | Omitted each of the six table deletions separately: each corresponding case retained its stale row and exited 1. |
| M-2 | duplicate_token_id_is_a_conflict, ts/tests/store/accounts.test.ts:197 | Before the duplicate guard, issuance resolved instead of rejecting with Conflict. |
| M-3 | unknown_passkey_is_not_found, ts/tests/store/accounts.test.ts:210 | Before the explicit missing-row guard, received NoResultError instead of NotFound. |
| M-4 | no_event_holds_a_clear_secret, ts/tests/store/accounts.test.ts:122 | Before replacing token object spreading with explicit fields, the clear secrets passed on the issuing object appeared in the token event. |

The I-2 test checks both validation and spending before and after rebuild.
Each I-3 case populates all six tables through events, adds a synthetic stale row to its selected table, and compares the entire rebuilt table with the event-derived contents.
The token collision test also checks the original hash, rejected replacement hash, issue order, and unchanged event log.
The secret test passes all three synthetic clear values as additional properties of the token object through issueToken, alongside the hash.
It scans every event body for all three values.
This pins omission of extra secret fields at the store boundary; hashing the designated hash arguments remains the API's responsibility, as specified by the account port.
No account interface or dependency changed.

## Validation

The initial targeted run reported 27 pass and 5 fail, covering the two migration cases, duplicate token, unknown passkey, and clear-secret leakage.
With deletion protections removed, the account tests also failed for the spent code and all six stale-table cases.
Every mutation was restored.
The targeted tests after implementation reported 32 pass, 0 fail.
Biome formatting completed successfully.
The final gate, sh scripts/check-ts.sh, exited 0: 1329 pass, 2 existing todo, 0 fail, and 3476 expect calls.
No tests opened sockets.
No historical brief, report, or review was edited.
No unresolved concerns.
