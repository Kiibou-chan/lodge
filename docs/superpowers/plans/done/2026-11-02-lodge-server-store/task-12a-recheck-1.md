# Task 12a recheck 1

Rechecked `git diff 18b0a78 b709aa8` in a scratch worktree at b709aa8 (removed after).
Gate `sh scripts/check-ts.sh` there: exit 0, 1253 pass, 2 todo, 0 fail.
Mutations applied one at a time to `src`, running `bun test tests/app tests/store`, each reverted.

## Findings

- I-1: answered, `ts/tests/store/held.test.ts:85-87` asserts `toBeInstanceOf(NotFound)` and the message. M3 (typed throw replaced by a plain `Error`) now fails `a_settled_hold_cannot_be_declined`.
- I-2: answered, the `deleteFrom("held")` before `rebuild` is gone (`held.test.ts:111-116`). M6 (remove `rebuild`'s own delete, `ts/src/store/events.ts:98`) now fails `holds_rebuild`.
- I-3: answered, `holds_belong_to_their_project` (`held.test.ts:145-160`) uses two projects and checks listing, foreign `decline` (`NotFound`), foreign approving `publish` (`REJECTED`), and no new events.
  M8 (listing filter removed) fails it.
  The two lookups now share `openHold` (`ts/src/store/read-tree.ts:55`), so M9 and M10 are one edit there, which fails it.
  Applied separately to `decline` only and to `publish` only, each also fails it.
- I-4: answered, `write-first.test.ts:17` adds `decline` and `approve` to the `test.each`, and `missing_project: hold|decline` (`:54-62`) checks class, message, and no events.
  M15 (decline's opening `touchHead` removed) fails `transaction_writes_heads_first: decline` and `missing_project: decline`.
- P-M1: answered, `openHold` in `read-tree.ts:55` is used at `sqlite-store.ts:53` and `:134`.
- P-M2: answered, `ts/tests/app/fakes.ts:59` uses `stampOf(START)`.
- P-M3: answered, `fakes.ts:37` and `:67` record `declined`, asserted at `fakes-held.test.ts:37`.

## Other checks

- Every file in the diff is under 300 lines (largest `database.test.ts`, 204).
- No em-dashes in the diff; British English holds.
- No dependency change; production change is only the extraction of `openHold`, with the same filters as before.
- No new Blocking or Important problem found.

Verdict: 0 Blocking, 0 Important, 0 Minor
