# Task 7b review

Reviewer: `reviewer` agent, first review of commit 7809f42 on `server-store-b` (diff `4766854..7809f42`).
Scope: the plan's Task 7b, Global Constraints, "Interfaces for plans 3 and 4" with its events-table bullets, Calls made 2, 3, 10, 11, and 14, and Review Focus 2, 3, and 4.
Probes and mutations ran in a detached scratch worktree at 7809f42 (`.claude/worktrees/review-7b`), since removed.
`sh scripts/check-ts.sh` there: Biome, `tsc`, dependency-cruiser (no violations, 155 modules), knip, and `bun test` 1040 pass, 0 fail.

## Correctness

What holds, checked by reading and by running:

- The compare-and-set opens `publish`'s transaction with `update heads set rev = rev where project = ? and rev = ?` (`ts/src/store/sqlite-store.ts:88-95`); a stale base, `null`, `x`, `2.0`, and `-1` each answer `REJECTED` with no event (`stale_base_is_rejected_and_writes_nothing`), and a second publish on one base is rejected.
- `check_writes` is ported with both messages (`ts/src/store/sqlite-store.ts:59-69` against `src/lodge/gitstore/plumbing.py:19-25`); all eight outside paths are refused with no event.
- Surrogate paths (`\p{Cs}` with the `u` flag, so an astral pair passes), a changed decision text, and an attachment overwrite are refused before any write; an unchanged decision text is accepted.
- `create` opens with `insert … on conflict do nothing`, `addMember` with `update heads set rev = rev` (d-thvvzx); `members` sorts with `byCodePoint`; stamps come from `stampOf(clock.now())` and actors from `actorText`.
- `trees`, `gate`, `freshness`, and `commit` answer as the plan's fifth events-table bullet says.
- `rebuild_gives_the_same_tables` and `rebuild_keeps_every_event` pass; no code in the diff updates or deletes an event.
- `file_bytes_survive_exactly` round-trips U+FEFF first, CRLF, U+0000, an astral character, and U+DC80 as byte 0x80.

### C-1 · Important · a commit message holding an escaped byte is stored corrupted, permanently

Handle: `ts/src/store/sqlite-store.ts:81` puts `message` into each `file` event, and the plan's events table makes `message` a `text` column (plan "Interfaces for plans 3 and 4", first bullet; `ts/src/store/schema.ts:43`, Task 7a).
`Lodge.add` builds that message from the first record's title (`ts/src/app/writes.ts:224-229`), and a title may hold U+DC80 to U+DCFF, which `encodeUtf8` accepts for the file itself.
Scenario, run in the scratch worktree through `store.publish` with message `m`:

| `m` | stored `message` |
|---|---|
| `"plain"` | `"plain"` |
| `"lodge: add d-1 t\uDC80"` | `""` |
| `"t\uDC80 tail"` | `"t\u{30020}tail"` |
| `"﻿lead"` | `"lead"` |

The file's bytes survive, but the event's message is lost or garbled, and since events are append-only it can never be corrected.
Plan 3's API takes drafts as JSON, where `"\udc80"` is a legal escape, and plan 4's import carries lodge 0.2 records read with `surrogateescape` (`src/lodge/gitstore/trees.py:16`), so both routes reach it.
d-wje1cn's reasoning weighs the `text` corruption for file text only (probes 1 and 2); the message column was not considered.
Fix: this conflicts with the plan's schema, so it goes to a recorded decision (`lodge add`, scope `process`, work item the plan).
Recommended: make `message` a `blob` written through `encodeUtf8` (as `path` is guarded by refusal, `message` cannot be refused without breaking `add` for a title lodge 0.2 accepts), changing `MIGRATIONS[0]` while no database exists yet; the alternative is to refuse in `publish` a message matching `/\p{Cs}/u` or starting with U+FEFF, which makes such an `add` fail where lodge 0.2 commits.
A test: publish with message `"t\uDC80 tail"` and read the event's message back equal.

### C-2 · Important · `names_are_checked` does not guard the owner's name check in `create`

Handle: `ts/tests/store/projects.test.ts:32-43`, the cases `["storage", "Ada"]` and `["storage", "1ada"]`.
`setup()` has already created `storage`, so without the person check `create` throws `Conflict("a project named storage exists")`, which is a `LodgeError`, and the test passes.
Run: mutation M1, deleting `checkName(owner);` at `ts/src/store/projects.ts:34`, leaves all 44 store tests passing.
The person check on `addMember` is guarded (`add_member_needs_a_new_name`); the one on `create` is not, so a project could be created with an owner named `Ada` and no test would notice.
Fix: use a project name that does not exist (`other`) for the person cases, and assert each message with its pattern, as the plan asks ("`<name> is not a project name: …`", "`… is not a person's name: …`", with the pattern), rather than the class alone.

### C-3 · Minor · the refusals run per path, not in the plan's phases

Handle: `ts/src/store/sqlite-store.ts:58-86` runs all four refusals and the encoding for one path before the next path.
The plan's Task 7b says `publish` "first refuses … each path in `writes` that lodge 0.2's `check_writes` refuses …; then a path holding any surrogate …; then a path under `lodge/decisions/` …", and lodge 0.2 runs `check_writes` over every path first (`src/lodge/gitstore/branch.py:108`).
Run: with a published decision, `publish(base, {decision: text + "\n", "notes/x": "x"})` throws `… is a published decision, …`, where lodge 0.2's order gives `notes/x is outside lodge/, which is all the store writes`.
Nothing is written either way, so only the message differs.
Fix: one loop per phase (outside and attachment, surrogate, decision, encoding), or a `checkWrites(base, writes)` function mirroring `plumbing.py` called first.

### C-4 · Minor · the encoding refusal's message is not asserted

Handle: `ts/tests/store/sqlite-store-refusals.test.ts:26-40` asserts only `rejects.toThrow(LodgeError)`.
Run: mutation M5, replacing `` `${path}: ${error.message}` `` at `ts/src/store/sqlite-store.ts:84` with `"x"`, leaves every store test passing.
Fix: assert the message starts with `lodge/a: ` and names the surrogate as `encodeUtf8`'s `ValueError` does.

## Practice

What holds: `src/store` imports only `#app`, `#core`, `kysely` (a type), and its own modules; no `node:`, `fetch`, `Bun.`, or `require` (grep); dependency-cruiser reports no `store-imports` or confinement violation; every file is under 120 lines; `src/store/events.ts` left knip's `entry` and knip is green; the parity table needs no row (the two `"7b"` rows are plan 1's).

### P-1 · Minor · the head lookup and the write-first touch are written out three times

Handle: the `select rev from heads … NotFound` lookup at `ts/src/store/read-tree.ts:6-12` and again at `ts/src/store/projects.ts:51-56`; the `set rev = rev` touch at `ts/src/store/sqlite-store.ts:89-94` and `ts/src/store/projects.ts:72-77`.
d-thvvzx adds two more touches in Task 12a (`decline` and an approving `publish`), so the rule will live in four copies.
Fix: `headOf(tx, project)` and `touchHead(tx, project, rev?)` beside `readTree` in `read-tree.ts`, `members` calling `headOf`, and the transactions calling `touchHead` as their first statement.

### P-2 · Minor · `attachmentTexts` reads every file's bytes to keep the attachments

Handle: `ts/src/store/sqlite-store.ts:29-38` selects all of the project's `files` rows, records included, and filters in TypeScript.
Fix: filter in SQL with a range on `path` (`>= 'lodge/attachments/'` and `< 'lodge/attachments0'`), which keeps byte order and avoids `like`'s case folding.

### P-3 · Minor · `checkName`'s boolean flag

Handle: `ts/src/store/projects.ts:20` `checkName(name, project = false)`, called as `checkName(project, true)` at line 33.
Fix: two constants pairing the pattern with its noun (`PROJECT_NAME = { pattern, what: "a project name" }`) passed in, or two small functions.

### P-4 · Minor · an acceptance case inside a refusal test

Handle: `ts/tests/store/sqlite-store-refusals.test.ts:41-58` puts the astral character into `a_path_holding_a_surrogate_is_refused` and branches on it with `if`.
Fix: keep the two surrogates in the `test.each`, and assert the astral path's `PUBLISHED` after it in the same test without a branch.

## Design

### D-1 · Minor · `publish` trusts the caller's `base` for the decision and attachment refusals

Handle: `ts/src/store/sqlite-store.ts:68` and `:72-76` compare against `base.attachments` and `base.files`, and `:87` accepts any `^[0-9]+$` revision.
The compare-and-set checks only `base.rev`, so a base whose `rev` is current but whose maps are not the stored state passes both refusals.
Run: after publishing a decision and an attachment, `publish(tree({ rev: current.rev, files: new Map(), attachments: new Set() }), { decision: "rewritten", attachment: "second" })` answers `PUBLISHED`, and both are overwritten; `tree({ ...current, rev: "0002" })` at revision 2 also publishes.
lodge 0.2 trusts `base.attachments` the same way (`src/lodge/gitstore/branch.py:108`), and the plan states the assumption ("checking against it is checking against the state written onto"), and every caller in plans 2 and 4 takes `base` from `trees()`; so no current caller fails.
It matters because d-j28rp0 puts these refusals in the store precisely as the guard for callers that skip `app`'s check, and s-pncjp8 says decisions are never rewritten.
Fix, if wanted: inside the transaction after the compare-and-set, read the `files` rows for the written paths under `lodge/decisions/` and `lodge/attachments/` and refuse against them, and accept only `^(0|[1-9][0-9]*)$`; otherwise leave as the plan has it.

### D-2 · Minor · d-thvvzx's write-first order in `create` and `addMember` is enforced by no test

Handle: `ts/src/store/projects.ts:36-40` and `:72-77`.
Run: mutation M6, adding a `select … from members` before the `update heads` in `addMember`, leaves all 44 store tests passing; Task 8's tests (plan lines 474-476) exercise only `publish`.
With a read first, a second connection's write between that read and this write fails the write with `database is locked` despite `busy_timeout` (probe 4), a raw SQLite error rather than `Conflict` or `NotFound`.
Fix: a test that wraps `database.db` with `withPlugin` recording each query node's kind, and asserts that the first statement of `create`, `addMember`, and `publish` is an insert or update on `heads`; Task 8 or Task 12a, which adds two more such transactions, is the natural place.

## Files read

Read: `CLAUDE.md`; `lodge spec` (Purpose); `lodge show` d-j28rp0, d-thvvzx, d-wje1cn; the plan's header, Global Constraints, Calls made, Review Focus, Interfaces, Tasks 7a, 7b, and 8's test list; `task-7b-brief.md` (task section diffed against the plan: identical); `task-7b-report.md`; `ts/src/store/{sqlite-store,projects,read-tree,index,events}.ts`; `ts/knip.json` diff; `ts/tests/store/{support,sqlite-store,sqlite-store-refusals,projects,rebuild}.test.ts`; `ts/src/app/writes.ts:120-235`; `src/lodge/gitstore/plumbing.py:1-40`, `branch.py:100-150`, `src/lodge/app/ports.py:55-90`.
Not read: `ts/src/store/schema.ts` beyond its `message` lines, `database.test.ts` (Task 7a, reviewed there), the rest of `ts/src/app` and `ts/src/core`, `probes.md` beyond grep hits, the untracked Codex log files.

Verdict: 0 Blocking, 2 Important (C-1, C-2), 8 Minor (C-3, C-4, P-1, P-2, P-3, P-4, D-1, D-2).
