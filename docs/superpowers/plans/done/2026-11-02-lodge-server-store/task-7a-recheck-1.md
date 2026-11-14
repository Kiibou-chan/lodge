# Task 7a recheck 1

Scope: `git diff 4736a59..fc7dd28` against I-1, I-2, and the Minors Codex fixed or deferred.

## I-1: fixed

`ts/src/store/schema.ts:44-46` adds `events_no_replace`, a before-insert trigger raising `events are append-only` when the new `seq` already exists.
`ts/tests/store/database.test.ts:59-72` runs both `insert or replace` and `replace` and expects the rejection message and the original actor kept.
Run in a scratch worktree: with the trigger removed, `bun test tests/store` gives 7 pass, 2 fail (both REPLACE tests).
The existing tests that insert events without `seq` still pass, so the null `seq` case is not refused.

## I-2: fixed

`ts/tests/store/database.test.ts:128-143` (`rebuild_removes_stale_rows`) plants a `heads`, a `files`, and a `members` row for a project no event names and expects all three empty after `rebuild`.
Run in a scratch worktree, deleting each of `ts/src/store/events.ts:71`, `:72`, `:73` in turn: each gives 8 pass, 1 fail, the failure being `rebuild_removes_stale_rows`.
The added `unknown_event_rolls_back_rebuild` (`:144-170`) and the second member event in `rebuild_derives_the_tables_from_raw_events` are additions beyond the finding and are sound.

## Minors

- m-1 fixed (`ts/tests/core/fileformat.test.ts:217-220` decodes the raw bytes).
- m-3 fixed (`ts/tests/core/bytes.test.ts:5` holds `efbbbf61`).
- m-5 fixed (`ts/src/core/text.ts:118-119` and the uses at `:134`, `:141`); behaviour is unchanged and the 979-test run covers the codec cases.
- m-9 answered as a ledger note in `task-7a-fix-1-report.md`; the coordinator must record it.
- m-2 deferred; the reason is only half sound.
  A contention regression test does need a second process, but the review's fix (set `busy_timeout` first, refuse unless the `journal_mode` answer is `wal`) is two lines and needs no such test beyond a unit check of the refusal.
  Acceptable as parked, provided the ledger assigns it to Task 8 (two writers), where a connection stuck in rollback-journal mode first matters; the report does not say which task takes it.
- m-4 deferred; sound.
  Nothing in 7a reads large files, and the fast path needs the 527,936-case comparison and timing the review itself says it did not run.
  The report should name plan 7b's `trees()` as the taker.
- m-8 deferred; sound.
  Task 7a has no `publish` or API input, and the report names the refusal (`decodeUtf8(encodeUtf8(text)) !== text`) for 7b or plan 3.
- m-6 and m-7 are claimed fixed (`ts/tests/structure/imports.test.ts:84-93`); the replaced expectation is now explicit and equal in strength.

## Gate and hygiene

`sh scripts/check-ts.sh` at fc7dd28: exit 0, 979 pass, 0 fail.
The only docs file in the diff is the new `task-7a-fix-1-report.md`; no earlier brief, report, or review was edited.
The branch was not touched; the scratch worktree is removed.

## New problems

None found.
Minor only: the report does not name the taker task for m-2 and m-4 (see above).

0 Blocking, 0 Important
