# Task 12c review

Commit 3134ce5 on `server-store`, reviewed in the scratch worktree `/var/tmp/lodge-review-12c` (removed after).
Gate: `sh scripts/check-ts.sh` exits 0 there (1285 pass, 2 todo, 0 fail; biome, tsc, depcruise, knip clean).
Mutations: 26 on `ts/src/app/threads.ts` and `ts/src/app/held.ts`, each run against `bun test tests/app tests/store` and reverted; three were equivalent (M18, M21) or constant-for-constant (where `"chat"`, which killed with `"mail"`).
Probes: a relayed close approved over MemoryStore, and a relayed ask, a relayed close, and their approvals over SqliteStore, all gave the expected answers (thread closed, last message by the person with the held where and when).

## Correctness

Held and approved as specified, verified by reading and by mutation:
- The hold sits after the `where` refusal, the ref resolution, the closed-thread refusal, the message build, and the check (`ts/src/app/threads.ts:147`, after the check at `:140` and beside the Task 11 `Forbidden` at `:122`); moving the hold or the refusals is killed by the three tests the report lists (reported; not re-run for the first two).
- An agent writing under a role is not held (M20 killed), a person's own message is not held (M19 killed), another person's is `Forbidden`.
- The approval publishes with `approves` = `seq` (M13 killed), a `REJECTED` answer rereads and a settled hold throws `NotFound` (M8, M23 killed), a closed thread leaves the hold open (test), a wrong approver is `Forbidden` before anything is read of the thread (`held.ts:12`).
- Waiting functions are untouched; a held message changes no thread's waiting.
- Task 12b's parked items are untouched: `held()` at `held.ts:9` and the add path (`writes.ts` is not in the diff).

### Important

**I-1. A relayed close is not tested at all** (`ts/src/app/threads.ts:152`, `ts/src/app/held.ts:29`-`:30`).
Five mutations survive the whole app and store suites: `operation: raises !== null ? "ask" : close ? "close" : "reply"` to `"ask" : "reply"` (M1) or to always `"reply"` (M2), `text: close && !msg.text ? null : msg.text` to `msg.text` (M3), `close: initial.operation === "close"` to `close: false` (M14), and `initial.text ?? ""` to `?? "x"` (M25).
Failure scenario: M1 or M14 lets an agent relay "ada closes this thread", ada approves, and the approved message is appended while the thread stays open and keeps waiting; no test fails.
My probe shows the unmutated code is right (held `operation: "close"`, `text: null`; approval leaves `state` closed with an empty message by ada), so this is a missing test, not a bug.
Fix: add `a_relayed_close_is_held_and_closes_the_thread_at_approval` in `tests/app/held-messages-approve.test.ts` (relay `close` by `ada` with where; `held()` lists `operation: "close"`; after `ada.approve` the thread's `state` is `closed`); a store twin in `tests/store/held-messages.test.ts` is optional.

**I-2. The held answer's `ids` and `about` are asserted nowhere** (`ts/src/app/threads.ts:158`-`:164`).
`ids: [thread.id]` to `ids: []` (M5) and `about: thread.about` to `null` (M6) both survive; the plan's Interfaces name `ids` as the thread's ID for a reply or close and the provisional ID for an ask, and plan 3 builds its HTTP answer from them.
`a_relayed_question_mints_its_thread_at_approval` only asserts `approved.written.ids` differs from `result.ids`, which an empty array also satisfies.
Fix: assert `result.ids` equals `[id]` for the relayed reply (`held-messages.test.ts`), that the held ask's `ids` has one `q-` ID, and that `about` is `s-aaaaaa`.

## Practice

### Minor

**M-1. The top-of-loop settle check is redundant** (`ts/src/app/threads.ts:91`-`:92`).
Removing it (M7) survives: `authorised` has just checked the hold, and a hold settling afterwards makes `publish` answer `REJECTED`, which the branch at `:176`-`:178` already turns into `NotFound`; it costs one `store.held()` read per attempt, and the only difference is that a hold settled in the window answers `NotFound` before a closed-thread or check refusal.
The same `held().some(seq)` test is written twice (`:91`, `:176`).
Fix: drop the first, or extract `isOpen(w, seq)` and keep one use, with a test for whichever behaviour is wanted.

**M-2. The `refresh` branch in `approve` for a message is unreachable** (`ts/src/app/held.ts:37`).
A hold's kind never changes, so `hold ${seq} is not an add` cannot fire; M26 (changing its text) survives.
Fix: narrow without a throw, for example have `authorised` take the kind it expects, or keep the throw and accept it as a type guard with a comment-free `satisfies`; at least do not leave a message nobody can read.

**M-3. `writeMessage` grew to about 140 lines with a seventh positional parameter** (`ts/src/app/threads.ts:81`-`:196`).
`approves` defaults to `null`, so d-d96y91 holds, but the held branch (`:147`-`:165`) is a block that could be `holdMessage(w, ...)`, which also keeps the file well under 300 lines (234 now).

**M-4. Test shape** (`tests/app/held-messages.test.ts:32`-`:45`, `held-messages-support.ts:8`).
The two waiting tests are one loop with ternary names and a boolean `own` flag on `setup`; `result.held as number` is cast eleven times.
Fix: two plain tests, and have `relay()` return `held` as a number.

**M-5. Where is `"chat"` in every test**, so a held `where` of the constant `"chat"` is indistinguishable from the real one (M10, M17 survive as `"chat"`, die as `"mail"`); use a second value in the approval test.

## Design

No Blocking or Important.
`held.ts → threads.ts` adds no cycle (depcruise green); the hold stores text, place, and minute rather than the file, so approval rereads the thread and checks it against the state it lands on, which is d-znagqe's rule for adds applied to messages.
A held ask mints its ID again at approval, as the plan says.

### Minor

**M-6. The ask's `ref` is held as `thread.about`, the resolved ID** (`threads.ts:153`), so a ref given as a name resolves at hold time and again at approval; M24 (holding the raw ref) survives because the test uses the ID.
Harmless today; a test with a title-style ref would pin it.

**M-7. Not exercised.** An approval whose check fails (`CHECK_FAILED`, hold stays open) has no message test; the plan lists it.
I could not construct a state where a check passes at hold and fails at approval without a new fixture, so I did not run it.

## Files

Read: the brief, report, plan Task 12c and Calls made, d-2v8vtk, d-znagqe, d-thvvzx, `git show 3134ce5`, `ts/src/app/{threads,held}.ts`, `ts/src/app/ports.ts` (held types), the five new or changed test files.
Not read: `ts/src/store/*` internals, `memory` fake store, plan 1 and 3 documents beyond the cited lines, the Python tree.

Verdict: 0 Blocking, 2 Important, 7 Minor
