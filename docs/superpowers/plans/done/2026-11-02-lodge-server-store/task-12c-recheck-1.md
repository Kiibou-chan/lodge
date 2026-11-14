# Task 12c, recheck 1

Fix commit b43f63b against `task-12c-review.md`, in the scratch worktree `/var/tmp/lodge-review-12cb` (removed after).
Gate: `sh scripts/check-ts.sh` exits 0 there (1286 pass, 2 todo, 0 fail; biome, tsc, depcruise, knip clean).
Files: `threads.ts` 242 lines, `held.ts` 62, the held-message tests 95, 77, and 28; none over 300.
No em-dashes in the changed source, tests, or report.

## Findings

- I-1 answered: `ts/tests/app/held-messages-approve.test.ts:77` adds `a_relayed_close_is_held_and_closes_the_thread_at_approval` (held `operation: "close"`, `text: null`, thread open before approval, closed after, empty message by ada, waiting cleared).
- I-2 answered: `held-messages.test.ts:8`-`:10` asserts `ids: [id]` and `about: "s-aaaaaa"` for a reply; `held-messages-approve.test.ts:27`-`:28` asserts one `q-` ID and `about` for an ask; the close test asserts both.
- M-1 answered: the top-of-loop read is gone (`threads.ts:117`); the `REJECTED` branch is the one remaining check; `a_hold_settled_on_the_last_attempt_is_not_found` counts four `held()` reads (`held-messages-approve.test.ts:81`), so a restored extra read fails it.
- M-2 answered: `authorised` takes the expected kind (`held.ts:12`-`:20`) and `refresh` is `authorised(w, seq, "add")` (`held.ts:42`); the unreachable throw is gone.
- M-3 answered: `holdMessage` at `threads.ts:82`-`:108`; `writeMessage` calls it at `:174`.
- M-4 answered: two plain waiting tests (`held-messages.test.ts:29`, `:41`); `relay()` returns `held` as a number (`held-messages-support.ts:22`-`:25`); the `as number` casts are gone.
- M-5 answered: the approval test relays with `where` `mail` and asserts `mail` (`held-messages-approve.test.ts:8`, `:17`).
- M-6 declared unsupported, claim holds: `core/search.ts:31`-`:42` `resolve` accepts a record ID or an exact record code, never a title, and `resolveRef` in `threads.ts:126` goes through it.
- M-6 residue (Minor): a code is a non-ID ref that does resolve, and the fixture entry has `code: "ITEM-1"` (`tests/app/support.ts:22`), so a test asking with `ITEM-1` and asserting the held `ref` is `s-aaaaaa` would pin the resolve-at-hold behaviour (M24) after all.
- M-7 declared uncovered, claim accepted: the report's reasoning (approving a message adds no dependency a check could fail on) is plausible and no fixture exists; the gap stays parked.

## Mutations re-run

Each applied alone on `ts/src/app/threads.ts` or `held.ts`, run against `bun test tests/app tests/store`, reverted.

| Mutation | Result |
| --- | --- |
| M1 relayed close op to `"reply"` unless ask | killed (1 fail) |
| M2 operation always `"reply"` | killed (1 fail) |
| M3 close text kept as `msg.text` | killed (1 fail) |
| M14 `close: false` at approval | killed (1 fail) |
| M25 `?? "x"` | killed (1 fail) |
| M5 `ids: []` | killed (3 fail) |
| M6 `about: null` | killed (3 fail) |

## New problems

None Blocking or Important.
The `authorised` generic with a defaulted `K` is slightly heavy for one caller passing a kind, but it type-checks, is covered, and is not worth a round.

Verdict: 0 Blocking, 0 Important, 1 Minor
