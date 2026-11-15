# Task 4, recheck of fix round 1

Fix diff `git diff 181bcc1 69cf210`, probed in a detached scratch worktree at 69cf210 (removed).
Each mutation was run with `bun test tests/store` and restored.

| Finding | Resolved | Handle | Mutation result |
|---|---|---|---|
| I-1 | yes | `ts/src/store/schema.ts:84-86` backfills `{}` per project; `ts/tests/store/database.test.ts:175-215` has a project and head before the migration, checks `names()`, `settings()`, and unknown | backfill deleted: `schema_2_is_migrated_to_3` and `schema_1_is_migrated_to_2` fail |
| I-2 | yes (test only, source unchanged) | `ts/tests/store/accounts.test.ts:186` (`spent_newest_code_never_revives_older_codes`, before and after rebuild) | delete-all at `account-events.ts:~40` removed: that test fails (114 pass, 1 fail) |
| I-3 | yes (test only) | `ts/tests/store/accounts.test.ts:215` (`rebuild_clears_stale_%s`, six cases) | each of the six names removed from the clear in `events.ts:105-114` separately: exactly the matching case fails each time |
| M-2 | yes | `ts/src/store/accounts.ts:106-113` throws `Conflict` under the tokens lock; test `accounts.test.ts:197` also checks hashes, order, and the event log unchanged | guard removed: `duplicate_token_id_is_a_conflict` fails |
| M-3 | yes | `ts/src/store/account-events.ts:44-46` throws `NotFound`; test `accounts.test.ts:210` checks no event remains | guard replaced by a plain Error: `unknown_passkey_is_not_found` fails |
| M-4 | yes | `accounts.ts:107` picks explicit fields; test `accounts.test.ts:122-142` hands clear secrets in the issuing object | `{ ...token, hash }` restored: `no_event_holds_a_clear_secret` fails |

## New findings

None Blocking, none Important.

Minor (no action needed): the M-4 test pins omission of extra fields at the store boundary only; hashing is the API's duty, as the report says.
Minor: the migration backfills `{}` where a rebuild would read `settings` from the event body; identical for plan 2 projects, which carry none (`events.ts:48-50`).

## Hygiene

`sh`-equivalent gate `bun --bun run check` in `ts/`: 1329 pass, 0 fail.
Largest store file is 145 lines, well under 300.
`#app` import in `account-events.ts` passed the structure tests.
No `*-codex-final.txt` in the diff; fixtures are synthetic.
