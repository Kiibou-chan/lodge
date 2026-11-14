# Task 4 review: accounts and project settings in store and app

Commit 2bcf61a on 42a852a, branch server-api-c.
Verdict: no Blocking, three Important, nine Minor; fix the Important ones in one round.
The gate is green (`sh scripts/check-ts.sh` in a scratch worktree: biome, tsc, depcruise, knip, 1320 pass, 2 todo, 0 fail).

## Pass 1: correctness

Matches the plan: `MIGRATIONS[2]` adds the six tables (`ts/src/store/schema.ts:79-84`), `user_version` is 3 (`MIGRATIONS.length`), `create` writes `settings: {}` by default (`ts/src/store/projects.ts:29-45`), `settings` is null for an unknown project, `names` is sorted, the account events have `project` empty and actor `server`, and `heads` gains no row (probe: `server_events_belong_to_no_project` holds under mutation).
Mutations I ran against the tests, each one change, `bun test tests/store`:

| Mutation | Result |
|---|---|
| `<` to `<=` in `valid` (`ts/src/store/accounts.ts:75`) | caught by `setup_code_expires` |
| newest code by `asc` (`accounts.ts:70`) | caught by `newer_setup_code_replaces_older` |
| drop the `row.id !== hash` test | caught by `newer_setup_code_replaces_older` |
| `tokenFor` ignores revocation | caught by two tests |
| lists in `desc` | caught by two tests |
| `revokeToken` revokes twice | caught by three tests |
| settings dropped from the event body, or ignored in `applyEvent` | caught by three and two tests |
| `settings` reads the wrong id | caught by three tests |
| `names` without `.sort` (`projects.ts:58-61`) | SURVIVES (see M-6) |
| delete-all on spend (`ts/src/store/account-events.ts:36`) | SURVIVES (I-2) |
| the six-table clear in `rebuild` (`ts/src/store/events.ts:105-114`) | SURVIVES (I-3) |
| `lock(...)` removed in `spendSetupCode`, `revokeToken`, `setUp` | SURVIVE (M-1) |

### I-1 Important: migration 2 leaves `project_settings` empty for existing projects

`ts/src/store/schema.ts:79-84` creates the derived tables and nothing fills them, and `openDatabase` (`schema.ts:96-107`) runs no `rebuild`.
Scenario: a schema-2 file holding a project made by plan 2's code opens at 3, and `settings("storage")` answers `null`, the contract's word for an unknown project, while `names()` lists it.
Task 5's `project-create` and every settings read would then treat a real project as absent, or give it the default length and import settings.
I ran it: create `storage` with `{ length: { title_chars: 70 } }`, drop `project_settings`, set `user_version=2`, reopen: `settings` is `null`, `names` is `["storage"]`.
`ts/tests/store/database.test.ts:206-215` (`checkMigration(2)`) asserts the six tables are empty with a `project` event present, so it pins the defect.
Fix: after the migrations in the same immediate transaction, fill `project_settings` from the `project` events (or call the projection), and change the test to expect `{}` for that event.
If the author rules that no schema-2 file exists outside tests, record it as a decision and note it at `schema.ts:79`; the plan is silent.

### I-2 Important: no test pins that a spent newest code leaves the older codes dead

`account-events.ts:36` (`if (table === "setup_codes") await tx.deleteFrom(table).execute()`) is the only thing that stops this: issue `old`, issue `new`, spend `new`, and `old` is then the newest remaining row and becomes valid again.
Mutated away, all 106 store tests pass.
This is Review Focus 3, a setup code accepted after another was spent.
Fix: add to `ts/tests/store/accounts.test.ts` a test (issue `old`, issue `new`, spend `new`, then `setupCodeValid("old")` and `spendSetupCode("old")` are false), also after `rebuild`.

### I-3 Important: no test pins the new clearing in `rebuild`

`events.ts:105-114` clears the six new tables; removed, everything passes, because `accounts_survive_reopening_and_rebuild` rebuilds from a state already equal to the replay.
Fix: write a stale row straight into one account table and into `project_settings`, run `rebuild`, expect it gone (plan 2's rebuild tests do this for the older tables).

### M-1 Minor: the write-first locks cannot be pinned by the planned tests

`accounts.ts:46-51` (`lock`) is correct: an `update` that matches no row still takes the write lock (checked with two `bun:sqlite` connections: the second `begin immediate` is refused).
But `setup_code_is_spent_once` calls `Promise.all` over one connection, which Kysely serialises, so removing `lock` from the three methods leaves 12 of 12 passing.
Nothing to fix in this task; the coordinator should know the claim rests on d-thvvzx and the probe, not on a test.
`lock` also rewrites every row of the table (`set seq = seq` with no `where`); `where("id", "=", "")` would take the same lock without the writes.

### M-2 Minor: a repeated token, passkey, or session identifier overwrites silently

`account-events.ts:20-27` upserts on `id` and moves `seq`.
Probe: `issueToken(t-1, storage, h1)` then `issueToken(t-1, other, h3)` gives `tokens()` of `t-2, t-1(other)` (order of issue broken) and `tokenFor(h1)` null, so the first token silently stops working.
Token IDs are random six characters (Task 5), so a collision is rare; a `Conflict` on a duplicate ID is the cheap guard.

### M-3 Minor: `usePasskey` and the store do not refuse a counter that goes back, and an unknown ID is a raw `NoResultError`

`account-events.ts:43-47` uses `executeTakeFirstOrThrow`; `usePasskey("nope", 3)` rejects with Kysely's `NoResultError` (probe), which Task 6 would turn into an `internal` 500 instead of `unauthorised`.
The counter check belongs to Task 6 (plan line 437), so this only needs a `NotFound` for an unknown ID.

### M-4 Minor: `no_event_holds_a_clear_secret` cannot fail

`accounts.test.ts:122-137` hashes the secrets itself and hands the store only hashes, so no implementation of the store could leak them.
The plan names the test, so keep it, but it asserts nothing about `SqliteAccounts`; the real guarantee is the API's (Task 5's `issued_token_is_stored_as_its_hash`).

## Pass 2: practice

Clean: no dependency, `package.json`, `knip.json`, or structure file changed; modules all at most 254 lines; no personal path or real record in code, tests, or report; fixtures synthetic; time through `Clock`; no socket, no git in tests; British English and one sentence per line in the report.

### M-5 Minor: small duplication and style in the new store files

`account-events.ts:4` redefines `json`, which `events.ts` already exports and `accounts.ts:12` imports; the `import type` of `Tables` sits after the `const` (`account-events.ts:6`); `projects.ts:56` uses `new TextDecoder().decode` where `decodeUtf8` of `#core` is used everywhere else in the diff, and returns `JSON.parse`'s untyped result.
Fix: import `json` and `decodeUtf8`, put imports first.

### M-6 Minor: `names` ordering is covered by index order, not by the code

`projects.ts:58-61` sorts, but removing the sort passes all tests, since SQLite reads `heads` through its text primary key's index.
The test creates `aaa` after `storage` and so would catch a rowid scan; fine for ASCII names (d-wx7d0f), but an `order by project` would say what is meant.

### M-7 Minor: the report's test-first table shows one cause for 12 tests

`task-4-report.md` gives "Missing SqliteAccounts export" as the first failure of all twelve account tests, so it shows no test failing for its own reason; the only mutation it names is `projects.test.ts:12`.
The survivors in I-2, I-3, and M-1 are what that leaves open.

### M-8 Minor: an untracked file sits in the lane

`docs/superpowers/plans/2026-11-02-lodge-server-api/task-4-codex-final.txt` (the builder's last message) is untracked; do not stage it with the review.

## Pass 3: design

Names match the plan's Task 4 and its consumers (Tasks 5, 6, 8): `Accounts`, `AgentToken`, `Passkey`, `ServerSetup` through `#app` as types only (`app/index.ts:1`), `SqliteAccounts(database, clock)` through `#store`, and the three `Projects` additions with the planned signatures; `front-door.test.ts` allows exactly those four.
`rebuild` replays the account kinds through `applyEvent` as the plan says, and `app` stays pure (`app/accounts.ts` holds interfaces only).

### M-9 Minor: `tokenFor` scans every token and parses each body on every agent request

`accounts.ts:113-117` lists all token rows, revoked ones included, and compares `hash` in memory, since the derived table keeps only `id`, `body`, and `seq`.
For one person's server this is small, but it is the bearer path of every request in Task 5; a `hash` column with an index in `MIGRATIONS[2]` (before it ships) is cheaper than a later migration.
The same layout applies to `sessions` and `setup_codes`, keyed by hash already, which are fine.

## Files

Read: `CLAUDE.md`; the plan's header, Global Constraints, Exports, Order and lanes, Names consumed, and Task 4; the brief and report; the whole `git diff 42a852a 2bcf61a` (source and tests); `ts/src/store/schema.ts` and `ts/src/store/projects.ts` in full.
Ran: the gate, the mutations above, and probes for two connections, the migration, duplicates, and an unknown passkey, all in a scratch worktree, now removed.
Not read: plan 2's own tests beyond those the diff touches, `ts/tests/structure/` rules (run, not read), Tasks 5 to 9 beyond the lines naming Task 4's API.
