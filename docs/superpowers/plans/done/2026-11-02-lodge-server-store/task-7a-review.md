# Task 7a review

Reviewed: `server-store-b` at f194667 against `server-store` (`git diff server-store..server-store-b`), from the plan's Task 7a, Global Constraints (with "Bytes"), Review Focus 2 and 4, and the events-table bullets of "Interfaces for plans 3 and 4".
Probes ran in a detached worktree of f194667 under `.claude/worktrees/review-7a`, removed afterwards.

## Ruling on the edited hash test

The edit of `hash_covers_undecodable_bytes` (`ts/tests/core/fileformat.test.ts:217-221`) is justified, and it brings the test back to its Python original rather than away from it.
lodge 0.2's `content_hash` encodes with `errors="surrogateescape"` (`src/lodge/core/fileformat.py:95`), and the Python test asserts the hash of the raw bytes `b"a\xffb"` (`tests/core/test_fileformat.py:216-219`).
Run against lodge 0.2 (`uv run --frozen --quiet python`): `content_hash("a\udcffb")` is `01ce0241d2a0`, equal to `sha256(b"a\xffb")[:12]`; the old TypeScript expectation, the hash of `"a�b"`, is `05087813392e`, which Python never gives.
The commit's TypeScript gives `01ce0241d2a0` for the same text and `518254327818` for probe 7's `"a\udc80\n"`, as Python does.
The old expectation was plan 1's "test that cannot hold" (`docs/superpowers/plans/done/2026-11-02-lodge-server-core/task-5a-report.md:137-138`), kept only because `TextEncoder` replaces a lone surrogate; Task 7a's `contentHash` through `encodeUtf8` is exactly what that report said would let it hold (`task-5a-review.md:48` of the same folder).
The plan's Global Constraints say an existing test is "edited only where a task says so", and Task 7a's Files list omits `fileformat.test.ts`; that is a gap in the plan, not a fault of the build, since the required `contentHash` cannot pass the old assertion (Codex's mutation row: the old encoder gives `05087813392e` against the expected `01ce0241d2a0`).
One Minor on the edited test follows (m-1).

## Correctness

Verified by running, in the scratch worktree:

- Codec against Python: 527,936 byte strings (200,000 random ones of length 0 to 7 biased to boundary bytes, every 1- and 2-byte string, and every 3-byte string with a third byte of 0x80, 0xBF, 0x41, or 0xC2) decoded by `bytes.decode("utf-8", "surrogateescape")` under lodge 0.2's Python and by `decodeUtf8`: 0 code-point mismatches, and `encodeUtf8(decodeUtf8(b))` gave `b` back in all 527,936.
- Review Focus 2's text `"﻿a\r\nb\u0000c\u{1F600}d\uDC80e\uDCFF"` encodes to `efbbbf610d0a620063f09f9880648065ff` (U+FEFF kept as `efbbbf`, CRLF kept, NUL kept, the astral character as four bytes, the escapes as 0x80 and 0xFF) and decodes back equal.
- U+D83D, U+DC7F, and U+DD00 each throw `ValueError` from `encodeUtf8` and from `contentHash`, as Python raises `UnicodeEncodeError` for all three.
- `openDatabase` on a file: `journal_mode` `wal`, `busy_timeout` 5000, `user_version` 1; on `":memory:"` `journal_mode` is `memory`, which SQLite forces.
- A `rebuild` that meets an unknown kind throws `unknown event kind: mystery` and leaves `files` as it was, so the transaction rolls back.
- `update`, `delete`, and `insert … on conflict(seq) do update` on `events` are refused with `events are append-only`.

### I-1 (Important): `insert or replace` rewrites an event past both triggers

`ts/src/store/schema.ts:44-47` creates only `before update` and `before delete` triggers, and SQLite fires delete triggers for a row that REPLACE removes only when `recursive_triggers` is on, which it is not (`pragma recursive_triggers` gives 0 on a database from `openDatabase`).
Run on a file database from `openDatabase` holding events 1 and 2: `insert or replace into events(seq, …) values (2, …, 'eve', …)` and `replace into events(seq, …) values (1, …)` are both ALLOWED, and afterwards both events carry the actor `eve` and the new bodies; Kysely offers the same statement as `insertInto("events").orReplace()`.
Failure scenario: a later task writing an event with an explicit `seq` (a rebuild tool, an import that keeps `seq`, or `orReplace()` used as an idempotent insert) silently rewrites history, and `rebuild` then derives the tables from the rewritten events, which Review Focus 4 and the Interfaces bullet "nothing ever updates or deletes an event" forbid.
Cost now against later: `MIGRATIONS[0]` can still change while no database exists; after the first deployment the fix needs a second migration.
Fix: add to `MIGRATIONS[0]` `create trigger events_no_replace before insert on events when exists (select 1 from events where seq = new.seq) begin select raise(abort, 'events are append-only'); end;`, which I ran: it refuses both REPLACE forms and still allows an insert without `seq` and one with a new `seq`; add both REPLACE forms to `events_are_append_only` (`ts/tests/store/database.test.ts:58-68`).
`pragma recursive_triggers = on` in `openDatabase` also refuses both (run), but holds only on connections lodge opens, so the trigger is the sturdier fix.
The plan's Interfaces bullet names two triggers (probe 3), so this adds to the plan rather than conflicting with it; if the coordinator reads it as a change of d-wje1cn's schema, it is a `lodge add` of scope `process`.

### I-2 (Important): no test sees `rebuild` keep a row that no event gives

`rebuild` deletes `heads`, `files`, and `members` before it replays (`ts/src/store/events.ts:71-73`), which is right, but no test fails without those deletes.
Run: with all three `deleteFrom` lines removed, `bun test tests/store` gives 5 pass, 0 fail; `rebuild_derives_the_tables_from_raw_events` (`ts/tests/store/database.test.ts:70-101`) starts from empty derived tables, and its second `rebuild` replays upserts that give the same rows with or without the deletes.
Plan 7b's `rebuild_gives_the_same_tables` compares live tables with rebuilt ones, which agree in that mutation too, so no planned test closes the gap.
Failure scenario: a later edit drops or narrows a delete (for example when Task 12a adds `held` to `rebuild`'s list), and a derived row that a bug wrote, or that a since-removed event kind left, survives every `rebuild`, so `rebuild` no longer repairs the derived tables, which is Review Focus 4's "a derived table that `rebuild` does not give back row for row".
Fix: in `database.test.ts`, insert a `heads`, a `files`, and a `members` row for a project no event names, run `rebuild`, and expect all three tables empty; I ran that test: it passes on f194667 and fails with only `deleteFrom("files")` removed.

### m-1 (Minor): the edited hash test spells the decoded text instead of decoding the bytes

`ts/tests/core/fileformat.test.ts:217-221` hashes the literal `"a\udcffb"`, while Python decodes `b"a\xffb"` with `surrogateescape` first (`tests/core/test_fileformat.py:217-219`).
The assertion is as strong, but the test no longer shows where the text comes from, and a change to `decodeUtf8` that mapped 0xFF elsewhere would not reach it.
Fix: `const raw = new Uint8Array([97, 255, 98]); expect(contentHash(decodeUtf8(raw))).toBe(createHash("sha256").update(raw).digest("hex").slice(0, 12));`.

### m-2 (Minor): a contended first open leaves the connection out of WAL, silently

`ts/src/store/schema.ts:58` runs `PRAGMA journal_mode=WAL` before `PRAGMA busy_timeout=5000`, and SQLite answers a contended `journal_mode` change with the old mode rather than an error.
Run: another process holds a read transaction on a fresh file for 800 ms; `openDatabase` on it after 200 ms succeeds after about 640 ms with `pragma journal_mode` `delete`, not `wal`; with the two pragmas swapped, the same run gives `wal`.
Failure scenario: two processes starting on a new database file (or one opening while a `sqlite3` shell reads it) leave one connection in rollback-journal mode, where readers and the writer block each other, so Task 8's two writers and probe 4's behaviour do not hold on that connection.
Fix: set `busy_timeout` first, then read the answer of `PRAGMA journal_mode=WAL` and refuse with `LodgeError` unless it is `wal`, or `memory` for `":memory:"`.

### m-3 (Minor): no core test of a leading U+FEFF

`ts/tests/core/bytes.test.ts:4-15` holds probe 7's and probe 11's byte strings, none starting with `efbbbf`, though U+FEFF first is Review Focus 2's first case and the default `TextDecoder` drops it.
The codec keeps it (run above), and plan 7b's `file_bytes_survive_exactly` will cover it through the store, but nothing in `core` would fail if `decodeUtf8` gained a fast path through a default `TextDecoder` (m-4).
Fix: add `["efbbbf61", [0xfeff, 97]]` to `cases`.

## Practice

### m-4 (Minor): the codec is two orders of magnitude slower than the built-ins

`encodeUtf8` (`ts/src/core/text.ts:106-116`) builds a `number[]` and calls `TextEncoder.encode` once per code point, and `decodeUtf8` (`ts/src/core/text.ts:118-148`) appends one code point at a time.
Run on Latin text with an astral character: 1,000,032 characters take 112 ms to encode (TextEncoder 0.7 ms) and 43 ms to decode (TextDecoder 1.1 ms); 4,000,062 characters 394 ms and 171 ms.
Failure scenario: plan 7b's `trees()` decodes every file of the project on each call, so a project the size of this repository's `lodge/` (1.6 MB on disk) spends tens of milliseconds per read in `decodeUtf8` alone.
Fix: a fast path that gives the same bytes and code points: in `encodeUtf8`, `text.isWellFormed() ? new TextEncoder().encode(text) : …` (a well-formed string holds no lone surrogate, so the escape case cannot arise); in `decodeUtf8`, try `new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(bytes)` and fall back to the loop on its `TypeError`, with `ignoreBOM: true` essential (m-3); in `core` the `catch` must begin `if (!(e instanceof TypeError)) throw e;`.
Not run: I did not time the fast path; rerun the 527,936-case comparison against it.

### m-5 (Minor): three parallel ternary chains keyed on one size

`ts/src/core/text.ts:122-143` derives the sequence length, the lead-byte mask, and the overlong minimum from three separate ternary chains on `first` and `size`.
A change to one table (say a new lead range) must be made in three places that do not read as one table.
Fix: one lookup, for example `const FORMS = [[0x80, 0x7f, 0], [0xc2, 0x1f, 0x80], [0xe0, 0x0f, 0x800], [0xf0, 0x07, 0x10000]]` chosen by `size`, or a small `leadSize(first)` with the masks and minima indexed by size.

### m-6 (Minor): the member upsert and the unknown-kind throw are untested

Run: with `doUpdateSet({ role })` at `ts/src/store/events.ts:51` changed to `doNothing()`, `bun test tests/store` gives 5 pass, 0 fail; the plan's "an unknown kind throws, so a later plan cannot forget its case" (`ts/src/store/events.ts:64`) has no test either, though I ran it (a `mystery` event makes `rebuild` throw `unknown event kind: mystery` and roll back).
Failure scenario: a second `member` event for one person (a later role change) leaves the first role in `members`, and a later plan's kind falling through a `default` that no longer throws goes unnoticed.
Fix: in `rebuild_derives_the_tables_from_raw_events`, add a second `member` event for `ada` with role `member` and expect that role; add a test that a raw event of kind `mystery` makes `rebuild` reject and leaves the tables as they were.

### m-7 (Minor): a branch inside a parametrised expectation duplicates a new test

`ts/tests/structure/imports.test.ts:84-98` now branches on `path.startsWith("src/store/")` inside `fs_outside_git_and_cli`, and its store row asserts exactly what the new `store_importing_node_builtin` (`ts/tests/structure/imports.test.ts:159-164`) asserts.
Fix: give the `test.each` rows their expected findings as a third column (`["src/store/a.ts", "node:fs", ["file-confinement: …", "store-imports: …"]]`), so the test holds no branch.

Checked and found as the plan says: no `catch` in `text.ts`, no regular expression or sort added in `core`, no comments stating an edit, every file under 300 lines (`text.ts` 148, `schema.ts` 92, `events.ts` 77, `database.test.ts` 110); `store-imports` matches probe 9 and, run on planted files, finds `bun:ffi`, `bun`, `bun:test`, `@noble/hashes`, `yaml`, `node:child_process`, and `node:net` from `src/store/`, and nothing for `kysely`, `bun:sqlite`, `#app`, and `#core`; `knip.json` drops `kysely` from `ignoreDependencies` and adds `src/store/events.ts` to `entry`, as d-tha8st's table says; `ts/tests/parity.json` needs no change, since Task 7a carries no Python test; `sh scripts/check-ts.sh` on f194667 passes, 973 tests.

## Design

### m-8 (Minor): text to bytes to text is the identity only for texts a decode gave

Bytes to text to bytes is exact (527,936 cases above), but a text whose escapes together spell valid UTF-8 does not come back: `"x\uDCC3\uDCA9y"` encodes to `78c3a979` and decodes to `"xéy"`, in TypeScript and in lodge 0.2's Python alike (run).
Task 7a needs nothing more, since parity with `surrogateescape` is what d-0q54zn asks; the risk lands in plan 7b's `publish` and plan 3's API, which take texts that no decode produced (an edit that joins two escapes, or a JSON body holding `\udcc3\udca9`), so the stored file reads back other than written, against s-q4s548.
Fix, for Task 7b's brief or plan 3: `publish` refuses a text with `decodeUtf8(encodeUtf8(text)) !== text`, beside its lone-surrogate refusal.

### m-9 (Minor): the plan's Files list omits the hash test that its `contentHash` change must edit

Task 7a's Files (plan line 377) does not list `ts/tests/core/fileformat.test.ts`, while the Global Constraints allow editing an existing test only where a task says so, and the required `contentHash` cannot pass that test's old assertion (ruling above).
Fix: the ledger line for Task 7a records the edit and that plan 1's "test that cannot hold" for `hash_covers_undecodable_bytes` now holds as Python asserts it; no decision is needed, since the plan and the code agree on `contentHash`.

The design otherwise holds: `store` reaches `core` and `app` only through `#core` and `#app`, `applyEvent` is the one function a write and `rebuild` share, a non-`project` event updates `heads` without inserting, so plan 3's account events of project `""` add no row (tested), and the schema, migration, and newer-schema refusal follow the plan's wording.

## Files

Read: `CLAUDE.md`; `lodge spec` (Purpose); the plan's Global Constraints, Exports, Calls made, Review Focus, Interfaces, Lanes, Task 7a, and Task 7b; `task-7a-brief.md` (against the plan's Task 7a); `task-7a-report.md`; `probes.md`, `probes/db.ts`, `probes/p3-tx.ts`; the whole diff `server-store..server-store-b` (`ts/src/core/text.ts`, `fileformat.ts`, `ts/src/store/*.ts`, `ts/package.json`, `ts/knip.json`, `ts/.dependency-cruiser.cjs`, every changed test); `ts/tests/structure/plant.ts`; `src/lodge/core/fileformat.py:93-96`, `tests/core/test_fileformat.py:216-219`; plan 1's `task-5a-report.md` and `task-5a-review.md` lines on the hash test (by grep); `lodge show d-wje1cn` and `d-0q54zn`.
Not read: the rest of `ts/src/core` and `ts/src/app`, `ts/tests/structure/calls.ts` and `guards.ts` (their rules ran in the gate), d-nf7wvx and d-tha8st (taken as the plan states them), and `task-7a-codex.log`.

## Verdict

0 Blocking, 2 Important, 9 Minor.

## Practice

In progress.

## Design

In progress.
