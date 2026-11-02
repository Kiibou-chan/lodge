# Plan recheck 5: plan 3, the API, sign-in, and the command

Rechecked: fix round 5, `git diff 9ac93ac 9a25b93` on `server-api`, against the seven mismatches of `preflight.md` and "Round 5: preflight" of `plan-fix-4.md`.
"Plan line N" is a line of `docs/superpowers/plans/2026-11-02-lodge-server-api.md` at `9a25b93`; "plan 2 line N" a line of `docs/superpowers/plans/2026-11-02-lodge-server-store.md` at `0244e79` of `origin/server-store`; Python handles are read in this tree, whose `src/lodge` is unchanged since `bf22731`.

## M-1 · Resolved

Plan line 352 and Task 4's Files: the migration is `MIGRATIONS[2]`, raising `user_version` from 2 to 3, and `ts/tests/store/database.test.ts` joins Task 4's Modify list.
The stated changes agree with plan 2's text:
- plan 2 has two migrations, `MIGRATIONS[0]` (plan 2 line 387) and `MIGRATIONS[1]` (line 589, "`user_version` becomes 2"), so the next is `[2]` and the version 3;
- plan 2's `schema_is_created_once` expects 2 after Task 12a (plan 2 line 601), and plan 3 now expects 3;
- plan 2's `schema_1_is_migrated_to_2` builds a version-1 file from migration 0's statements written out "since `MIGRATIONS` is not exported" and opens it at 2 with `held` and its event kept (plan 2 line 599); plan 3 keeps its file and name and expects 3 with `held` and the six account tables;
- the new sibling `schema_2_is_migrated_to_3` writes out migrations 0 and 1 by the same route, which plan 2 line 388 (`MIGRATIONS` declared without `export`) makes the only one.
The kept name `schema_1_is_migrated_to_2` now describes a migration to 3; that is plan 2's test name, not a carried Python name, so it costs nothing beyond a misleading title, and no finding is raised.

## M-2 · Resolved

Task 3's Files now read "Create or modify: `ts/src/cli/index.ts` and `ts/package.json`'s `imports` (`#cli`)", with the second lane to merge keeping both sides, and `ts/knip.json` stays under Modify.

## M-3 · Resolved

Plan line 286: `server_is_needed` (a `ProjectSettings` with `server: null`: `serverOf` throws a `CliError` whose message is `NO_SERVER` and whose exit code is 2).

## M-4 · Resolved

Plan line 114 cites `0244e79` and names the later changes (Task 12c of `a035344`, the coordinator's R3-1 ruling); the ledger gains the alignment line.
`origin/server-store` is at `0244e79` today (`git log -1 origin/server-store`).

## M-5 · Resolved

Plan line 445: an entry's draft is `{name, kind, title, statement}` and an area's `{name, kind, title, intro}`, read from the `SpecEntry` and `Area` that `recordFromDraft` gives; a problem draft keeps the raw `text`.
Plan line 460 pins the values, and they match the drafts `seed` writes: `Transcripts are kept` and `Held.` from `entry_text` (`tests/e2e/support.py:24-25`), `Storage` and `How data is kept.` from `area_text` (`:28-30`).
Task 9's page (plan line 612) shows an area's `intro`.

## M-6 · Resolved

Plan line 395 (`project-create`): a key of `settings` other than `length` and `import` is `usage` with `settings: unknown section [<name>]` for a table and `settings: unknown key <name>` otherwise.
Those are lodge 0.2's words: `src/lodge/core/settings.py:30-35` raises `unknown section [{name}]` for a mapping and `unknown key {name}` otherwise, and the `settings: ` prefix is the one the existing `parseCoreSettings` refusal already carries.
`project_create_checks_the_settings` (plan line 405) gains `{"store": {"mode": "tree"}}`: `usage`, `settings: unknown section [store]`, and no project created.
The command never sends such a key, since Task 3's `core` holds only `length` and `import`.

## M-7 · Resolved (spot-checked)

Six of the ten corrected handles, read with `sed -n` here:
- `src/lodge/cli/parser.py:153`: `if not text.isdecimal() or int(text) < 1:`;
- `src/lodge/main.py:29-30`: `def now(…)` returning `datetime.now().astimezone()`, and `:38`: `return secrets.token_bytes(8)`;
- `src/lodge/core/apply.py:137`: `area = existing.area`;
- `src/lodge/cli/commands.py:71-73`: the `Add` case reading drafts and attachments before `_add`;
- `src/lodge/cli/threads.py:104-106`: the `CHECK_FAILED` branch printing the check lines and returning 1;
- `src/lodge/cli/threads.py:71-82`: `def _message_command` and its `--by author` rule.
`commands.py:104-105` (the exit 1 on `CHECK_FAILED`) and `:115-122` (`_read_drafts` and `_read_attachments` by base name) also hold.
No old handle survives in the plan (`grep` of the ten patterns at `9a25b93` finds only the new ones), and `probes.md` item 8 now names d-j28rp0 (no d-pmaw3a left in the plan or `probes.md`).

## New findings

None.
The diff changes only the lines above, one ledger line, `plan-fix-4.md`, `probes.md` item 8, and adds `preflight.md`; no name, type, or lane wait changes elsewhere.
Recheck 4's N-8 is also answered in passing: `agents_relay_is_held` (plan line 405) now first adds `seed`'s three drafts through the token, so its `ask` has a record.
The preflight's notes N-1 to N-5 and preconditions P-1 and P-2 stay for the briefs and the coordinator, as `plan-fix-4.md` says; P-1 (d-d0vca9 not yet in `calls.ts` at `7d5ecbc`) still blocks Task 8's gate until plan 1's fix wave merges.

## Counts

Resolved: 7 of 7 (M-1 to M-7).
Not resolved: 0.
New: 0 Blocking, 0 Important, 0 Minor.
